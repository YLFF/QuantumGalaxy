from datetime import datetime,timedelta
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')

import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j
from QGI.feishu import *
from QGI.mysql import MYSQL
from QGI.logger import get_logger

mysql=MYSQL(db='web_server')
uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
user = "QG_Editor"
password = "editor"
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