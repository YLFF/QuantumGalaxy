from flask import Flask
 
from flask_apscheduler import APScheduler
 
import datetime
 

from utils import get_mysql,get_logger
import logging
logger=get_logger('ev_band.aps',chlevel=logging.INFO)
from .models import Code2JS
from atlassian import Jira

def reset_mysql():

#print(self.code)
    mysql=get_mysql(database='web_server')
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
    mysql.write_query('update ev_band_info set status=0')
    mysql.write_many_query(sql='insert into ev_band_info (code,name,status) values (%s,%s,1) ON DUPLICATE KEY UPDATE status=1',val=r)

def fetch_data():
    mysql=get_mysql(database='web_server')
    jira = Jira(
        url='https://research.quantumgalaxy.cn/',
        username='wangzhilin',
        password='wangzhilin')
    codes=mysql.read_query('select code from ev_band_info where status=1')
    for c in codes:
        c=c[0]
        worker=Code2JS(c)
        history=worker.split_ev_band(worker.clean_data(worker.find_issue()))
        for h in history:
            mysql.write_query("insert ignore into ev_band_data (code,start_date,target_date,pc,xc,xo,po) values ('%s','%s','%s',%s,%s,%s,%s)"%(c,*(h.values()) ))

def ev_band_routine():
    '''从jira到mysql.web_server的快照，将持仓公司信息从jira获取，处理到走廊的形式保存，
    减少对jira的访问'''
    reset_mysql()
    fetch_data()
if __name__=='__main__':

    ev_band_routine()