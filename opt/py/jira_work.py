#用来更新n值，目前qgdbs所有ticker都在jira issue中，此任务可下线
import logging
from  jira import JIRA
import sys
import time
#time.sleep(1)
sys.path.append('E:\wangzhilin\QuantumGalaxy')
#print(sys.path)

import numpy as np
from QGI.mysql import MYSQL,get_mysql
from datetime import date, timedelta
from QGI.logger import get_logger
if __name__=='__main__':
    logger=get_logger()
    jira = JIRA('https://research.quantumgalaxy.cn/', basic_auth=('wangzhilin', "wangzhilin"))
    cny = jira.issue(id='COMPSTUDY-5348')
    usd=jira.issue(id='COMPSTUDY-5349')
    day=(date.today()-timedelta(1)).__format__('%Y-%m-%d')
    sql='select code,value from customized_data where find_in_set(code,"C00001.QG,C00002.QG,C00003.QG,C00004.QG") and date="'+day+'"'
    
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    result=mysql.read_query(sql)
    result=dict(result)
    #print(result)
    result=[result['C00001.QG'],result['C00002.QG'],result['C00003.QG'],result['C00004.QG']]
    if result[0]:
        cny.update(customfield_10916=result[0],customfield_10918=result[1])
    if result[2]:
        usd.update(customfield_10916=result[2],customfield_10918=result[3])
    print(result)
    time.sleep(5)
    #datalist=[day]+datalist