
import logging
import jira
import sys

#time.sleep(1)
sys.path.append('E:\wangzhilin\QuantumGalaxy')
#print(sys.path)
from QGI.feishu import *
import numpy as np
from QGI.mysql import MYSQL
from iFinDPy import *
import pandas as pd
import time

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







def get_query_list(mysql):

    #sql0='select * from edb_info where find_in_set(code,"L001619976,L001618529,L001619472,G002600770,G002600771,G002600772")'
    sql="select ths_code,name,code from edb_info where name like '%国债%' and name like '%收益率%' and ths_code is not null"
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
    THS_iFinDLogout()
    return data



def compute(data):
    data=data.set_index('id')
    try:
        debt2,debt3,debt5=float(data.loc['L001619976','value'])/100,float(data.loc['L001618529','value'])/100,float(data.loc['L001619472','value'])/100
    except:
        debt2,debt3,debt5=np.nan,np.nan,np.nan
    try:
        usdebt2,usdebt3,usdebt5=float(data.loc['G002600770','value'])/100,float(data.loc['G002600771','value'])/100,float(data.loc['G002600772','value'])/100
    except:
        usdebt2,usdebt3,usdebt5=np.nan,np.nan,np.nan
    debt25=(((1+debt5)**5)/((1+debt2)**2))**(1/3)-1.005
    usdebt25=(((1+usdebt5)**5)/((1+usdebt2)**2))**(1/3)-1.005
    n_now=(debt3)**-1
    n_25=(debt25)**-1
    n_usnow=usdebt3**-1
    n_us25=usdebt25**-1

    #顺序：国债-3 N-now 国债-2 国债-3  国债-2~5 N-2 美国债-3 美N-now 美国债-2 美国债-5 美国债-2~5 美N-2
    #data={'n0_cny':n_now,'n2_cny':n_25,'n0_usd':n_usnow,'n2_usd':n_us25}
    data=pd.DataFrame( {'name':['n0_cny','n2_cny','n0_usd','n2_usd'],'value':[n_now,n_25,n_usnow,n_us25]})
    data.replace({np.nan:None},inplace=True)
    return data



def feishu_work(mysql,day):
    sql='select code,value from customized_data where find_in_set(code,"C00001.QG,C00002.QG,C00003.QG,C00004.QG") and date="'+day+'"'
    result=mysql.read_query(sql)
    #print(sql)
    

    result=dict(result)
    #print(result)
    datalist=[result['C00001.QG'],result['C00002.QG'],result['C00003.QG'],result['C00004.QG']]
    datalist=[day]+datalist
    feishu=FeishuAPI()
    r=feishu.append_table(datalist,table_id=table_dict['n_table_id'],sheet_id=table_dict['n_sheet1_id'])
    title='N值发布 - %s\n'%(date.today())
    msg=''
    try:
        msg+='A股（参考中国国债收益率，以当下及两年后的预期收益率综合计算后得出）\n当下的N：%.3f\n两年后远期的N：%.3f\n'%(datalist[1],datalist[2])
    except:
        pass
    try:
        msg+='美股（参考美国国债收益率，以当下及两年后的预期收益率综合计算后得出）\n当下的N：%.3f\n两年后远期的N：%.3f\n'%(datalist[3],datalist[4])
    except:
        pass
    #r=post_msg(title,msg,webhook='https://open.feishu.cn/open-apis/bot/v2/hook/f04a0171-6a64-4215-bba9-e9e7ff5bce7d')
    #print(msg)
    if msg =='':
        return 0
    else:
        
        time.sleep(5)
        r=post_n_msg(title,msg,webhook=webhook_dict['全员群voyager']) 
        if r[27]=='0':
            logger.info('succeed in posting msg to webhook :全员群voyager')
        return r


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
        d=compute(r) #d-> customized_data
        #d.set_index('name')
        print(d)
        code=['C00001.QG','C00002.QG','C00003.QG','C00004.QG']
        val1=[]
        for i,v in d.iterrows():
            val1.append((v['value'],day,code[i]))
        #print('val1')
        #return(val1)
        
        sql0="insert  into ths_edb_data (code,date,value) values(%s,%s,%s)"
        sql1="insert  into customized_data (value,date,code) values(%s,%s,%s)"
        result0=mysql.write_many_query(sql0,val0)
        result1=mysql.write_many_query(sql1,val1)
        r=feishu_work(mysql,day)
        mysql.close()
        #print(result0,result1)


if __name__=='__main__':
    job()

