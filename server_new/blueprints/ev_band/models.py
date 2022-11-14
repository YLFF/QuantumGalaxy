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

    res=[round(math.exp(r),2) for r in res]
    res.insert(0,y0)
    res.append(y1)
    return res
def geo_mean(data,factor=10):
    raw=math.pow(np.prod(data),1.0/len(data))
    #data0=data[0]
    #data1=data[-1]
    data=data+[data[0]]*factor
    #data=[data[-1]]
    '''增加factor，使走廊起点离当天市值更近'''
    mean=math.pow(np.prod(data),1.0/len(data))
    #print(raw,mean,data1,data0)
    return mean
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
        return code
    
    return code


class Code2JS():
    '''对issue changelog分析并拆解为多个走廊（一个走廊初始数据为6个数）'''
    def __init__(self,code):
        self.code=code
        host='localhost'
        user='Local_Editor'
        password='QuantumGalaxy'
        database='qgdbs'
        self.m='xn'
        self.mysql=MYSQL(host,user,password,database)
        self.server_mysql=MYSQL(host,user,password,db='web_server')
    def find_issue(self):
        from atlassian import Jira
        #print(self.code)
        jira = Jira(
            url='https://research.quantumgalaxy.cn/',
            username='wangzhilin',
            password='wangzhilin')
        self.issue=jira.jql(f'project = POSITION AND cf[10201] ~  {self.code}')
       
        model=self.issue['issues'][0]['fields']['customfield_11206']
        if model:
            if model['id']=='10801':
                m='x'
            elif model['id']=='10800':
                m='xn'
            else:
                m='xn'
        else:
            m='xn'
        self.m=m
        key=self.issue['issues'][0]['key']

        self.code=self.issue['issues'][0]['fields']['customfield_10201']
        log=jira.get_issue_changelog(key)['histories']
        return log
    def fetch_summary(self):
        try:
            self.find_issue()
            return self.issue['issues'][0]['fields']['summary']
        except Exception as e:
            logger.error(e)
            return False
    def clean_data(self,log):
        '''只保留issue changelog中包含 目标情景日/xo/po/xc/pc等字段的日志及其时间'''
        history=[]
        for row in log:
            t=datetime.strptime(row['created'][:16],'%Y-%m-%dT%H:%M')
            items=row['items']
            new={}
            get=False
            for item in items:
                field=item['field']
                if field  in ['未来情景日','保守认为利润(Xc)','乐观认为利润(Xo)','乐观情景概率','保守情景概率']:
                    
                    new['start_date']=t
                    if field=='未来情景日':
                        new['target_date']=datetime.strptime(item['toString'],'%Y-%m-%d')
                    if field=='保守认为利润(Xc)':
                        new['xc']=item['toString']
                    if field=='乐观认为利润(Xo)':
                        new['xo']=item['toString']
                    if field=='乐观情景概率':
                        new['po']=item['toString']
                    if field=='保守情景概率':
                        new['pc']=item['toString']



                    if not get:
                        get=True
                        history.append(new)

                    
                       

        return history
    def split_ev_band(self,history):

        '''以12小时为界，间隔低于12小时则不视为新走廊；将所有走廊的完整数据生成'''
        '''issue:不视为新走廊，但数值应当每次更新为最新'''
        results=[]
        for i in range(len(history)):
            
            if i ==0 :
                start_date=history[i].get('start_date',None)
                target_date=history[i].get('target_date',None)
                pc=history[i].get('pc',None)
                po=history[i].get('po',None)
                xc=history[i].get('xc',None)
                xo=history[i].get('xo',None)
                result=history[i]
                keys=['start_date','target_date','pc','xc','xo','po']
                values=[start_date,target_date,pc,xc,xo,po]

            
               
            start_date=history[i].get('start_date',start_date)
            target_date=history[i].get('target_date',target_date)
            pc=history[i].get('pc',pc)
            po=history[i].get('po',po)
            xc=history[i].get('xc',xc)
            xo=history[i].get('xo',xo)
            values=[start_date,target_date,pc,xc,xo,po]
            result=dict(zip(keys,values))
            #print(result)
            if i<len(history)-1:
                delta=history[i+1]['start_date']-history[i]['start_date']
                if delta.days==0 and delta.seconds<43200:
                        pass
                else:
                    
                    results.append(result)
            else:
                results.append(result)
        return results
    def history_from_mysql(self):
        mysql=self.server_mysql
        code=self.code
        try:
            if mysql.read_query('select status from ev_band_info where code="%s"'%code)[0][0]:
                res=mysql.read_query('select start_date,target_date,pc,xc,xo,po from ev_band_data where code="%s"'%code)
                h=[]
                for r in res:
                    h.append(dict(zip(('start_date','target_date','pc','xc','xo','po'),r)))
                #print('get history results from mysql:%s'%mysql)
                logger.info('get history results from mysql')
                #print(h)
                return h
        except Exception as e:
            logger.error('had error where fetch history from mysql:%s'%e)
            return 0
    def work(self):
        try:
            results=self.history_from_mysql()

            if results:

                pass
            else:
                history=self.split_ev_band(self.clean_data(self.find_issue()))
                results=self.split_ev_band(history)
                print('using jira api for history data')
            js=[]
            results=results[::-1]
            for r in results:
                one=self.one_work(r)
                
                if not one:
                    return False,False
                js.append(one)
                r['start_date']=r['start_date'].strftime("%Y-%m-%d")
                r['target_date']=r['target_date'].strftime("%Y-%m-%d")
            #js=json.dumps(js)
            return results,js,self.m
        except Exception as e:
            logger.error(e)
            return (False,False,False)
    def gen_dataset(self,data,model='xn'):
        code=self.code
        mysql=self.mysql
        if model=='xn' or model ==None:

            target_date=data['target_date']
            start_date=data['start_date']

            xo,xc,po,pc=float(data['xo']),float(data['xc']),float(data['po']),float(data['pc'])
            
            stock_start_date=start_date-timedelta(183)
            stock_start_date=stock_start_date.strftime('%Y-%m-%d')

            #print(xo,xc,po,pc,target_date,start_date)
            ev_data=mysql.read_query('select date,market_value from ticker_data where code="%s" and date<=now() and date>="%s"'%(code,stock_start_date))
            ev_data=[ev for ev in ev_data]
            stock_end_date=ev_data[-1][0]

            import math


            ppf = [-1.282, -0.842, -0.524, -0.253, 0, 0.253, 0.524, 0.842, 1.282]


            s,mu=calcu_norm(xc,pc,xo,po,ppf)
            #print(s,mu)
            df=pd.DataFrame(data=ev_data,columns=['date','ev'])
            df.set_index('date',inplace=True)


            stock_data=mysql.read_query(f'select date,market_value from ticker_data where code="{code}" and date<="{start_date}" order by date desc limit 45')
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
            #start_date=datetime.strptime(start_date,'%Y-%m-%d')
            #target_date=datetime.strptime(target_date,'%Y-%m-%d')
            days=(target_date-start_date).days
            interp_num=days-1
            day_list=[start_date+timedelta(i) for i in range(days+1)]
            day_list=[datetime.date(d) for d in day_list]
            level0=log_inter1(interp_num,start[0],end[0])

            level1=log_inter1(interp_num,start[1],end[1])

            level2=log_inter1(interp_num,start[2],end[2])
            #print(level2)
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
            df.loc[df.index[-1],'last_ev']=float(df['ev'][-1]).__round__(2)
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
            df.sort_index(inplace=True)
            last_row=df.iloc[-1:]
            last_row.index+=timedelta(1)
            #print(last_row.index)
            df=pd.concat([df,last_row])
            df.index=df.index.astype('str',)
            df=df.reset_index()
            df.loc[df.shape[0]-2,'down_pred_point']=down_pred_point
            df.loc[df.shape[0]-2,'up_pred_point']=up_pred_point
            df.loc[df.shape[0]-2,'pred_point']=pred_point
            df = df.astype(object).replace(np.nan, 'None')
            dataset={}
            dataset['source']=[df.columns.to_list()]
            dataset['source']
            for i,r in df.iterrows():

                row=r.to_list()
                dataset['source'].append(row)
            #j=json.dumps(dataset)
        
        elif model=='x' :

            target_date=data['target_date']
            start_date=data['start_date']

            xo,xc,po,pc=float(data['xo']),float(data['xc']),float(data['po']),float(data['pc'])
            
            stock_start_date=start_date-timedelta(183)
            stock_start_date=stock_start_date.strftime('%Y-%m-%d')

            #print(xo,xc,po,pc,target_date,start_date)
            ev_data=mysql.read_query('select date,close_price  from ticker_data where code="%s" and date<=now() and date>="%s"'%(code,stock_start_date))
            ev_data=[ev for ev in ev_data]
            stock_end_date=ev_data[-1][0]

            import math


            ppf = [-1.282, -0.842, -0.524, -0.253, 0, 0.253, 0.524, 0.842, 1.282]


            s,mu=calcu_norm(xc,pc,xo,po,ppf)
            #print(s,mu)
            df=pd.DataFrame(data=ev_data,columns=['date','ev'])
            df.set_index('date',inplace=True)
            df=df.astype({'ev':'float64'})

            stock_data=mysql.read_query(f'select date,close_price from ticker_data where code="{code}" and date<="{start_date}" order by date desc limit 45')
            vol=mysql.read_query(f'select vol from processed_data where code="{code}" and date<="{start_date}" order by date desc limit 1')
            vol=vol[0][0]

            stock_data=[float(p) for (d,p) in stock_data]
            stock_data=geo_mean(stock_data)
            #print(stock_data)

            factor=[(1-vol)**10,(1-vol)**5,1,(1+vol)**5,(1+vol)**10,]
            start=np.outer(stock_data,factor)[0]
            #print(start)
            #n=mysql.read_query('select value from customized_data where code="C00002.QG" order by date desc limit 1')[0][0]
            end=np.exp([mu-0.842*s,mu-0.5*s,mu,mu+0.5*s,mu+0.842*s])
            
            #print(start_date)
            #start_date=datetime.strptime(start_date,'%Y-%m-%d')
            #target_date=datetime.strptime(target_date,'%Y-%m-%d')
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
            df.loc[df.index[-1],'last_ev']=float(df['ev'][-1]).__round__(2)
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
            df.sort_index(inplace=True)
            last_row=df.iloc[-1:]
            last_row.index+=timedelta(1)
            #print(last_row.index)
            df=pd.concat([df,last_row])
            df.index=df.index.astype('str',)
            df=df.reset_index()
            df.loc[df.shape[0]-2,'down_pred_point']=down_pred_point
            df.loc[df.shape[0]-2,'up_pred_point']=up_pred_point
            df.loc[df.shape[0]-2,'pred_point']=pred_point
            df = df.astype(object).replace(np.nan, 'None')
            dataset={}
            dataset['source']=[df.columns.to_list()]
            dataset['source']
            for i,r in df.iterrows():

                row=r.to_list()
                dataset['source'].append(row)
            #j=json.dumps(dataset)
        return dataset
    def one_work(self,data):
        mysql=self.mysql
        code=self.code
        
        try:
            dataset=self.gen_dataset(data,self.m)
            #print(dataset)
            return dataset
        except Exception as e:

            #raise Exception
            logger.error('had exception during process data: %s'%e)
            return False
    
def fetch_all_position():
    try:
        host='localhost'
        user='Local_Editor'
        password='QuantumGalaxy'
        mysql=MYSQL(host,user,password,'web_server')
        issues=mysql.read_query('select name,code from ev_band_info where status=1')
        r=[]
        for issue in issues:
            code=issue[1]
            summary=issue[0]
            r.append((code,summary))
        return r
    except:
        from atlassian import Jira
        #print(self.code)
        jira = Jira(
            url='https://research.quantumgalaxy.cn/',
            username='wangzhilin',
            password='wangzhilin')
        issues=jira.jql('project = POSITION and cf[11723] in(胸有成竹,应该能用,不太确定)')
        issues=issues['issues']
        r=[]
        for issue in issues:
            #print(issue)
            code=issue['fields']['customfield_10201']
            summary=issue['fields']['summary']
            r.append((code,summary))
        print('get ev_band index from jira')
    return r
        