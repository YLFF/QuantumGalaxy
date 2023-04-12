import requests
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
from QGI.neoapi import Neo4j
from config import args
def get_neo():
    if args.debug:
        #neo_uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
        #neo_user = "neo4j"
        #neo_password = "QuantumGalaxy"
        neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
        neo_user = "QG_Editor"
        neo_password = "editor"
    else:
        neo_uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
        neo_user = "neo4j"
        neo_password = "QuantumGalaxy"
        #neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
        #neo_user = "QG_Editor"
        #neo_password = "editor"


    neo=Neo4j(neo_uri,neo_user,neo_password)
    return neo
def write_node_type(nodetype):
    for k,v in {'Product':'产品','Technique':'工艺','Demand':'需求','Indicator':'指标','Company':'企业','Scenario':'情景'}.items():
        if k in nodetype:
            r=v
        
    try:       
        return r
    except:
        return 'unknown'
def write_edge_type(edgetype):
    for k,v in {'compose':'原材料','parent':'父节点','carry':'储运','measure':'反映','produce':'生产','peer':'同位','supply':'供应','imagine':'想象'}.items():
        if k in edgetype:
            r=v
        
    try:
        return r
    except:
        return 'unknown'
def node_process(node):
    dic={}
    dic['neoid']=node.id
    dic['category']=list(node.labels)
    dic['category']=write_node_type(dic['category'])
    prop=dict(node.items())
    dic['name']=prop.pop('name')
    if prop.get('code',None):
        dic['code']=prop['code']
    #dic['others']=prop
    dic['more_info']={}
    if prop.get('datadate',None):
        dic['more_info']['datadate']=str(prop['datadate'])
    if prop.get('chgrate',None):
        dic['more_info']['chgrate']=prop['chgrate']    
    if prop.get('value',None):
        dic['more_info']['value']=prop['value']
    if prop.get('market_value',None):
        dic['more_info']['market_value']=prop['market_value']
    
    if prop.get('chgrate1d',None):
        dic['more_info']['chgrate1d']=prop['chgrate1d']
    if prop.get('stdchg1m',None):
        dic['more_info']['stdchg1m']=prop['stdchg1m']
    if prop.get('stdchg3m',None):
        dic['more_info']['stdchg3m']=prop['stdchg3m']


    #关于配图。图片索引为多维表格的token加recordid（默认为节点表），每次联调后需要下载多为表格中图片到固定位置，并把token和id存入neo。还需要做针对产品的下载图片接口
    if prop.get('file_token',None):
        dic['more_info']['file_token']=prop['file_token']
    if prop.get('record_id',None):
        dic['more_info']['record_id']=prop['record_id']
    
    ###dic中可能存在无法json化的数据 如Date类型###
    return dic

        
def edge_process(edge):
    dic={}
    dic['neoid']=edge.id
    dic['category']=edge.type
    dic['category']=write_edge_type(dic['category'])
    dic['source']=edge.start_node.id
    dic['target']=edge.end_node.id
    prop=dict(edge.items())
    
    #dic['others']=prop
    return dic
def get_lenth(names,neo):
    cypher="match p=shortestPath((n1)-[*..6]-(n2)) where n1.name='%s' and n2.name='%s' return length(p) as l"%(names[0],names[1])
    r=neo.simple_query(cypher)
    if r:
        lenth=r[0].get('l')
    else:
        lenth=None
    return lenth
def build_filter_cypher(item='chgrate1d',threshold=0.08):
    cypher={'node_cypher':'match (n)-[r]->(p:Product) where abs(n.%s)>%s return n'%(item,threshold),
            'link_cypher':'match (n)-[r]->(p:Product) where abs(n.%s)>%s return r'%(item,threshold)}
    return cypher
def day_market_cypher():

    cypher={'node_cypher':'match (n)-[r]->(p:Product) where abs(n.chgrate1d)>0.08 return n',
            'link_cypher':'match (n)-[r]->(p:Product) where abs(n.chgrate1d)>0.08 return r'}
    return cypher
def season_market_cypher():
    return {'node_cypher':'match (n)-[r]->(p:Product) where abs(n.stdchg3m)>1 return n',
            'link_cypher':'match (n)-[r]->(p:Product) where abs(n.stdchg3m)>1 return r'}
def build_neo_data(name=None,model='exact',cypher=None,tiers=1):
    '''model=[exact,vague,code,cypher]'''
    tiers=int(tiers)
    print("tiers='%s'"%tiers)
    neo=get_neo()
    print('start query in model: %s'%model)
    '''从名字获取星图中两步以内相关的节点和边，返回组装的json'''
    if model=='cypher':
        node_cypher=cypher['node_cypher']
        link_cypher=cypher['link_cypher']
    elif model=='exact':
        '''改成只找一层'''
        if tiers==1:
            node_cypher='match (n)-[*0..1]-(n1) where n.name="%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.name="%s" return r '%(name)
        else:
            node_cypher='match (n)-[*0..2]-(n1) where n.name="%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.name="%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.name="%s" return r'%(name,name)
        
    elif model=='vague':
        if tiers==1:
            print('1')
            node_cypher='match (n)-[*0..1]-(n1) where n.name contains "%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.name contains "%s" return r '%(name)
        else:
            node_cypher='match (n)-[*0..2]-(n1) where n.name contains "%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.name contains "%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.name contains "%s" return r'%(name,name)
    elif model=='code':
        if tiers==1:
            node_cypher='match (n)-[*0..1]-(n1) where n.code = "%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.code= "%s" return r '%(name)
        else:
            node_cypher='match (n)-[*0..2]-(n1) where n.code = "%s" return distinct n1'%name
            link_cypher='match (n)-[r]-(n1) where n.code= "%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.code= "%s" return r'%(name,name)
    elif model=='path':
        lenth=get_lenth(names=name,neo=neo)
        if lenth:
            print("path lenth from '%s' and '%s' is :%s"%(name[0],name[1],lenth))
            node_cypher="match p=(n1)-[*0..%s]-(n2) where n1.name='%s' and n2.name='%s' \
                with nodes(p) as ns\
                unwind ns as n\
                return distinct n"%(lenth+1,name[0],name[1])
            link_cypher="match p=(n1)-[*0..%s]-(n2) where n1.name='%s' and n2.name='%s'\
                with relationships(p) as rs\
                unwind rs as r\
                return distinct r"%(lenth+1,name[0],name[1])
        else:
            return {'nodes':[],'links':[]}
    print(node_cypher)
    nodes=neo.simple_query(node_cypher)
    links=neo.simple_query(link_cypher)
    nodesdata=[]
    print(len(nodes))
    for record in nodes:
        node=record[0]
        #print(node)
        nodesdata.append(node_process(node))
    linksdata=[]
    for record in links:
        link=record[0]
        linksdata.append(edge_process(link))
    neo.close()
    return {'nodes':nodesdata,'links':linksdata}
    
def user_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        r"E:\wangzhilin\QuantumGalaxy\server_8383_prod\logs\user.log",
        'a',
        encoding='utf-8')
    fh.setLevel(logging.INFO)
    #ch = logging.StreamHandler()
    #ch.setLevel(chlevel)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    #ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

def bitable_name(app_token):
    r=requests.get(r'http://82.156.248.152:81/bitapp/?app_token=%s'%app_token).json()
    if r['code']==0:
        return r['name']
    else:
        return None
def bitable_check(app_token):
    try:
        res=requests.get(r'http://172.21.0.14:81/bitapp/tables?app_token=%s'%app_token)
        tables=res.json()
        if tables['code']==0:
            #print(tables)
            tables=tables['data']
            node_table,link_table,indi_table=None,None,None

            for table in tables:
                if table['name']=='节点表':
                    node_table=table['table_id']
                if table['name']=='关系表':
                    link_table=table['table_id']
                if table['name']=='监测指标表':
                    indi_table=table['table_id']
            if node_table and link_table and indi_table:
                print('good table')
                return True,[node_table,link_table,indi_table]
            else:
                msg='not all tables found, node,link,indicator :%s'%[node_table,link_table,indi_table]
                return False,msg
        else:
            print(tables)
            return False,tables
    except Exception as e:
        return False,e
def get_main_info(field):
    '''从某双向选择的field中获取textarr项，去除其他'''
    '''双选字段信息为list但似乎只有1个元素，处理方式存疑'''
    #return [one['text_arr'] for one in field]
    return field[0]['text_arr'] if field else None

def post_process(raw):
    '''raw:{nodes:...,links:...,indicators:,,,'''
    nodes,links,indicators=raw['nodes'],raw['links'],raw['indicators']
    res_nodes=[]
    try:
        for n in nodes:
            f=n['fields']
            more_info={}
            
            external_backbone=get_main_info(f.get('所属外部骨干'))
            if external_backbone:more_info['external_backbone']=external_backbone
            
            res_node={'bitapp_id':n['record_id'],'name':f.get('节点名称'),'category':f.get('节点类型'),'more_info':more_info}
            code=f.get('公司代码')
            if code:res_node['code']=code
            x,y=f.get('画布位置X'),f.get('画布位置Y')
            if x and y:
                res_node['x']=round(float(x),2)
                res_node['y']=round(float(y),2)
            res_nodes.append(res_node)
    except Exception as e:
        return {'code':-3,'msg':'had problem when processing nodes, type:"%s"exception:%s'%(e.__class__.__name__,str(e))}
    res_links=[]
    try:
        for l in links:
            f=l['fields']
            res_link={'bitapp_id':l['record_id'],'source':f['主体'][0]['record_ids'][0],'target':f['客体'][0]['record_ids'][0],'category':get_main_info(f['关系'])[0]}
            res_links.append(res_link)
    except Exception as e:
        return {'code':-3,'msg':'had problem when processing edges, type:"%s"exception:%s'%(e.__class__.__name__,str(e))}
    try:
        for i in indicators:
            f=i['fields']
            res_link={'bitapp_id':i['record_id'],'source':i['record_id'],'target':f['挂钩节点'][0]['record_ids'][0],'category':"反映"}
            #res_links.append(res_link)
            #"指标代码","挂钩节点","指标性质","单位","指标定义","影响方向","画布位置X","画布位置Y","世界线跟踪表-主要相关指标"
            more_info={}
            type=f.get('指标性质')
            if type:more_info['type']=type
            
            res_node={'bitapp_id':i['record_id'],'name':f.get('指标名'),'category':'指标','more_info':more_info}
            code=f.get('指标代码')
            if code:res_node['code']=code
            x,y=f.get('画布位置X'),f.get('画布位置Y')
            if x and y:
                res_node['x']=round(float(x),2)
                res_node['y']=round(float(y),2)
            res_links.append(res_link)
            res_nodes.append(res_node)
    except Exception as e:
        return {'code':-3,'msg':'had problem when processing indicators, type:"%s"exception:%s'%(e.__class__.__name__,str(e))}
    return{'code':0,'nodes':res_nodes,'links':res_links}

    
def bitable_works(bitapp_token,subgraph_name=None):
    '''查多维表格的完整性（节点表 关系表 监测指标表'''
    res,data=bitable_check(bitapp_token)
    if not res:
        return {'code':-1,'msg':'查多维表格完整性失败，请确认包含节点表/关系表/监测指标表，并且给予星图编辑器可读权限    '+str(data)}
    else:
        #查节点表内容
        node_table,link_table,indi_table=data
        nodes,links,indicators=None,None,None
        params={'app_token':bitapp_token,'table_id':node_table,'graph_name':subgraph_name,'fields':'["节点名称","节点类型","公司代码","画布位置X","画布位置Y","参与子图","所属外部骨干"]'}
        r=base_fetch_func('http://172.21.0.14:81/bitapp/record',headers=None,params=params,method='get')
        ''' {
        "fields": {
        "公司代码": "600905.SH", 
        "参与子图": [
          {
            "record_ids": [
              "recFANk4QN", 
              "rec7txIH74"
            ], 
            "table_id": "tblXDUFR2NRoGLTC", 
            "text": "某局部图1,粗骨干图", 
            "text_arr": [
              "某局部图1", 
              "粗骨干图"
            ], 
            "type": "text"
          }
        ], 
        "节点名称": "三峡能源", 
        "节点类型": "企业"
      }, 
      "id": "rec9KgK3RV", 
      "record_id": "rec9KgK3RV"
    }, '''
        if r['code']==0:
            nodes=r['data']
        params={'app_token':bitapp_token,'table_id':link_table,'graph_name':subgraph_name,'fields':'["主体","关系","客体","参与子图"]'}
        r=base_fetch_func('http://172.21.0.14:81/bitapp/record',headers=None,params=params,method='get')
        '''"links": [
    {
      "fields": {
        "主体": [
          {
            "record_ids": [
              "rec2Af8KSz"
            ], 
            "table_id": "tblPlTiBMOFD7suF", 
            "text": "绝缘材料", 
            "text_arr": [
              "绝缘材料"
            ], 
            "type": "text"
          }
        ], 
        "关系": [
          {
            "record_ids": [
              "recazF7Tvz"
            ], 
            "table_id": "tblXBqHmlnY21CWH", 
            "text": "原材料", 
            "text_arr": [
              "原材料"
            ], 
            "type": "text"
          }
        ], 
        "参与子图": [
          {
            "record_ids": [
              "recFANk4QN", 
              "rec7txIH74"
            ], 
            "table_id": "tblXDUFR2NRoGLTC", 
            "text": "某局部图1,粗骨干图", 
            "text_arr": [
              "某局部图1", 
              "粗骨干图"
            ], 
            "type": "text"
          }
        ], 
        "客体": [
          {
            "record_ids": [
              "recoBIz2VC"
            ], 
            "table_id": "tblPlTiBMOFD7suF", 
            "text": "海洋线缆", 
            "text_arr": [
              "海洋线缆"
            ], 
            "type": "text"
          }
        ]
      }, 
      "id": "recVYQrqqD", 
      "record_id": "recVYQrqqD"
    }, '''
        if r['code']==0:
            links=r['data']       
        params={'app_token':bitapp_token,'table_id':indi_table,'graph_name':subgraph_name,'fields':'["指标名","指标代码","挂钩节点","指标性质","单位","指标定义","影响方向","画布位置X","画布位置Y","世界线跟踪表-主要相关指标"]'}
        r=base_fetch_func('http://172.21.0.14:81/bitapp/record',headers=None,params=params,method='get')
        '''"indicators": [
    {
      "fields": {
        "指标名": "全国新增风电装机量", 
        "指标性质": "定量"
      }, 
      "id": "recgJNitOI", 
      "record_id": "recgJNitOI"
    }
  ], '''
        if r['code']==0:
            indicators=r['data']   
        if nodes and links :
            if not indicators:
                indicators=[]
            raw={'nodes':nodes,'links':links,'indicators':indicators}
            #return raw
            result=post_process(raw)
            return result
        else:
            return {'code':-2,'msg':'检查节点/边/指标表失败，可能是子图名有误。检查到的结果：节点：%s\t\n边:%s \t\n 指标:%s'%(nodes,links,indicators)}
def find_file(token,id):
    import os
    root_dir=r'E:\wangzhilin\QuantumGalaxy\pics'
    file_dir=os.path.join(root_dir,token)
    files=os.listdir(file_dir)
    file_name=None
    for file in files:
        name=os.path.splitext(file)
        if name[0]==id:
            file_name=name[0]+name[1]
    return  file_dir,file_name
   