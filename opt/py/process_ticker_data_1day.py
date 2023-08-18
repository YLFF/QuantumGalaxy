from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL,get_mysql
from QGI.logger import get_logger
from datetime import date,timedelta,datetime
import pandas as pd
import numpy as np
from QGI.feishu import text_group_msg
def query_data(mysql,today):
    '''get ticker data from today-370 to today,and process to dataframe'''
    start_date=(today-timedelta(370)).__format__('%Y-%m-%d')
    end_date=today.__format__("%Y-%m-%d")
    #sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code where region ='%s' and b.date>'%s' and a.status=1"%(region,start_date)
    sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code inner join qg_indicator_info c on c.qg_code=a.code where  b.date>'%s' and b.date<='%s' and a.status=1 and c.need_process=1 "%(start_date,end_date)
    result=mysql.read_query(sql)
    sql="select c.qg_code, b.date,b.value from edb_info a inner join wind_edb_data b on a.wind_code = b.code inner join qg_indicator_info c on c.qg_code=a.code where  b.date>'%s' and b.date<='%s'  and c.need_process=1 "%(start_date,end_date)
    
    
    result+=mysql.read_query(sql)
    df=pd.DataFrame(result,columns=['code','date','close_price'])
    df['date']=pd.to_datetime(df['date'])
    groups=df.groupby('code')
    df_list=[]
    for code,t in groups:
        if t.shape[0]>1:
            df=t.set_index('date')
            df1=pd.DataFrame(data={df.iloc[1]['code']:df['close_price']},index=df.index)
            if df1.index[-1].__format__("%Y-%m-%d")==today.__format__("%Y-%m-%d"):
                df_list.append(df1)
    print(len(df_list))
    result=pd.concat(df_list,axis=1)
    result.replace({None:np.nan},inplace=True)
    result.fillna(method='pad',limit=10,inplace=True)
    result=result.astype(float)
    return result
# give a decorateor to handle the exception
def handle_processing_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            #logger this error with the function name and stack trace
            logger.error(f'Error in {fn.__name__}: {e}', exc_info=True)
            return None

    return wrapper

@handle_processing_exception
def compute_stdchg60(df,today):

        df=np.log(df)
        df=df.truncate(after=today)
        stdchg60=(df-df.shift(1)).iloc[-60:].std()
        return stdchg60
@handle_processing_exception
def compute_meanchg60(df,today):
        
                df=np.log(df)
                df=df.truncate(after=today)
                meanchg60=(df-df.shift(1)).iloc[-60:].mean()
                return meanchg60
@handle_processing_exception            
def compute_std_chg_from_days(df,today,days):
    #days=7,30,90

        df=np.log(df)
        df=df.truncate(after=today)
        after=df.iloc[-1]
        former=df.truncate(after=today-timedelta(days)).iloc[-1]
        stdchg60=(df-df.shift(1)).iloc[-60:,:].std()
        
        result=(after-former)/(np.sqrt(days)*stdchg60)
        return result
@handle_processing_exception
def compute_chg_from_days(df,today,days):
    #df=df.truncate(after=today).iloc[-1]
    former=df.truncate(after=today-timedelta(days)).iloc[-1]
    df=df.truncate(after=today).iloc[-1]
    return (df-former)/former

def compute(df,today):
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
    return processed_df
def process_job(region,today=None):
    
    mysql=get_mysql()
    
    num=mysql.read_query(f'select count(*) from ticker_data where date="{today}"')[0][0]
    if num<=500:
        logger.error(f'No data for {today}')
        return 0
    
    df=query_data(mysql,today)
    logger.info(f'Processing {today}, {df.shape[0]} records and {df.shape[1]} tickers')
    result=compute(df,today)
    result=result.reset_index().rename(columns={'index':'code'})
    result.replace([np.inf,-np.inf],np.nan,inplace=True)
    result.replace({np.nan:None},inplace=True)
    logger.info(f'Processed {today}, {result.shape[0]} tickers')
    sql='insert ignore into processed_data (code,date,change_rate_1d,change_rate_3d,change_rate_2w,change_rate_1m,change_rate_3m,change_rate_6m,change_rate_1y,stdchg7d,stdchg1m,stdchg3m,vol,change_mean) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    val=result.values.tolist()
    number=mysql.write_many_query(sql,val)
    return number
def meta_job(region,today=None):
    if not today:
        today=date.today()-timedelta(0) if region in {'CN','HK'} else date.today()-timedelta(days=1)
    number=process_job(region,today)
    
    info='processed %s records for region %s on  %s'%(number,region,today.__format__("%Y-%m-%d"))
    if number<=500:
            info+='******may have some problems******'
    logger.info(info)
    text_group_msg(info)
if __name__=='__main__':
    logger=get_logger(fh=True,f_name='processed_data_log')
    meta_job('US')