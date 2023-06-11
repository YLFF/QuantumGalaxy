from auth import *
import sys     
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re
from logging.handlers import RotatingFileHandler
import numpy as np
import pandas as pd
from jira import JIRA
from QGI.feishu import *
from QGI.mysql import MYSQL
from QGI.neoapi import Neo4j
def get_logger(name,chlevel=logging.ERROR):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = RotatingFileHandler(
        "E:\wangzhilin\QuantumGalaxy\server_openai\logs\%s.log"%name,
        'a',
        maxBytes=10*1024*1024,
        
        encoding='utf-8')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(chlevel)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

def get_mysql(database='qgdbs'):

    
    #database='qgdbs'
    mysql=MYSQL(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,database)

    return mysql
def get_neo(database='nova'):
    if database=='nova':
        neo=Neo4j(NOVA_URI,NOVA_USER,NOVA_PASSWORD)
    else:
        neo=Neo4j(ATLAS_URI,ATLAS_USER,ATLAS_PASSWORD)
    return neo
