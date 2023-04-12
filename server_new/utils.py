import re
from jira import JIRA
import logging
import sys     
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re
from QGI.feishu import text_group_msg
import numpy as np
import pandas as pd
from jira import JIRA
from QGI.feishu import *
from QGI.mysql import MYSQL
def get_logger(name,chlevel=logging.ERROR):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    #fh = logging.FileHandler(
    #    "E:/wangzhilin/QuantumGalaxy/logs/flask_server.log",
    #    'a',
    #    encoding='utf-8')
    #fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(chlevel)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    logger.addHandler(ch)
    #logger.addHandler(fh)
    return logger

def get_mysql(database='qgdbs'):

    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    #database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    return mysql

def openai_test():
    try:
        r=requests.get('http://172.21.0.14:84/test',timeout=(5, 10))
        r=r.json()
        if r['code']==0:
            r['msg']='ALL OK'
    except:
        r={'code':-3,'msg':':84 SERVER DOWN'}
    return r

def send_test_msg(msg):
    text_group_msg(str(msg))
    return True