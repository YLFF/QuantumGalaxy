
import logging
import sys
import numpy as np
sys.path.append('E:\wangzhilin\QuantumGalaxy')
print(sys.path)

 

from iFinDPy import *
from QGI.feishu import *
from QGI.mysql import MYSQL


def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/n_log.log",'a')
    fh.setLevel(logging.INFO)
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter=logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


 


 
'''host='localhost'
user='Local_Editor'
password='QuantumGalaxy'
database='qgdbs'
mysql=MYSQL(host,user,password,database)'''


 
def get_query_list(mysql):

    sql0='select * from edb_info where find_in_set(code,"L001619976,L001618529,L001619472,G002600770,G002600771,G002600772")'
    result_tuple=mysql.read_query(sql0)
    result=[]
    for r in result_tuple:
        result.append((r[1],r[3]))#(code,name)

    
    return(result)


 
#r=get_query_list(mysql)

 
'''day=date.today()-timedelta(3)
day=day.strftime('%Y-%m-%d')
day'''

 
def query(result,day):
    THS_iFinDLogin('lzxh0011','450503')

    edb_list=[]
    for row in result:
            edb_list.append(row[0])
    edb_str=''
    for s in edb_list:
        edb_str+=s+';'
    edb_str=edb_str[:-1]
    
    data=THS_EDB(edb_str,'',day,day)
    THS_iFinDLogout()
    return data


 
'''data=query(r,day)
data.data.shape!=(0,0)'''

 
def compute(data):
    debt2,debt3,debt5,usdebt2,usdebt3,usdebt5=data['value'].astype(float)/100
    debt25=(((1+debt5)**5)/((1+debt2)**2))**(1/3)-1.005
    usdebt25=(((1+usdebt5)**5)/((1+usdebt2)**2))**(1/3)-1.005
    n_now=(debt3)**-1
    n_25=(debt25)**-1
    n_usnow=usdebt3**-1
    n_us25=usdebt25**-1
    #顺序：国债-3 N-now 国债-2 国债-3  国债-2~5 N-2 美国债-3 美N-now 美国债-2 美国债-5 美国债-2~5 美N-2
    data={'n0_cny':n_now,'n2_cny':n_25,'n0_usd':n_usnow,'n2_usd':n_us25}
    return data

 
def feishu_work(mysql,day):
    sql='select name,value from customized_edb_data where find_in_set(name,"n0_cny,n2_cny,n0_usd,n2_usd") and date="'+day+'"'
    result=mysql.read_query(sql)
    print(sql)


    result=dict(result)
    datalist=[result['n0_cny'],result['n2_cny'],result['n0_usd'],result['n2_usd']]
    datalist=[day]+datalist
    r=append_table(datalist,table_id=table_dict['n_table_id'],sheet_id=table_dict['n_sheet1_id'])
    title='N值发布 - %s\n'%(date.today())
    msg='A股（参考中国国债收益率，以当下及两年后的预期收益率综合计算后得出）\n当下的N：%.3f\n两年后远期的N：%.3f\n'%(datalist[1],datalist[2])
    msg+='美股（参考美国国债收益率，以当下及两年后的预期收益率综合计算后得出）\n当下的N：%.3f\n两年后远期的N：%.3f\n'%(datalist[3],datalist[4])
    #r=post_msg(title,msg,webhook='https://open.feishu.cn/open-apis/bot/v2/hook/f04a0171-6a64-4215-bba9-e9e7ff5bce7d')
    #r=post_msg(title,msg,webhook=webhook_dict['Debug群juno'])
    return r


 


 
def job():

    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    day=date.today()-timedelta(1)
    day=day.strftime('%Y-%m-%d')
    r=get_query_list(mysql)
    r=query(r,day)
    assert r.errorcode==0
    r=r.data #r->edb_data
    if r.shape==(0,0):
        logger.info('no n_data for day:%s'%day)
        return 'no data today'
    else:    
        val0=[]
        for i,row in r.iterrows():
            
            val0.append((row['id'],row['time'],float(row['value'])))
        #print(val0)
        d=compute(r) #d-> customized_edb_data

        val1=[]
        for k,v in d.items():
            val1.append((k,v,day))
        #print(val1)
        sql0="insert into edb_data (code,date,value) values(%s,%s,%s)"
        sql1="insert into customized_edb_data (name,value,date) values(%s,%s,%s)"
        result0=mysql.wirte_many_query(sql0,val0)
        result1=mysql.wirte_many_query(sql1,val1)
        r=feishu_work(mysql,day)
        mysql.close()
        print(result0,result1)


logger=get_logger()
job()

 



