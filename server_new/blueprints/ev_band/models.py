from datetime import datetime,timedelta
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
import numpy as np
import pandas as pd
import json
import scipy,math
from jira import JIRA
from utils import get_logger
logger=get_logger(__name__)
def log_inter1(num:int,y0,y1):
    '''返回长度为num+2的插值列表。num:插值数量'''
    f=scipy.interpolate.interp1d(x=[0,num+1],y=[math.log(y0),math.log(y1)],kind='linear')
    res=f([x+1 for x in range(num)])

    res=[math.exp(r) for r in res]
    res.insert(0,y0)
    res.append(y1)
    return res
def geo_mean(data):
    return math.pow(np.prod(data),1.0/len(data))
def calcu_norm(xc,pc,xo,po,ppf) :
    '''-> (s,mu)'''
    xc=np.log(xc)
    xo=np.log(xo)
    no=round((1-po)*10-1)
    nc=round((1-pc)*10-1)
    #print(no,nc)
    s=(xo-xc)/(ppf[no]-ppf[nc])
    mu=((xo-ppf[no]*s+xc-ppf[nc]*s)/2)
    return(s,mu)
def ev_band_check(code):
    try:
        assert '.' in code
        code=code.upper()
    except:
        return False
    
    return code

def data_process(code):
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    jira= JIRA('https://research.quantumgalaxy.cn/', basic_auth=('wangzhilin', "wangzhilin"))
    try:
        issue=jira.search_issues(f'project = POSITION AND status != 尚未纳入 AND resolution = Unresolved AND cf[10201] ~  {code}')[0]
    except:
        logger.error(f'no position issue, code: {code}')
        return False,False

    try:
        target_date=issue.fields.customfield_10622
        start_date=issue.fields.updated[:10]

        xo=issue.fields.customfield_10918
        po=issue.fields.customfield_10919
        xc=issue.fields.customfield_10916
        pc=issue.fields.customfield_10914
        
        stock_start_date=datetime.strptime(start_date,'%Y-%m-%d')-timedelta(183)
        stock_start_date=stock_start_date.strftime('%Y-%m-%d')


        ev_data=mysql.read_query('select date,market_value from ticker_data where code="%s" and date<=now() and date>="%s"'%(code,stock_start_date))
        ev_data=[ev for ev in ev_data]
        stock_end_date=ev_data[-1][0]

        import math


        ppf = [-1.282, -0.842, -0.524, -0.253, 0, 0.253, 0.524, 0.842, 1.282]


        s,mu=calcu_norm(xc=xc,xo=xo,pc=pc,po=po,ppf=ppf)
        #print(s,mu)
        df=pd.DataFrame(data=ev_data,columns=['date','ev'])
        df.set_index('date',inplace=True)


        stock_data=mysql.read_query(f'select date,market_value from ticker_data where code="{code}" and date<="{start_date}" order by date desc limit 60')
        vol=mysql.read_query(f'select vol from processed_data where code="{code}" and date<="{start_date}" order by date desc limit 1')
        vol=vol[0][0]

        stock_data=[float(p) for (d,p) in stock_data]
        stock_data=geo_mean(stock_data)
        #print(stock_data)

        factor=[(1-vol)**10,(1-vol)**5,1,(1+vol)**5,(1+vol)**10,]
        start=np.outer(stock_data,factor)[0]
        #print(start)
        n=mysql.read_query('select value from customized_data where code="C00002.QG" order by date desc limit 1')[0][0]
        end=np.exp([mu-0.842*s,mu-0.5*s,mu,mu+0.5*s,mu+0.842*s])*n
        
        #print(start_date)
        start_date=datetime.strptime(start_date,'%Y-%m-%d')
        target_date=datetime.strptime(target_date,'%Y-%m-%d')
        days=(target_date-start_date).days
        interp_num=days-1
        day_list=[start_date+timedelta(i) for i in range(days+1)]
        day_list=[datetime.date(d) for d in day_list]
        level0=log_inter1(interp_num,start[0],end[0])

        level1=log_inter1(interp_num,start[1],end[1])

        level2=log_inter1(interp_num,start[2],end[2])

        level3=log_inter1(interp_num,start[3],end[3])

        level4=log_inter1(interp_num,start[4],end[4])
        level4=[level4[i]-level3[i] for i in range(len(level4))]
        level3=[level3[i]-level2[i] for i in range(len(level4))]
        level2=[level2[i]-level1[i] for i in range(len(level4))]
        level1=[level1[i]-level0[i] for i in range(len(level4))]
        level0=tuple(dict(zip(day_list,level0)).items())
        level1=tuple(dict(zip(day_list,level1)).items())
        level2=tuple(dict(zip(day_list,level2)).items())
        level3=tuple(dict(zip(day_list,level3)).items())
        level4=tuple(dict(zip(day_list,level4)).items())
        down_pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1])
        pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1]+level2[-1][1])
        up_pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1]+level2[-1][1]+level3[-1][1])
        down_pred_point=np.round(down_pred_point[1],2)
        pred_point=np.round(pred_point[1],2)

        up_pred_point=np.round(up_pred_point[1],2)
        df['last_ev']=None
        df.loc[df.index[-1],'last_ev']=df['ev'][-1]
        #df['last_ev'][-1]=df['ev'][-1]
        df1=pd.DataFrame(level0,columns=['date','level0'])
        df1.set_index('date',inplace=True)
        df=pd.concat([df,df1],axis=1)
        df1=pd.DataFrame(level1,columns=['date','level1'])
        df1.set_index('date',inplace=True)
        df=pd.concat([df,df1],axis=1)
        df1=pd.DataFrame(level2,columns=['date','level2'])
        df1.set_index('date',inplace=True)
        df=pd.concat([df,df1],axis=1)
        df1=pd.DataFrame(level3,columns=['date','level3'])
        df1.set_index('date',inplace=True)
        df=pd.concat([df,df1],axis=1)
        df1=pd.DataFrame(level4,columns=['date','level4'])
        df1.set_index('date',inplace=True)
        df=pd.concat([df,df1],axis=1)
        df['down_pred_point']=None
        df['pred_point']=None
        df['up_pred_point']=None
        down_pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1])
        pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1]+level2[-1][1])
        up_pred_point=(level0[-1][0],level0[-1][1]+level1[-1][1]+level2[-1][1]+level3[-1][1])
        down_pred_point=np.round(down_pred_point[1],2)
        pred_point=np.round(pred_point[1],2)

        up_pred_point=np.round(up_pred_point[1],2)
        
        df.index=df.index.astype('str',)
        df=df.reset_index()
        df.loc[df.shape[0]-1,'down_pred_point']=down_pred_point
        df.loc[df.shape[0]-1,'up_pred_point']=up_pred_point
        df.loc[df.shape[0]-1,'pred_point']=pred_point
        df = df.astype(object).replace(np.nan, 'None')
        dataset={}
        dataset['source']=[df.columns.to_list()]
        dataset['source']
        for i,r in df.iterrows():

            row=r.to_list()
            dataset['source'].append(row)
        j=json.dumps(dataset)
        summary=issue.fields.summary
        return j,summary
    except:
        logger.error('had exception during process data')
        return False,False