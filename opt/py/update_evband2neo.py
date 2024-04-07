# -*- coding: utf-8 -*-
'''市值走廊任务，从服务器读取现存的走廊并写入neo数据库对应节点。停用'''

from datetime import datetime,timedelta
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')

import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j
from QGI.feishu import *
from QGI.mysql import MYSQL,get_mysql
from QGI.logger import get_logger

mysql=get_mysql('web_server')

uri = "neo4j+ssc://0789bfae9.databases.neo4j.io"
user = "QG_Editor"
password = "qgeditor"
neo=Neo4j(uri,user,password)
codes=mysql.read_query('select code from ev_band_info where status=1')
logger=get_logger('evband2neo')
neo.simple_query('match (n:Indicator) remove n.evband_url')
n=0
for code in codes:
    code=code[0]
    url='http://82.156.248.152:82/ev_band/'+code
    r=neo.simple_query('match (n:Indicator) where n.code ="%s" set n.evband_url="%s" return n'%(code,url))
    if r:
        n+=1
logger.info(f'update {n} ev_bands to neo')