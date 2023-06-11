import requests
import sys

sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
from copy import deepcopy
from blueprints.live_editor.models import bitable_works

indicator_template=lambda id,name,code,x,y: f'''<mxCell id="{id}" value="{name}&lt;br /&gt;{code if code else ''}" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#FFFFCC;gradientColor=none;fontColor=#000000;fontSize=20;" vertex="1" parent="base1"><mxGeometry x="{x}" y="{y}" width="100" height="100" as="geometry"/></mxCell>'''
product_template=lambda id,name,x,y:f'<mxCell id="{id}" value="{name}" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#0362A1;gradientColor=none;fontColor=#FFFFFF;fontSize=15;" vertex="1" parent="base1"><mxGeometry x="{x}" y="{y}" width="100" height="100" as="geometry"/></mxCell>'
demand_template=lambda id,name,x,y:f'<mxCell id="{id}" value="{name}" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#CC0000;gradientColor=none;fontColor=#FFFFFF;fontSize=20;" vertex="1" parent="base1"><mxGeometry x="{x}" y="{y}" width="100" height="100" as="geometry"/></mxCell>'
technique_template=lambda id,name,x,y:f'<mxCell id="{id}" value="{name}" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#999999;gradientColor=none;fontColor=#FFFFFF;fontSize=20;" vertex="1" parent="base1"><mxGeometry x="{x}" y="{y}" width="100" height="100" as="geometry"/></mxCell>'
company_template=lambda id,name,code,x,y:f'''<mxCell id="{id}" value="{name}&lt;br /&gt;{code if code else ''}" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#ffffff;strokeColor=#00AB0B;strokeWidth=6;fontSize=20;" vertex="1" parent="base1"><mxGeometry x="{x}" y="{y}" width="100" height="100" as="geometry"/></mxCell>'''

compose_template=lambda id,target,source:f'<mxCell id="{id}" value="原材料" style="endArrow=classic;html=1;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
supply_template=lambda id,target,source:f'<mxCell id="{id}" value="供应" style="endArrow=classic;html=1;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
produce_template=lambda id,target,source:f'<mxCell id="{id}" value="生产" style="endArrow=classic;html=1;labelBackgroundColor=#CCFFCC;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
peer_template=lambda id,target,source:f'<mxCell id="{id}" value="同位" style="endArrow=none;html=1;endFill=0;shape=link;width=4;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
measure_template=lambda id,target,source:f'<mxCell id="l{id}" value="反映" style="endArrow=classic;html=1;strokeColor=#FF66B3;strokeWidth=2;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
parent_template=lambda id,target,source:f'<mxCell id="{id}" value="父节点" style="endArrow=classic;html=1;strokeColor=#9933FF;strokeWidth=2;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
carry_template=lambda id,target,source:f'<mxCell id="{id}" value="储运" style="endArrow=classic;html=1;strokeColor=#FFB366;strokeWidth=2;fontSize=15;" diagramCategory="general" diagramName="DirectionalConnector" edge="1" source="{source}" target="{target}" parent="base1"><mxGeometry x="0.0242" y="4" width="50" height="50" relative="1" as="geometry"></mxGeometry></mxCell>'
def build_body(raw):
    body=''
    gived_position=0
    for node in raw['nodes']:
        if not node.get('x') or not node.get('y'):
                #print(f"{gived_position%10},{gived_position//10}")
                #print(gived_position)
                node['x']=gived_position%10*150
                node['y']=gived_position//10*150
                gived_position+=1
        
        if node['category']=='产品':
            body+=product_template(node['bitapp_id'],node['name'],node.get('x'),node.get('y'))
        elif node['category']=='工艺':
            body+=technique_template(node['bitapp_id'],node['name'],node.get('x'),node.get('y'))
        elif node['category']=='需求':
            body+=demand_template(node['bitapp_id'],node['name'],node.get('x'),node.get('y'))
        elif node['category']=='指标':
            body+=indicator_template(node['bitapp_id'],node['name'],node.get('code'),node.get('x'),node.get('y'))
        elif node['category']=='企业':
            body+=company_template(node['bitapp_id'],node['name'],node.get('code'),node.get('x'),node.get('y'))
    print(f"gived_position:{gived_position}")
    for link in raw['links']:
        if link['category']=='原材料':
            body+=compose_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='生产':
            body+=produce_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='供应':
            body+=supply_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='反映':
            body+=measure_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='父节点':
            body+=parent_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='同位':
            body+=peer_template(link['bitapp_id'],source=link['source'],target=link['target'])
        elif link['category']=='储运':
            body+=carry_template(link['bitapp_id'],source=link['source'],target=link['target'])        
    return body




def filter_region(raw1,region_name):
    '''子图、区域筛选：两端都在区域内则为该区域的边，挂靠节点在区域内则该节点和measure边在区域内，'''
    '''需要把raw nodes转成字典'''
    from copy import deepcopy
    raw=deepcopy(raw1)
    node_dic={item['bitapp_id']:item for item in raw['nodes']}
    #link_dic={item['bitapp_id']:item for item in raw['links']}
    #print(node_dic)
    nodes=[]
    links=[]
    for link in raw['links']:
        if node_dic[link['source']].get('region')==node_dic[link['target']].get('region')==region_name:
                #print(node_dic[link['source']]['name'])
                #print(node_dic[link['source']].get('region'))
                links.append(link)
        elif node_dic[link['target']].get('region')==region_name and link['category']=='反映':
                links.append(link)

    
    for link in links:
        source=node_dic[link['source']]
        target=node_dic[link['target']]
        if not source in nodes:
              nodes.append(source)
              #print(source['name'])
        if not target in nodes:
              nodes.append(target)
              #print(target['name'])
    
    result={'nodes':nodes,'links':links}
    return result
def filter_category(raw1,category):
    '''公司/指标筛选：两端都不是公司/指标'''
    '''需要把raw nodes转成字典'''
    from copy import deepcopy
    raw=deepcopy(raw1)
    print(type(raw))
    node_dic={item['bitapp_id']:item for item in raw['nodes']}
    #link_dic={item['bitapp_id']:item for item in raw['links']}
    #print(node_dic)
    nodes=[]
    links=[]
    for link in raw['links']:
        if node_dic.get(link['source']) and node_dic.get(link['target']):
            if node_dic[link['source']].get('category')!=category and node_dic[link['target']].get('category')!=category:
                    #print(node_dic[link['source']]['name'])
                    #print(node_dic[link['source']].get('region'))
                    links.append(link)
        

    
    for link in links:
        source=node_dic[link['source']]
        target=node_dic[link['target']]
        if not source in nodes:
              nodes.append(source)
              #print(source['name'])
        if not target in nodes:
              nodes.append(target)
              #print(target['name'])
    
    result={'nodes':nodes,'links':links}
    return result

def string_work(raw):
    #raw=bitable_works(bitapp_id,subgraph_name=subgraph_name)
    
    if raw:
        head='<mxGraphModel><root><mxCell id="base"/><mxCell id="base1" parent="base"/>'
        tail='</root></mxGraphModel>'
        body=build_body(raw)
        result=head+body+tail
        return result
    else: return False