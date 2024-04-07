import requests
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
from QGI.neoapi import Neo4j
def get_neo():
    
    neo_uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
    neo_user = "neo4j"
    neo_password = "QuantumGalaxy"

    '''neo_uri = "neo4j+ssc://789bfae9.databases.neo4j.io"
    neo_user = "QG_Editor"
    neo_password = "qgeditor"'''


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
    #dic['others']=prop
    
    if prop.get('code',None):
        dic['code']=prop['code']
    if prop.get('value',None):
        dic['value']=prop['value']
    if prop.get('market_value',None):
        dic['market_value']=prop['market_value']
    
    if prop.get('chgrate1d',None):
        dic['chgrate1d']=prop['chgrate1d']
    if prop.get('stdchg1m',None):
        dic['stdchg1m']=prop['stdchg1m']
    if prop.get('stdchg3m',None):
        dic['stdchg3m']=prop['stdchg3m']

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
def build_neo_data(name,model):
    '''model=[ext,vague,code]'''
    neo=get_neo()
    print('start query in model: %s'%model)
    '''从名字获取星图中两步以内相关的节点和边，返回组装的json'''
    if model=='exact':
        
        node_cypher='match (n)-[*0..2]-(n1) where n.name="%s" return distinct n1'%name
        link_cypher='match (n)-[r]-(n1) where n.name="%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.name="%s" return r'%(name,name)
        
    elif model=='vague':
        node_cypher='match (n)-[*0..2]-(n1) where n.name contains "%s" return distinct n1'%name
        link_cypher='match (n)-[r]-(n1) where n.name contains "%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.name contains "%s" return r'%(name,name)
    elif model=='code':
        node_cypher='match (n)-[*0..2]-(n1) where n.code = "%s" return distinct n1'%name
        link_cypher='match (n)-[r]-(n1) where n.code= "%s" return r \
            union \
            match (n)-[r1]-(n1)-[r]-(n2) where n.code= "%s" return r'%(name,name)
    print(node_cypher)
    nodes=neo.simple_query(node_cypher)
    links=neo.simple_query(link_cypher)
    nodesdata=[]
    for record in nodes:
        node=record[0]
        nodesdata.append(node_process(node))
    linksdata=[]
    for record in links:
        link=record[0]
        linksdata.append(edge_process(link))
    return {'nodes':nodesdata,'links':linksdata}
    
def user_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        r"E:\wangzhilin\QuantumGalaxy\server_83\logs\user.log",
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