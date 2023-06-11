
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
    sql="select code, market_value2 from processed_data where date='%s' and code in %s and not market_value2 is null"%(today,codestr1)
    r=mysql.read_query(sql)
    neo.update_node_market_value(data=r)
    sql="select code, stdchg3m from processed_data where date='%s' and code in %s"%(today,codestr1)
    result=mysql.read_query(sql)
    neo.update_company_stdcgh3m(data=result)

    #neo.add_indicator_to_company()
    neo.close()
    mysql.close()


def update_from_code_1day(neo):
    #neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    #neo_user = "QG_Editor"
    #neo_password = "editor"
    #neo=Neo4j(neo_uri,neo_user,neo_password)
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
    df1=pd.DataFrame(data=r,columns=['code','value']).set_index('code')
    df=pd.merge(df,df1,'outer',left_index=True,right_index=True)
    print(len(r))
    #neo.update_node_value(data=r)
    sql="select code,date from ticker_data where date='%s' and code in %s   "%(today,codestr1)
    r=mysql.read_query(sql)
    df1=pd.DataFrame(data=r,columns=['code','datadate']).set_index('code')
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





if __name__=='__main__':
    neo_uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    neo_user = "QG_Editor"
    neo_password = "editor"
    #neo_atlas=Neo4j(neo_uri,neo_user,neo_password)
    uri = "neo4j+ssc://534ea9b7.databases.neo4j.io:7687"
    user = "neo4j"
    password = "QuantumGalaxy"
    neo_nova=Neo4j(uri,user,password)
    #update_from_code(neo_atlas)
    update_from_code_1day(neo_nova)







