
from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np


def query_code(mysql,today):
    '''return a list of df for every ticker in spcific region, df[code,close] [today-370,today]'''
   
    #today=date.today()-timedelta(1)
    start_date=(today-timedelta(370)).__format__('%Y-%m-%d')
    #sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code where region ='%s' and b.date>'%s' and a.status=1"%(region,start_date)
    sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code inner join qg_indicator_info c on c.qg_code=a.code where  b.date>'%s' and a.status=1 and c.need_process=1 "%start_date
    result=mysql.read_query(sql)
    sql="select c.qg_code, b.date,b.value from edb_info a inner join wind_edb_data b on a.wind_code = b.code inner join qg_indicator_info c on c.qg_code=a.code where  b.date>'%s'  and c.need_process=1 "%start_date
    
    
    result+=mysql.read_query(sql)
    result=list(result)
    
    df=pd.DataFrame(result,columns=['code','date','close'])
    group=df.groupby('code') #tuple(code,df)
    df_list=[]
    #result=pd.DataFrame({code: data["close"] for code, data in group})
    #return result
    for t in group:
        #print(t)
        if t[1].shape[0]>30:
            t[1]['date']=pd.to_datetime(t[1]['date'])
            df=t[1].set_index('date')
            df1=pd.DataFrame(data={df.iloc[1]['code']:df['close']},index=df.index)
            #print(df1)
            if df1.index[-1].__format__("%Y-%m-%d")==today.__format__("%Y-%m-%d"):

                #print(t[0])
                df_list.append(df1)
    result=pd.concat(df_list,axis=1)
    result.replace({None:np.nan},inplace=True)
    result.fillna(method='pad',limit=10,inplace=True)
    result=result.astype('float')
    return result









def compute_chg_from_days(df,today:datetime.date,days:int):
    try:# for some new ticker which has no date before the day
        df=df.truncate(after=today)
        #print(df)
        #print(days)
        former=df.truncate(after=today-timedelta(days)).iloc[-1]

        return (df.iloc[-1]-former)/former
    except:
        return None

    
    





def compute_std_chg_from_days(df,today,days):
    #days=7,30,90
    try:
        df=df.truncate(after=today)
        after=np.log(df.iloc[-1])
        former=np.log(df.truncate(after=today-timedelta(days)).iloc[-1])
        stdchg60=(np.log(df)-np.log(df.shift(1))).iloc[-60:,:].std()
        
        result=(after-former)/(np.sqrt(days)*stdchg60)
        return result
    except:

        raise 


def compute_std_chg_from_days(df,today,days):
    #days=7,30,90
    try:
        df=np.log(df)
        df=df.truncate(after=today)
        after=df.iloc[-1]
        former=df.truncate(after=today-timedelta(days)).iloc[-1]
        stdchg60=(df-df.shift(1)).iloc[-60:,:].std()
        
        result=(after-former)/(np.sqrt(days)*stdchg60)
        return result
    except:

        raise 


def compute_stdchg60(df,today):
    try:
        df=np.log(df)
        df=df.truncate(after=today)
        stdchg60=(df-df.shift(1)).iloc[-60:,:].std()
        

        return stdchg60
    except:

        raise 

def compute_meanchg60(df,today):
    try:
        df=np.log(df)
        df=df.truncate(after=today)
        stdchg60=(df-df.shift(1)).iloc[-60:,:].mean()
        

        return stdchg60
    except:

        return None
def compute(df, today: datetime.date):
    processed_df = pd.DataFrame(
        data={
            'date': today,
            'chg1d': compute_chg_from_days(df, today, 1),
            'chg3d': compute_chg_from_days(df, today, 3),
            'chg2w': compute_chg_from_days(df, today, 14),
            'chg1m': compute_chg_from_days(df, today, 30),
            'chg3m': compute_chg_from_days(df, today, 91),
            'chg6m': compute_chg_from_days(df, today, 182),
            'chg1y': compute_chg_from_days(df, today, 365),
            'stdchg7d': compute_std_chg_from_days(df, today, 7),
            'stdchg1m': compute_std_chg_from_days(df, today, 30),
            'stdchg3m': compute_std_chg_from_days(df, today, 90),
            'stdchg': compute_stdchg60(df, today),
            'change_mean':compute_meanchg60(df,today)
        },
        index=df.columns,
    )
    #processed_df['date'],processed_df['chg1d']=today,compute_chg_from_days(test,today,1)
    #chg1d,chg3d,chg2w,chg1m,chg3m,chg6m,chg1y=compute_chg_from_days(df,today,1),compute_chg_from_days(df,today,3),compute_chg_from_days(df,today,14),compute_chg_from_days(df,today,30),compute_chg_from_days(df,today,90),compute_chg_from_days(df,today,180),compute_chg_from_days(df,today,365)
    #stdchg7d,stdchg1m,stdchg3m=compute_std_chg_from_days(df,today,7),compute_std_chg_from_days(df,today,30),compute_std_chg_from_days(df,today,90)
    #processed_df=pd.DataFrame(data=[[today,chg1d,chg3d,chg2w,chg1m,chg3m,chg6m,chg1y,stdchg7d,stdchg1m,stdchg3m]],columns=['date','chg1d','chg3d','chg2w','chg1m','chg3m','chg6m','chg1y','stdchg7d','stdchg1m','stdchg3m'])
    return processed_df


def get_logger():
    logger=logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/processed_data_log.log",'a')
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


def metajob(region):
    logger.info('begin job for %s'%region)
    THS_iFinDLogin('lzxh0011','450503')
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)

    if region=='US':
        today=date.today()-timedelta(1)
    else:
        today=date.today()-timedelta()
    test_sql='select * from ticker_data where date = "%s" limit 5'%today.__format__("%Y-%m-%d")
    result=mysql.read_query(test_sql)
    if len(result)==0:
        info='no data from ticker_data for region %s on %s'%(region,today.__format__("%Y-%m-%d"))
        logger.info(info)
        number=0
    else:
        df=query_code(mysql,today)
        logger.info('begin compute')
        result=compute(df,today)
        result=result.reset_index().rename(columns={'index':'code'})
        result=result.replace([np.inf, -np.inf], np.nan)
        result.replace({np.nan: None},inplace=True)
        sql='insert ignore into processed_data (code,date,change_rate_1d,change_rate_3d,change_rate_2w,change_rate_1m,change_rate_3m,change_rate_6m,change_rate_1y,stdchg7d,stdchg1m,stdchg3m,vol,change_mean) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        val=result.values.tolist()
        number=mysql.write_many_query(sql,val)
        info='processed %s records for region %s on  %s'%(number,region,today.__format__("%Y-%m-%d"))
        if number<=500:
            info+='******may have some problems******'
    from QGI.feishu import text_group_msg
    try:
        
        week=datetime.today().weekday()

        info='行情更新日报'+info
        if 1<=week<=5 and number==0:
            info+='******may have some problems!!!!!!!!!!!!!!******'
        #text_group_msg(info)
    except:pass
    return info

        

if __name__=='__main__':
    metajob('US')




