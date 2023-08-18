# -*- coding: utf-8 -*-
'''从同花顺标的池获取新标的写入qgdbs'''
from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL,get_mysql
import time
from QGI.logger import get_logger
''''write a doc about this project'''
logger=get_logger(fh=True,f_name='ths_new_stock')
mysql=get_mysql()


#logger=get_logger()





def init_ticker_info():

    THS_iFinDLogin('lzxh0011','450503')
    today=(date.today()-timedelta(1)).__format__('%Y-%m-%d')
    dic={'CN':'001005120','HK':'011001012','US':'161001001'}
    #all cn:001005120 all A股 001005010
    #dic={'USA':'161001001'}
    for k,v in dic.items():
        list_df=THS_DP('block',today+';'+v,'thscode:Y,security_name:Y')
        assert list_df.errorcode==0
        list_df=list_df.data
        sql="insert ignore into qg_indicator_info (qg_code,name,category,need_process) values (%s,%s,'ticker',1)"
        sql1="insert ignore into ticker_info (code,name,type,region,status) values (%s,%s,'stock','"+k+"',1)"
        
        
        val=[]
        for i,r in list_df.iterrows():
            val.append((r['THSCODE'],r['SECURITY_NAME']))
        result=mysql.write_many_query(sql,val)
        result=mysql.write_many_query(sql1,val)
    
    THS_iFinDLogout()



init_ticker_info()
THS_iFinDLogout()
mysql.close()

#time.sleep()