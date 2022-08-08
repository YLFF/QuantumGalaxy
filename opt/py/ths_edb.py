
import logging

import sys

#time.sleep(1)
sys.path.append('E:\wangzhilin\QuantumGalaxy')
#print(sys.path)

import numpy as np
from QGI.mysql import MYSQL
from iFinDPy import *
import pandas as pd
import time

def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/ths_log.log",'a')
    fh.setLevel(logging.INFO)
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter=logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger







def get_query_list(mysql):

    #sql0='select * from edb_info where find_in_set(code,"L001619976,L001618529,L001619472,G002600770,G002600771,G002600772")'
    sql="select ths_code,name,code from edb_info where not ths_code is null"
    result_tuple=mysql.read_query(sql)
    #result=[]
    #for r in result_tuple:
    #    result.append(r)#(code,name)
    result=list(result_tuple)
    
    return(result)


def ths_query(result,day):
    THS_iFinDLogin('lzxh0011','450503')

    edb_list=[]
    for row in result:
            edb_list.append(row[0])
    edb_str=''
    for s in edb_list:
        edb_str+=s+';'
    edb_str=edb_str[:-1]
    
    data=THS_EDB(edb_str,'',day,day)
    #data=THS_EDB(edb_str,'','2022-06-01','2022-07-26')
    THS_iFinDLogout()
    return data




def job():
    time.sleep(5)
    logger=get_logger()
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    day=date.today()-timedelta(1)
    day=day.strftime('%Y-%m-%d')
    r0=get_query_list(mysql)
    r=ths_query(r0,day)
    assert r.errorcode==0
    r=r.data #r->edb_data
    if r.shape==(0,0):
        logger.info('no n_data for day:%s'%day)
        return 'no data today'
    else:    
        logger.info('got  data shape: %s,%s'%r.shape)
        
        #print(r)
        val0=[] 
        for i,row in r.iterrows():
            
            val0.append((row['id'],row['time'],float(row['value'])))
        #print(val0)

        #d.set_index('name')

        
        sql0="insert ignore  into ths_edb_data (code,date,value) values(%s,%s,%s)"

        result0=mysql.write_many_query(sql0,val0)

        mysql.close()
        #print(result0,result1)


if __name__=='__main__':
    job()

