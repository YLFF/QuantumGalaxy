
from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j



def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/aura_api_log.log",'a',encoding='utf-8')
    fh.setLevel(logging.INFO)
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter=logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
logger=get_logger()


def update_from_name():
    neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    neo_user = "QG_Editor"
    neo_password = "editor"
    neo=Neo4j(neo_uri,neo_user,neo_password)
    sql_host='localhost'
    sql_user='Local_Editor'
    sql_password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(sql_host,sql_user,sql_password,database)
    code=neo.fetch_company_with_code()
    today=date.today()-timedelta(1)
    today=today.__format__('%y-%m-%d')
    codestr=str(code)
    codestr1='('+codestr[1:-1]+')'
    sql="select code,close_price from ticker_data where date='%s' and code in %s"%(today,codestr1)
    r=mysql.read_query(sql)
    neo.update_company_value(data=r)

    sql="select code, stdchg3m from processed_data where date='%s' and code in %s"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_company_stdcgh3m(data=result)

    neo.add_indicator_to_company()
    neo.close()
    mysql.close()


def update_from_code_1day():
    neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    neo_user = "QG_Editor"
    neo_password = "editor"
    neo=Neo4j(neo_uri,neo_user,neo_password)
    sql_host='localhost'
    sql_user='Local_Editor'
    sql_password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(sql_host,sql_user,sql_password,database)
    code=neo.fetch_company_and_indicator_with_code()
    strip_code=[]
    for c in code:
        strip_code.append(c.replace('\t','').replace('\n',''))
    today=date.today()-timedelta(1)
    today=today.__format__('%y-%m-%d')
    codestr=str(strip_code)
    codestr1='('+codestr[1:-1]+')'
    sql='update ticker_info set status=1 where code in %s'%codestr1
    result=mysql.write_query(sql)
    sql="select code,close_price from ticker_data where date='%s' and code in %s and not close_price is null  "%(today,codestr1)
    r=mysql.read_query(sql)
    
    neo.update_node_value(data=r)
    
    sql="select code,date from ticker_data where date='%s' and code in %s  "%(today,codestr1)
    r=mysql.read_query(sql)
    neo.update_node_data_date(data=r)
    
    sql="select code, stdchg3m from processed_data where date='%s' and code in %s and not stdchg3m is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_stdcgh3m(data=result)
    sql="select code, stdchg1m from processed_data where date='%s' and code in %s and not stdchg1m is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_stdcgh1m(data=result)
    sql="select code, change_rate_1d from processed_data where date='%s' and code in %s and not change_rate_1d is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_chg1d(data=result)
    neo.add_indicator_to_company()
    neo.close()
    mysql.close()







def update_from_code():
    neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    neo_user = "QG_Editor"
    neo_password = "editor"
    neo=Neo4j(neo_uri,neo_user,neo_password)
    sql_host='localhost'
    sql_user='Local_Editor'
    sql_password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(sql_host,sql_user,sql_password,database)
    code=neo.fetch_company_and_indicator_with_code()
    strip_code=[]
    for c in code:
        strip_code.append(c.replace('\t','').replace('\n',''))
    today=date.today()-timedelta(0)
    today=today.__format__('%y-%m-%d')
    codestr=str(strip_code)
    codestr1='('+codestr[1:-1]+')'
    sql='update ticker_info set status=1 where code in %s'%codestr1
    result=mysql.write_query(sql)
    sql="select code,close_price from ticker_data where date='%s' and code in %s and not close_price is null  "%(today,codestr1)
    r=mysql.read_query(sql)

    neo.update_node_value(data=r)
    sql="select code,date from ticker_data where date='%s' and code in %s   "%(today,codestr1)
    r=mysql.read_query(sql)
    neo.update_node_data_date(data=r)
    
    sql="select code, stdchg3m from processed_data where date='%s' and code in %s  and not stdchg3m is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_stdcgh3m(data=result)
    sql="select code, stdchg1m from processed_data where date='%s' and code in %s and not stdchg1m is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_stdcgh1m(data=result)
    sql="select code, change_rate_1d from processed_data where date='%s' and code in %s and not change_rate_1d is null"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_node_chg1d(data=result)
    neo.add_indicator_to_company()
    neo.close()
    mysql.close()





if __name__=='__main__':
    update_from_code_1day()







