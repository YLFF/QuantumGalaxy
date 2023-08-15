import pandas as pd
import sys,os
from jira import JIRA
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL,get_mysql
from datetime import date,datetime


class ScoutHelper():
    def __init__(self,codelist) -> None:
        
        self.codelist=[code.upper() for code in codelist]
        self.__jira=None
        self.__mysql=None
        self.no_data_list=[]
        self.no_jira_list=[]
        self.result=''
        self.filename=''
        pass
    @property
    def mysql(self):

        if not hasattr(self, '__mysql') or self.__mysql is None:
                # 连接到MySQL
                self.__mysql = get_mysql('qgdbs')
                return self.__mysql
        
    @property
    def jira(self):

        if not hasattr(self, '__jira') or self.__jira is None:
                # 连接到MySQL
                self.__jira = JIRA('https://research.quantumgalaxy.cn/', basic_auth=('bot2', "jira_bot2")) 
                return self.__jira
        
            

    def fecth_ticker_data(self):
        #市值、涨幅
        #sql=f'select a.code,a.date,a.market_value,change_rate_1d from ticker_data a join processed_data b on a.code=b.code where a.date=b.date and a.code={code} order by date desc limit 1'
        sql=f'''SELECT a.code, a.date, a.market_value, b.change_rate_1d\
            FROM ticker_data a\
            JOIN processed_data b ON a.code = b.code AND a.date = b.date\
            WHERE a.code IN {tuple(self.codelist)}\
            AND (\
            SELECT COUNT(*)\
            FROM ticker_data\
            WHERE code = a.code AND date > a.date\
            ) = 0'''
        ticker_data=self.mysql.read_query(sql)
        self.mysql_df=pd.DataFrame(data=ticker_data,columns=['code','date','market_value','change_1d'])
        self.mysql_df=self.mysql_df.round({'market_value':2})
        self.mysql_df['change_1d']=self.mysql_df['change_1d'].apply(lambda x: '{:.2%}'.format(x))
        tickers=[t[0] for t in ticker_data]
        for ticker in self.codelist:
            if ticker not in tickers:
                self.no_data_list.append(ticker)
        return self.mysql_df

    def fecth_jira_data(self):
        #summary,description  侦察逻辑customfield_11216
        jira_data=[]
        for code in self.codelist:
            get_issue=self.jira.search_issues(f'project = COMPSTUDY  AND issuetype = 公司研究 AND 万得代码 ={code}')
            if not get_issue:
                self.no_jira_list.append(code)
            else:
                issue=get_issue[0]
                summary,description=issue.fields.summary,issue.fields.__dict__.get('customfield_11216',None)
                
                jira_data.append((code,summary,description))
        self.jira_df=pd.DataFrame(data=jira_data,columns=['code','summary','description'])
    
    def work(self):
        self.fecth_jira_data()
        self.fecth_ticker_data()
        df=pd.merge(self.jira_df,self.mysql_df,on='code')
        if self.no_data_list:
             print('no_data_list:',self.no_data_list)
        if self.no_jira_list:
             print('no_jira_list',self.no_jira_list)
        if not (self.no_data_list and self.no_jira_list):
             print('all good')
        df['text']=None
        for i,r in df.iterrows():
            df.loc[i,'text']=f"""{r['summary']}{r['code']}({r['market_value']}亿元,{r['change_1d']})：{r['description']}"""
        
        return df
    def main(self):
        df=self.work()
        df1=pd.DataFrame(data=[['这些标的没有行情信息：',self.no_data_list],['这些标的没有jira问题：',self.no_jira_list]])
        num=df.shape[0]
        root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\scout\files'
        self.filename=datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")+'.xlsx'
        path=os.path.join(root,self.filename)
        
        
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            df1.to_excel(writer,sheet_name='Sheet2',index=False)
        self.result=f'共生成{num}条信息，有{len(self.no_data_list)}个标的没有行情信息，有{len(self.no_jira_list)}个标的没有jiraissue'
        #worksheet.write(f'A{shape+1}', '这些标的没有行情信息：'+self.no_data_list)
        #worksheet.write(f'A{shape+2}', '这些标的没有jira问题：'+self.no_jira_list)
        #print(df1)
        return df
    def __del__(self):
        if self.__mysql is not None:
            self.__mysql.close()
        