import re
from jira import JIRA
import logging
import sys     
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re

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
