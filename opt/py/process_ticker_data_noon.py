
from iFinDPy import *
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from datetime import datetime,timedelta

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
    fh=logging.FileHandler("E:/wangzhilin/QuantumGalaxy/logs/noon_ticker_log.log",'a',encoding='utf-8')
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
    df=pd.DataFrame(index=code)
    sql='update ticker_info set status=1 where code in %s'%codestr1
    result=mysql.write_query(sql)
    sql="select code,close_price from ticker_data where date='%s' and code in %s and not close_price is null  "%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','close']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    print(len(r))
    #neo.update_node_value(data=r)
    sql="select code,date from ticker_data where date='%s' and code in %s   "%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','date']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_data_date(data=r)
    sql="select code, market_value2 from ticker_data where date='%s' and code in %s and not market_value2 is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','market_value']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_market_value(data=r)
    sql="select code, stdchg3m from processed_data where date='%s' and code in %s  and not stdchg3m is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg3m']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_stdchg3m(data=result)
    sql="select code, stdchg1m from processed_data where date='%s' and code in %s and not stdchg1m is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg1m']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_stdchg1m(data=result)
    sql="select code, change_rate_1d from processed_data where date='%s' and code in %s and not change_rate_1d is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg1d']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_chg1d(data=result)
    sql='''SELECT t1.code,t1.stdchg1m - t2.stdchg1m AS diff \
    FROM processed_data t1 \
    JOIN processed_data t2 ON t1.code = t2.code \
    WHERE t1.date = '%s' AND t2.date = ( \
        SELECT MAX(date) \
        FROM processed_data \
        WHERE date <= DATE_SUB('%s', INTERVAL 7 DAY) AND code = t1.code \
    ) \
    AND t1.code  in %s'''%(today,today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','chg1m_1w_diff']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.add_indicator_to_company()

    df=df.dropna(how='all').round(2)
    cypher_list=[]
    for i,r in df.iterrows():
        
        cypher=f'''match (n:Company|Indicator {{code:'{i}'}}) set '''
        fields=''
        for k,v in r.items():
            if k=='date':
                fields+='n.'+k+'='+"'"+(str(v) if v else 'null')+"'"+','
            else:
                fields+='n.'+k+'='+(str(v) if v else 'null')+','
        cypher+=fields[:-1]
        
        cypher_list.append(cypher)
    print(f"{len(cypher_list)} cyphers loaded")
    print(cypher_list[0])
    r=neo.multi_cypher(cypher_list)  
    neo.close()
    mysql.close()
    return r







def update_from_code(neo):
    #neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    #neo_user = "QG_Editor"
    #neo_password = "editor"
    #neo=Neo4j(neo_uri,neo_user,neo_password)
    #uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
    #user = "neo4j"
    #password = "QuantumGalaxy"
    #neo=Neo4j(uri,user,password)
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
    df=pd.DataFrame(index=code)
    sql='update ticker_info set status=1 where code in %s'%codestr1
    result=mysql.write_query(sql)
    sql="select code,price from ticker_data_noon where date='%s' and code in %s and not price is null  "%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','value']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    print(len(r))
    #neo.update_node_value(data=r)
    sql="select code,date from ticker_data_noon where date='%s' and code in %s   "%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','datadate']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_data_date(data=r)
    #sql="select code, market_value2 from ticker_data where date='%s' and code in %s and not market_value2 is null"%(today,codestr1)
    #r=mysql.read_query(sql)
    #df1=pd.DataFrame(data=r,columns=['code','market_value']).set_index('code')
    #df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_market_value(data=r)
    sql="select code, stdchg3m from processed_data where date='%s' and code in %s  and not stdchg3m is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg3m']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_stdchg3m(data=result)
    sql="select code, stdchg1m from processed_data where date='%s' and code in %s and not stdchg1m is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg1m']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_stdchg1m(data=result)
    sql="select code, change_rate_1d from processed_data where date='%s' and code in %s and not change_rate_1d is null"%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','chgrate1d']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.update_node_chg1d(data=result)
    sql='''SELECT t1.code,t1.stdchg1m - t2.stdchg1m AS diff \
    FROM processed_data t1 \
    JOIN processed_data t2 ON t1.code = t2.code \
    WHERE t1.date = '%s' AND t2.date = ( \
        SELECT MAX(date) \
        FROM processed_data \
        WHERE date <= DATE_SUB('%s', INTERVAL 7 DAY) AND code = t1.code \
    ) \
    AND t1.code  in %s'''%(today,today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','stdchg1m_1w_diff']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    #neo.add_indicator_to_company()

    df=df.dropna(how='all').round(2)
    cypher_list=[]
    for i,r in df.iterrows():
        
        cypher=f'''match (n:Company|Indicator {{code:'{i}'}}) set '''
        fields=''
        for k,v in r.items():
            if k=='datadate':
                fields+='n.'+k+'='+"'"+(str(v) if v else 'null')+"'"+','
            else:
                fields+='n.'+k+'='+(str(v) if v else 'null')+','
        cypher+=fields[:-1]
        
        cypher_list.append(cypher)
    print(f"{len(cypher_list)} cyphers loaded")
    print(cypher_list[0])
    r=neo.multi_cypher(cypher_list)  
    neo.close()
    mysql.write_query('delete from processed_data where date="%s"'%today)
    mysql.close()
    return r






def query_code(mysql,today):
    '''return a list of df for every ticker in spcific region, df[code,close] [today-370,today]'''
   

    today=date.today()-timedelta(0)
    #yestoday=(today-timedelta(1)).__format__('%Y-%m-%d')
    start_date=(today-timedelta(370)).__format__('%Y-%m-%d')
    #sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code where region ='%s' and b.date>'%s' and a.status=1"%(region,start_date)
    sql="select a.code, b.date,b.close_price from ticker_info a inner join ticker_data b on a.code = b.code  where  b.date>'%s' and b.date<'%s' and a.status=1 and  (a.region='hk' or a.region='cn') "%(start_date,today.__format__('%Y-%m-%d'))
    result=mysql.read_query(sql)
    #sql="select c.qg_code, b.date,b.value from edb_info a inner join wind_edb_data b on a.wind_code = b.code  where  b.date>'%s' and b.date<'%s' and a.status=1 and (a.region='hk' or a.region='cn') "%(start_date,today.__format__('%Y-%m-%d'))


    #result+=mysql.read_query(sql)
    sql="select a.code,a.date,a.price from ticker_data_noon a inner join ticker_info b on a.code=b.code where a.date='%s' and b.status=1 and (b.region='hk' or b.region='cn') "%today.__format__('%Y-%m-%d')
    result+=mysql.read_query(sql)
    result=list(result)
    df=pd.DataFrame(result,columns=['code','date','close'])
    group=df.groupby('code') #tuple(code,df)
    df_list=[]
    #result=pd.DataFrame({code: data["close"] for code, data in group})
    #return result
    for t in group:
        #print(t)
        if t[1].shape[0]>90:
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
            'stdchg': compute_stdchg60(df, today)
        },
        index=df.columns,
    )
    #processed_df['date'],processed_df['chg1d']=today,compute_chg_from_days(test,today,1)
    #chg1d,chg3d,chg2w,chg1m,chg3m,chg6m,chg1y=compute_chg_from_days(df,today,1),compute_chg_from_days(df,today,3),compute_chg_from_days(df,today,14),compute_chg_from_days(df,today,30),compute_chg_from_days(df,today,90),compute_chg_from_days(df,today,180),compute_chg_from_days(df,today,365)
    #stdchg7d,stdchg1m,stdchg3m=compute_std_chg_from_days(df,today,7),compute_std_chg_from_days(df,today,30),compute_std_chg_from_days(df,today,90)
    #processed_df=pd.DataFrame(data=[[today,chg1d,chg3d,chg2w,chg1m,chg3m,chg6m,chg1y,stdchg7d,stdchg1m,stdchg3m]],columns=['date','chg1d','chg3d','chg2w','chg1m','chg3m','chg6m','chg1y','stdchg7d','stdchg1m','stdchg3m'])
    return processed_df





def metajob(region,today=None):
    logger.info('begin job for %s'%region)
    #THS_iFinDLogin('lzxh0011','450503')
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    if not today:
        if region=='US':
            today=date.today()-timedelta(1)
        else:
            today=date.today()-timedelta(0)
        
    test_sql='select * from ticker_data_noon where date = "%s" limit 5'%today.__format__("%Y-%m-%d")
    result=mysql.read_query(test_sql)
    if len(result)==0:
        info='no data from ticker_data_noon for region %s on %s'%(region,today.__format__("%Y-%m-%d"))
        number=0
        logger.info(info)
    else:
        df=query_code(mysql,today)
        logger.info('begin compute')
        result=compute(df,today)
        result=result.reset_index().rename(columns={'index':'code'})
        result=result.replace([np.inf, -np.inf], np.nan)
        result.replace({np.nan: None},inplace=True)
        sql='insert ignore into processed_data (code,date,change_rate_1d,change_rate_3d,change_rate_2w,change_rate_1m,change_rate_3m,change_rate_6m,change_rate_1y,stdchg7d,stdchg1m,stdchg3m,vol) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        val=result.values.tolist()
        number=mysql.write_many_query(sql,val)
        info='processed %s records for region %s on  %s'%(number,region,today.__format__("%Y-%m-%d"))
        if number<=500:
            info+='******may have some problems******'
    from QGI.feishu import text_group_msg
    try:
        week=datetime.today().weekday()+1

        info='行情更新日报'+info
        if 1<=week<=5 and number==0:
            info+='******may have some problems!!!!!!!!!!!!!!******'
        print(info)
        text_group_msg(info)
    except:pass
    return info
if __name__=='__main__':
    r=metajob('CNHK')
    print(r)
    uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
    user = "neo4j"
    password = "QuantumGalaxy"
    neo_nova=Neo4j(uri,user,password)
    #update_from_code(neo_atlas)
    update_from_code(neo_nova)





