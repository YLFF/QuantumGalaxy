import sys
from datetime import datetime, timedelta

sys.path.append('E:\wangzhilin\QuantumGalaxy')
import copy

import logging

from random import random

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


import json
import math
import os

import numpy as np
import pandas as pd
import scipy
from jira import JIRA
from QGI.feishu import *

from QGI.mysql import MYSQL
from QGI.neoapi import Neo4j
from server_new.utils import get_logger
from .utils import *
logger=get_logger(__name__)
def get_neo():
    uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    user = "QG_Editor"
    password = "editor"
    neo=Neo4j(uri,user,password)
    return neo
def get_backbone_index():
    neo=get_neo()
    backbones=neo.read_query("match (n)  where not  n.backbone contains ',' return distinct n.backbone ")
    return [backbone.values()[0] for backbone in backbones]

class QGDiGraph(nx.DiGraph):
    pass
class Backbone2JS():
    def __init__(self,name):
        self.name=name
        uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
        user = "QG_Editor"
        password = "editor"
        self.neo=Neo4j(uri,user,password)
        host='localhost'
        user='Local_Editor'
        password='QuantumGalaxy'
        
        self.mysql=MYSQL(host,user,password,'qgdbs')
        self.G=None
    def _close_neo(self):
        self.neo.close()
    def _restart_neo(self):
        uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
        user = "QG_Editor"
        password = "editor"
        self.neo=Neo4j(uri,user,password)
        return self.neo
    def _get_backbone_from_neo(self):
        '''first of everything'''
        backbone=self.name
        cypher='match (n) where n.backbone contains "%s" \
        return distinct n.name as name,labels(n) as labels,n.backbone as backbone,n.code as code \
        union all \
        match (n1) where n1.backbone contains "%s" \
        with n1 \
        match (n:Indicator)-[]-(n1) \
        return  distinct n.name as name,labels(n) as labels,n.backbone as backbone,n.code as code order by labels'%(backbone,backbone)
        nodes=self.neo.read_query(cypher)
        cypher1='match p=(n1)-[r]->(n2) where n1.backbone contains "%s" and n2.backbone contains "%s" return startNode(r).name as start,endNode(r).name as end,type(r) as rela \
        union all \
        match p=(n:Indicator)-[r]-(n1) where n1.backbone contains "%s"\
        return  distinct startNode(r).name as start,endNode(r).name as end,type(r) as rela'%(backbone,backbone,backbone)
        edges=self.neo.read_query(cypher1)
        self.nodes,self.edges=nodes,edges
        return (nodes,edges)
    
    def __get_backbone_from_mysql(self):
        '''不能用：找不到与骨干节点相连的indicator，要等骨干相关标的完善之后'''
        backbone=self.name
        sql='select name,bname,labels,code from backbone_nodes where bname="%s"'%backbone
        pass
    def _init_graph(self,nodes,edges):
        G=QGDiGraph()
        assert nx.is_directed_acyclic_graph(G)
        

        for node in nodes:
            G.add_node(node[0],**node[1:])
        for edge in edges:
            G.add_edge(edge[0],edge[1],relationship=edge[2])
        self.G=G
        return G
    def get_G(self) -> nx.Graph:
        n,e=self._get_backbone_from_neo()
        print(f'获取{self.name}骨干图，共有{len(n)}个节点，{len(e)}条边')
        return self._init_graph(n,e)


    def _fetch_indicator_data(self):
        date=self.mysql.read_query('select date from processed_data where code="000001.SZ" order by date desc limit 1')
        #std7d=pd.DataFrame(index=[d[0] for d in date])
        std1m=pd.DataFrame(index=[d[0] for d in date])
        #std3m=pd.DataFrame(index=[d[0] for d in date])
        nodes=self.nodes
        for node in nodes:
            code=node.get('code')
            labels=node.get('labels')
            #print(labels)
            if code and 'Indicator' in labels:
                #print(node)
                d=self.mysql.read_query('select date,stdchg7d,stdchg1m,stdchg3m from processed_data where code= "%s" order by date desc limit 30'%code)
                #df7d=pd.DataFrame(index=[row[0]for row in d],columns=[code],data=[row[1] for row in d])
                df1m=pd.DataFrame(index=[row[0]for row in d],columns=[code],data=[row[2] for row in d])
                #df3m=pd.DataFrame(index=[row[0]for row in d],columns=[code],data=[row[3] for row in d])
                #std7d=pd.concat([std7d,df7d],axis=1)
                std1m=pd.concat([std1m,df1m],axis=1)
                #std3m=pd.concat([std3m,df3m],axis=1)
        #std7d=std7d.sort_index().fillna(method='bfill').dropna()
                #std7d.to_csv(r'E:\wangzhilin\QuantumGalaxy\backbone\raw_data\std7d.csv')
        std1m=std1m.sort_index().fillna(method='bfill').dropna()
                #std1m.to_csv(r'E:\wangzhilin\QuantumGalaxy\backbone\raw_data\std1m.csv')
        #std3m=std3m.sort_index().fillna(method='bfill').dropna()
                #std3m.to_csv(r'E:\wangzhilin\QuantumGalaxy\backbone\raw_data\std3m.csv')
        #self.std1m=std1m
        #print(std1m)
        return std1m

    def _gen_js_1day(self,one_day_data:pd.Series):
        '''从所有indicator边传导到对应的产品/工艺的供需差（数据用stdchg1m中某一天），在各节点加权平均（权重暂为1，考虑用市值/量利等），得到多个在节点上的初始激励'''
        if not self.G:
            self.get_G()
        G=copy.deepcopy(self.G)
        
        #print(std1m)
        dic={}
        
        for name,attr in self.G.nodes(True):
            if attr['code']:
                dic[attr['code']]=name

        '''
        for code,data in one_day_data.iteritems():
                node=dic[code]
                self.G.nodes[node]['std']=data
                #print(self.G.nodes[node])
                
        
        for n,preds in self.G.pred.items():
            if preds:
                values=[]
                for pred in preds:
                    std=self.G.nodes.data('std')[pred]
                    
                    if std:
                        values.append(std)
                if len(values)!=0:
                    self.G.nodes[n]['i']=np.average(values)
        [(n,d) for (n,d) in self.G.nodes.data('i') if d]
        '''       

        #每天为一组数据，放到nodes/edges里
        #print(date)
        datas=one_day_data.values
        max=np.max(datas)
        min=np.min(datas)
        column=one_day_data.index
        for code,data in one_day_data.iteritems():
            node=dic[code]
            G.nodes[node]['std']=data

            #nor=normalize(data,datas)
            #colorstr=get_cmap_color_str(nor,regrcmp)
            
            #print(colorstr)
        for u,v,attr in G.edges(data=True):
            if 'Indicator' in  G.nodes[u]['labels'] :
                if 'measure' in attr['relationship'] or 'produce' in attr['relationship']:
                    attr['velocity']=G.nodes[u]['std']
                    #print(attr['velocity'],datas)
                    nor=normalize(attr['velocity'],max,min)
                    colorstr=get_cmap_color_str(nor,regrcmp)
                    attr['color']=colorstr
                    
            else:
                attr['velocity']=0
            #a=Backbone_handler(G)


            node_json=[]
            stock=list(nx.get_node_attributes(G,'std').values())
            for n in copy.deepcopy(G.nodes(data=True)):
                name,attr=n
                attr['name']=name
                attr['labels']=attr.pop('labels')
                #attr['color']=get_cmap_color_str(normalize(attr['stock'],stock),regrcmp)
                node_json.append(attr)
                
            edge_json=[]
            velocity=list(nx.get_edge_attributes(G,'velocity').values())

            for e in copy.deepcopy(G.edges(data=True)):
                s,end,attr=e
                attr['source']=s
                attr['target']=end
                #print(attr)
                #attr['color']=get_cmap_color_str(normalize(attr['velocity'],velocity),regrcmp)
                #attr['color']=
                #
                edge_json.append(attr)
            #print(edge_json)
        #self.G=G
        return node_json,edge_json
    def gen_js(self,):
        std1m=self._fetch_indicator_data()
        jsdata={}
        jsdata['categories']=[{'name':"Product"},{'name':"Technique"}, {'name':"Company"}, {'name':"Indicator"}]
        jsdata['dates']=std1m.index.astype(str).tolist()
        jsdata['nodes']=[]
        jsdata['links']=[]
        print(f'共{len(jsdata["dates"])}天数据')
        
        for date,r in std1m.iterrows():
            #print(date,r['600584.SH'])
            n,e=self._gen_js_1day(r)
            jsdata['nodes'].append(n)
            jsdata['links'].append(e)
        return jsdata
