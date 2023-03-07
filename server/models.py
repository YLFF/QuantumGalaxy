import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
import logging,re


def qgcode_generator(mysql: MYSQL) -> str:
    '''generate a new code for Exxx or Cxxx  qgcode'''
    #type='e'or 'c'
    sql = 'select qg_code from qg_indicator_info where qg_code like "%s%%.QG" order by qg_code desc limit 1' % 'C'
    #print(sql)
    old = mysql.read_query(sql)
    if len(old) == 0:
        num = 1
    else:
        num = int(re.findall(r"\d+", old[0][0])[0]) + 1
    new = 'C' + str(num).zfill(5) + '.QG'

    mysql.close()

    return new


class QGCodeLoader():
    ''' 检查一个输入的qgnode信息是否合法，合法则录入qgindicatorinfo并根据分类录入下属的三个info，并录入其他相关信息；不合法则不入库并返回错误信息。
    '''
    def __init__(self, issue):
        #self.mysql=kwargs.get('mysql',False)

        self.issue = issue
        #self.issue = None

        d = issue.fields.__dict__
        self.already_had_code = d.get('customfield_11711', None)
        self.category = d['issuetype'].id  #ticker:10704 #edb:10703 c:10700
        t = d.get('customfield_11009', None)
        if t:
            self.type = t.value  #万得EDB 同花顺EDB
        else:
            self.type = None
        self.source_code = d.get('customfield_11429', None)

        self.name = d['summary']
        self.unit = d.get('customfield_11431', None)
        self.desc = d['description']
        self.status = d['status'].id  #1:开放 ：监测中

        #self.dict['qg_code']='321321.sg'

        self.result_msg = {
            0: 'good indicator',
            -101: 'bad indicator:no TYPE found for ticker indicator',
            -102: 'got wrong type for edb indicator, expect 万得 or 同花顺',
            -103: 'no UNIT found for edb indicator',
            -104: 'got invalid category',
            -201: 'already had an indicator with same qg_code',
            -202: 'got invalid code for some reason',
            -203: 'got invalid indicator name'
        }

    def _get_mysql(self):
        sql_host = 'localhost'
        sql_user = 'Local_Editor'
        sql_password = 'QuantumGalaxy'
        database = 'qgdbs'
        mysql = MYSQL(sql_host, sql_user, sql_password, database)
        return mysql

    def mysql_write(self, sql, val=None):
        mysql = self._get_mysql()
        if val:

            mysql.write_many_query(sql, val)
        else:
            mysql.write_query(sql)
        mysql.close()

    def mysql_read(self, sql):
        mysql = self._get_mysql()
        r = mysql.read_query(sql)
        mysql.close()
        return r

    def check_attr_and_find_target_db(self):
        '''verify nodeinfo is legal ,set default value if not found.
        find target 2nd datebase by category, return 2nd db string'''

        if self.category == '10704':
            self.category = 'ticker'
            try:
                self.source_code = re.findall(r"(\w+.\w+)",
                                              self.source_code)[0]
            except:
                self.result_msg[
                    -202] = 'got invalid code:%s' % self.source_code
                return False, -202
            #ticker should have a type like 'stock' or other
            '''
            if not self.dict.get('type', False):

                logger.error('no TYPE found for ticker indicator')
                return False, -101
            if self.dict.get('status', 1) != 0:
                self.dict['status'] = 1
            if not self.dict.get('summary', None):
                #set a default value for args which needed
                self.dict['summary'] = None
            if not self.dict.get('region', None):
                self.dict['region'] = None'''
            self.region = None
            self.ticker_status = 1
            self.qg_code = self.source_code
            self.business = None
            return 'ticker', 0
        elif self.category == '10703':
            self.category = 'edb'
            try:
                self.source_code = re.findall(r"(\w+\w+)", self.source_code)[0]
            except:
                self.result_msg[
                    -202] = 'got invalid code:%s' % self.source_code
                return False, -202
            if self.type == '同花顺EDB':
                self.qg_code = self.source_code + '.TH'
            elif self.type == '万得EDB':
                self.qg_code = self.source_code + '.WD'
            else:

                return False, -102

            if not self.unit:
                #logger.error('no UNIT found for edb indicator')
                return False, -103
            '''if not self.dict.get('summary', False):
                self.dict['summary'] = None'''
            #if not self.frequency:
            self.frequency = 0

            return 'edb', 0
        elif self.category == '10700':
            self.category = 'customized'
            #C类指标重启监测会发一个新的代码，怎么处理
            if self.already_had_code:
                self.qg_code = self.already_had_code
            else:
                self.qg_code = qgcode_generator(self._get_mysql())
            return 'customized', 0
        else:
            #print(self.dict['qg_code'])
            return False, -104

    def check_code(self):
        '''check if the code already in qg_indicator_info'''
        if not self.name:
            self.result_msg[-203] = 'got invalid indicator name: "%s"' % (
                self.name)
            return False, -203

        sql = 'select name from qg_indicator_info where qg_code= "%s"' % self.qg_code
        r = self.mysql_read(sql)
        if r:
            self.result_msg[
                1] = 'Already had a indicator with same qgcode :%s, which name is :%s' % (
                    self.qg_code, r[0][0])
            return True, 1
        else:
            return True, 0

    def load(self):
        #print(self.dict)
        r, result_code = self.check_attr_and_find_target_db()
        if r:
            r1, result_code = self.check_code()
            if result_code == 1:
                self.issue.update({'customfield_11711': self.qg_code})
                return 1, self.result_msg[1]
            if result_code == 0:
                sql0 = 'insert into qg_indicator_info (qg_code,name,category,description,need_process) value("%s","%s","%s","%s",%s)' % (
                    self.qg_code, self.name, self.category, self.desc,
                    self.status)

                #print(sql0)
                self.mysql_write(sql0)
                if r == 'ticker':
                    sql = 'insert into ticker_info (code,name,region,status,type,business) value ("%s","%s","%s",%s,"%s","%s")' % (
                        self.qg_code, self.name, self.region,
                        self.ticker_status, self.type, self.business)
                    #print(sql)
                    self.mysql_write(sql)
                elif r == 'edb':
                    if self.type == '同花顺EDB':

                        sql = 'insert into edb_info (code,name,ths_code,frequency,unit) value ("%s","%s","%s",%s,"%s") ' % (
                            self.qg_code, self.name, self.source_code,
                            self.frequency, self.unit)
                        #print(sql)
                    else:
                        sql = 'insert into edb_info (code,name,wind_code,frequency,unit) value ("%s","%s","%s",%s,"%s") ' % (
                            self.qg_code, self.name, self.source_code,
                            self.frequency, self.unit)
                        #print(sql)
                    self.mysql_write(sql)
                elif r == 'customized':
                    sql = 'insert into customized_info (code,name) value ("%s","%s")' % (
                        self.qg_code,
                        self.name,
                    )
                    #print(sql)
                    self.mysql_write(sql)
                #issue.update(:self.dict['code'])
                self.issue.update({'customfield_11711': self.qg_code})
                return 0, 'Success in loading indicator: "%s" to qgdbs, whose qg_code is "%s"' % (
                    self.name, self.qg_code)
            else:

                return result_code, self.result_msg[result_code]
        else:

            return result_code, self.result_msg[result_code]


class QGIndicatorUpdater(QGCodeLoader):
    def __init__(self, issue):
        super(QGIndicatorUpdater, self).__init__(issue)
        self.qg_code = 'C00001.QG'
        self.datadate = '2022-07-14'
        self.data = 50
        self.result_msg = {
            -1: "issue's status: %s does not allow updating" % self.status,
            0: 'Success in updating new data for indicator : %s' % self.qg_code
        }

    def update(self):
        if self.status != 1:
            return -1, self.result_msg[-1]
        else:
            former = self.mysql_read(
                'select value from customized_data where code like "%s" order by date desc limit 1'
                % self.qg_code)[0][0]
            chg = (self.data - former) / self.data
            logger.info('change from last data: %f' % chg)
            #issue.update()
            return 0, self.result_msg[0]


from QGI.mysql import MYSQL
from datetime import datetime,timedelta
import numpy as np
import math
def geo_mean(data,w=0.98):
    weight=[w**i for i in range(len(data))]

    
    #data=[data[-1]]
    '''加快衰减，使走廊起点离当天市值更近'''
    mean=sum(np.array(weight)*np.array(data)) / sum(weight)
    #print(raw,mean,data1,data0)
    return mean
def issue2investper2mysql(issue,mysql):




    model=issue.fields.customfield_11206
    if model:
        if model.id=='10801':
            m='x'
        elif model.id=='10800':
            m='xn'
        else:
            m='xn'
    else:
        m='xn'
    code=issue.fields.customfield_10201
    far_data=issue.fields.customfield_11441
    start_date=datetime.today()
    if m=='xn':
        if code.split('.')[1].upper()  in ['HK','SH','BJ','SZ']:
            n=mysql.read_query('select value from customized_data where code="C00002.QG" order by date desc limit 1')[0][0]
        else:
            n=mysql.read_query('select value from customized_data where code="C00004.QG" order by date desc limit 1')[0][0]

        n_near=n

        stock_data=mysql.read_query(f'select date,market_value from ticker_data where code="{code}" and date<="{start_date}" order by date desc limit 45')
        stock_data=[float(p) for (d,p) in stock_data]
        stock_data=geo_mean(stock_data)
        x_near=stock_data/n_near
    else:
        stock_data=mysql.read_query(f'select date,close_price from ticker_data where code="{code}" and date<="{start_date}" order by date desc limit 45')
        stock_data=[float(p) for (d,p) in stock_data]
        stock_data=geo_mean(stock_data)
    vol=mysql.read_query(f'select vol from processed_data where code="{code}" and date<="{start_date}" order by date desc limit 1')
    vol_near=vol[0][0]
    x_far,s_far,target_date=far_data.split(', ')
    x_far,s_far,target_date=float(x_far),float(s_far),datetime.strptime(target_date,'%Y-%m-%d')
    r=[code,start_date,target_date,x_near,n_near,vol_near,x_far,s_far]
    return r
def check_time(issue,mysql):
    code=issue.fields.customfield_10201
    r=mysql.read_query('select timestamp from invest_perspective where code="%s" order by timestamp desc limit 1'%code)
    if r:
        lasttime=r[0][0]
        delta=datetime.now()-lasttime
        return delta.seconds>=60*60*12
    else:
        return True
def invest_per_work(issue_id):

    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    from jira import JIRA
    jira = JIRA('https://research.quantumgalaxy.cn/',
                basic_auth=('wangzhilin','wangzhilin'))
    issue = jira.issue(issue_id)
    r=issue2investper2mysql(issue,mysql)
    if check_time(issue,mysql):
        res=mysql.write_many_query('insert into invest_perspective (code,start_date,target_date,x_near,n_near,vol_near,x_far,s_far) values (%s,%s,%s,%s,%s,%s,%s,%s)',val=[r])

    else:
        print( 'already has a record,  update it')
        timestamp=mysql.read_query('select timestamp from invest_perspective where code="%s" order by timestamp desc limit 1'%r[0])[0][0]
        #res=mysql.write_many_query('insert into invest_perspective (code,start_date,target_date,x_near,n_near,vol_near,x_far,s_far) values (%s,%s,%s,%s,%s,%s,%s,%s)',val=[r])
        res=mysql.write_query('update invest_perspective set code="%s",\
            start_date="%s",target_date="%s",x_near="%s",n_near="%s",vol_near="%s",x_far="%s",s_far="%s",timestamp=CURRENT_TIMESTAMP\
                where timestamp="%s" '%(*r,timestamp))
    return res
