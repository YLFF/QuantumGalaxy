import requests
import sys

sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
from copy import deepcopy


def bitable_name(app_token):
    r = requests.get(r'http://82.156.248.152:81/bitapp/?app_token=%s' %
                     app_token).json()
    if r['code'] == 0:
        return r['name']
    else:
        return None


def bitable_check(app_token):
    try:
        res = requests.get(
            r'http://172.21.0.14:81/bitapp/tables?app_token=%s' % app_token)
        tables = res.json()
        if tables['code'] == 0:
            #print(tables)
            tables = tables['data']
            node_table, link_table, indi_table = None, None, None

            for table in tables:
                if table['name'] == '节点表':
                    node_table = table['table_id']
                if table['name'] == '关系表':
                    link_table = table['table_id']
                if table['name'] == '监测指标表':
                    indi_table = table['table_id']
                if table['name'] == '骨干定义表':
                    backbone_table = table['table_id']
            if node_table and link_table and indi_table:
                print('good table')
                return True, [
                    node_table, link_table, indi_table, backbone_table
                ]
            else:
                msg = 'not all tables found, node,link,indicator :%s' % [
                    node_table, link_table, indi_table, backbone_table
                ]
                return False, msg
        else:
            print(tables)
            return False, tables
    except Exception as e:
        return False, e


def get_main_info(field):
    '''从某双向选择的field中获取textarr项，去除其他'''
    '''双选字段信息为list但似乎只有1个元素，处理方式存疑'''
    #return [one['text_arr'] for one in field]
    return field[0]['text_arr'] if field else None


def post_process(raw):
    '''raw:{nodes:...,links:...,indicators:,,,'''
    nodes, links, indicators, backbone_mark = raw['nodes'], raw['links'], raw[
        'indicators'], raw['backbone_mark']
    res_nodes = []
    try:
        for n in nodes:
            f = n['fields']
            more_info = {}

            external_backbone = get_main_info(f.get('所属外部骨干'))
            if external_backbone:
                more_info['external_backbone'] = external_backbone
            intro = f.get('简要介绍')
            if intro: more_info['intro'] = intro
            if  f.get('节点名称') and f.get('节点类型'):
                #print(f)
                res_node = {
                    'bitapp_id': n['record_id'],
                    'name': f.get('节点名称'),
                    'category': f.get('节点类型'),
                    'more_info': more_info
                }
                rough=f.get('粗骨干权限')
                #print(rough)
                if rough:
                    res_node['rough']=rough
                code = f.get('公司代码')
                if code: res_node['code'] = code
                region=f.get('区域')
                if region:
                    #print(region)
                    res_node['region']=region[0]['text']
                    
                x, y = f.get('画布位置X'), f.get('画布位置Y')
                #用查找引用方式写xy的话返回列表
                if type(x) == list:
                    x = x[0]
                if type(y) == list:
                    y = y[0]

                if x and y:
                    res_node['x'] = round(float(x), 2)
                    res_node['y'] = round(float(y), 2)
                res_nodes.append(res_node)
    except Exception as e:
        return {
            'code':
            -3,
            'msg':
            'had problem when processing nodes, type:"%s"exception:%s' %
            (e.__class__.__name__, str(e))
        }
    res_links = []
    try:
        for l in links:
            try:
                f = l['fields']
                more_info = {}
                pro_line = f.get('产线地位')
                if pro_line: more_info['pro_line'] = pro_line
                res_link = {
                    'bitapp_id': l['record_id'],
                    'source': f['主体'][0]['record_ids'][0],
                    'source_name_ref': f['主体'][0]['text'],
                    'target_name_ref': f['客体'][0]['text'],
                    'target': f['客体'][0]['record_ids'][0],
                    'category': get_main_info(f['关系'])[0],
                    'more_info': more_info
                }
                res_links.append(res_link)
            except:
                pass
    except Exception as e:
        return {
            'code':
            -3,
            'msg':
            'had problem when processing edges, type:"%s"exception:%s' %
            (e.__class__.__name__, str(e))
        }
    try:
        for i in indicators:
            try:
                f = i['fields']
                res_link = {
                    'bitapp_id': i['record_id'],
                    'source': i['record_id'],
                    'target': f['挂钩节点'][0]['record_ids'][0],
                    'category': "反映"
                }
                #res_links.append(res_link)
                #"指标代码","挂钩节点","指标性质","单位","指标定义","影响方向","画布位置X","画布位置Y","世界线跟踪表-主要相关指标"
                more_info = {}
                itype = f.get('指标性质')
                if itype: more_info['type'] = itype

                res_node = {
                    'bitapp_id': i['record_id'],
                    'name': f.get('指标名'),
                    'category': '指标',
                    'more_info': more_info
                }
                code = f.get('指标代码')
                if code: res_node['code'] = code
                x, y = f.get('画布位置X'), f.get('画布位置Y')
                if x and y:
                    res_node['x'] = round(float(x), 2)
                    res_node['y'] = round(float(y), 2)
                res_links.append(res_link)
                res_nodes.append(res_node)
            except:
                pass
    except Exception as e:
        return {
            'code':
            -3,
            'msg':
            'had problem when processing indicators, type:"%s"exception:%s' %
            (e.__class__.__name__, str(e))
        }
    return {
        'code': 0,
        'nodes': res_nodes,
        'links': res_links,
        'backbone_mark': backbone_mark
    }


def filter_result(expand_ids, raw):
    '''根据recordlist中节点的id，筛选出某张表中与该节点相连的边及相关节点'''

    result = deepcopy(raw)
    result['links'] = []
    result['nodes'] = []
    result['expanded_nodes'] = 0
    new_nodes = deepcopy(expand_ids)
    for l in raw['links']:
        #print(n)
        if l['source'] in expand_ids:
            #print(l)
            if not l['target'] in new_nodes:
                new_nodes.append(l['target'])
                result['expanded_nodes'] += 1
            result['links'].append(l)
        elif l['target'] in expand_ids:
            if not l['source'] in new_nodes:
                new_nodes.append(l['source'])
                result['expanded_nodes'] += 1
            result['links'].append(l)
    for n in raw['nodes']:
        if n['bitapp_id'] in new_nodes:
            result['nodes'].append(n)
    return result


def bitable_works(bitapp_token, subgraph_name=None):
    '''查多维表格的完整性（节点表 关系表 监测指标表,骨干定义表'''
    res, data = bitable_check(bitapp_token)
    if not res:
        return {
            'code': -1,
            'msg':
            '查多维表格完整性失败，请确认包含节点表/关系表/监测指标表，并且给予星图编辑器可读权限    ' + str(data)
        }
    else:
        #查节点表内容
        node_table, link_table, indi_table, backbone_table = data
        nodes, links, indicators = None, None, None
        params = {
            'app_token':
            bitapp_token,
            'table_id':
            node_table,
            'graph_name':
            subgraph_name,
            'fields':
            '["节点名称","节点类型","公司代码","画布位置X","画布位置Y","参与子图","所属外部骨干","简要介绍","粗骨干权限"]'
            #'["节点名称","节点类型","公司代码","画布位置X","画布位置Y","参与子图","所属外部骨干","简要介绍","粗骨干权限","区域"]'
        }
        r = base_fetch_func('http://172.21.0.14:81/bitapp/record',
                            headers=None,
                            params=params,
                            method='get')
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
        if r['code'] == 0:
            nodes = r['data']
        params = {
            'app_token': bitapp_token,
            'table_id': link_table,
            'graph_name': subgraph_name,
            'fields': '["主体","关系","客体","参与子图","产线地位","粗骨干权限"]'
        }
        r = base_fetch_func('http://172.21.0.14:81/bitapp/record',
                            headers=None,
                            params=params,
                            method='get')
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
        if r['code'] == 0:
            links = r['data']
        params = {
            'app_token':
            bitapp_token,
            'table_id':
            indi_table,
            'graph_name':
            subgraph_name,
            'fields':
            '["指标名","指标代码","挂钩节点","指标性质","单位","指标定义","影响方向","画布位置X","画布位置Y","世界线跟踪表-主要相关指标","粗骨干权限"]'
        }
        r = base_fetch_func('http://172.21.0.14:81/bitapp/record',
                            headers=None,
                            params=params,
                            method='get')
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
        if r['code'] == 0:
            indicators = r['data']
        params = {
            'app_token': bitapp_token,
            'table_id': backbone_table,
            'filter': 'CurrentValue.[本骨干标记]=1'
        }
        r = base_fetch_func('http://172.21.0.14:81/bitapp/record',
                            headers=None,
                            params=params,
                            method='get')

        if r['code'] == 0:
            backbone_mark = r['data']
        if nodes and links:
            if not indicators:
                indicators = []
            raw = {
                'nodes': nodes,
                'links': links,
                'indicators': indicators,
                'backbone_mark': backbone_mark
            }
            #return raw
            result = post_process(raw)
            return result

        else:
            return {
                'code':
                -2,
                'msg':
                '检查节点/边/指标表失败，可能是子图名有误。检查到的结果：节点：%s\t\n边:%s \t\n 指标:%s' %
                (nodes, links, indicators)
            }
