
from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
import time

def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/ths_new_stock.log",'a',encoding='utf-8')
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



host='localhost'
user='Local_Editor'
password='QuantumGalaxy'
database='qgdbs'
mysql=MYSQL(host,user,password,database)



def init_ticker_info():
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    THS_iFinDLogin('lzxh0011','450503')
    today=(date.today()-timedelta(1)).__format__('%Y-%m-%d')
    dic={'CN':'001005010','HK':'011001012','US':'161001001'}
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
    mysql.close()
    #THS_iFinDLogout()



init_ticker_info()
THS_iFinDLogout()


time.sleep()