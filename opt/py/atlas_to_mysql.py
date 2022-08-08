

import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL

import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j


def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    #fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/aura_api_log.log",'a',encoding='utf-8')
    #fh.setLevel(logging.INFO)
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter=logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    logger.addHandler(ch)
    #logger.addHandler(fh)
    return logger
logger=logging.getLogger()


uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
user = "QG_Editor"
password = "editor"


neo=Neo4j(uri,user,password)
host='localhost'
user='Local_Editor'
password='QuantumGalaxy'
database='qgdbs'
mysql=MYSQL(host,user,password,database)


cypher='match (n) return id(n),labels(n),n.name,n.code,n.description'
result=neo.read_query(cypher)




val=[]
for r in result:
    val.append((r.values()[0],str(r.values()[1])[1:-1],r.values()[2],r.values()[3],r.values()[4]))


for v in val:
    sql='insert into atlas (id,labels,name,code,defination) values(%s,"%s","%s","%s","%s") on duplicate key update labels="%s",name="%s",code="%s",defination="%s"'%(v[0],v[1],v[2],v[3],v[4],v[1],v[2],v[3],v[4])
    #print(sql)
    mysql.write_query(sql)




