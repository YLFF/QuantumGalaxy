from flask import Flask
 
from flask_apscheduler import APScheduler
 
import datetime
 

from utils import get_mysql,get_logger
import logging
logger=get_logger('scheduler',chlevel=logging.INFO)

import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')

import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j
def reset_mysql():
    logger.info('start')
    mysql=get_mysql(database='web_server')
    mysql.write_query('delete from backbone_edges')
    mysql.write_query('delete from backbone_nodes')
    uri = "neo4j+ssc://789bfae9.databases.neo4j.io"
    user = "QG_Editor"
    password = "qgeditor"
    neo=Neo4j(uri,user,password)
    nodes=neo.read_query(cypher='match (n) where n.backbone contains "" \
        return distinct n.name,labels(n),n.backbone,n.code \
        union all \
        match (n1) where n1.backbone contains "" \
        with n1 \
        match (n:Indicator)-[]-(n1) \
        return  distinct n.name,labels(n),n.backbone,n.code order by labels(n)')
    edges=neo.read_query('match p=(n1)-[r]->(n2) where n1.backbone contains "" and n2.backbone contains "" return startNode(r).name,endNode(r).name,type(r) \
        union all \
        match p=(n:Indicator)-[r]-(n1) where n1.backbone contains ""\
        return  distinct startNode(r).name,endNode(r).name,type(r)')
    val=[]
    val1=[]
    
    for node in nodes:
        val.append((node.get('n.name'),str(node.get('labels(n)'))[1:-1],node.get('n.backbone'),node.get('n.code')))
    for edge in edges:
        val1.append((edge.get('startNode(r).name'),edge.get('endNode(r).name'),edge.get('type(r)')))
    #print(val)
    #print(val1)
    n=mysql.write_many_query('insert into backbone_nodes (name,labels,bname,code) values (%s,%s,%s,%s)',val)
    e=mysql.write_many_query('insert into backbone_edges (start,end,rela) values (%s,%s,%s)',val1)
    mysql.close()
    logger.info((n,e))
    return n,e
