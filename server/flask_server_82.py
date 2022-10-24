#from crypt import methods
import sys
import logging
from apps import assistant

sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
import re
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
feishu=FeishuAPI()
def get_logger():
    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        "E:/wangzhilin/QuantumGalaxy/logs/flask_server.log",
        'a',
        encoding='utf-8')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


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


from jira import JIRA

jira = JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('bot2', "jira_bot2"))
logger = get_logger()
from flask import request, render_template, redirect, abort, url_for,session
import json
from flask import Flask
from datetime import datetime, timedelta

ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84']
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
'''
@app.before_request
def limit_remote_addr():

    client_ip = str(request.remote_addr)
    print(client_ip)
    valid = False
    for ip in ALLOWED_IPS:
        if client_ip.startswith(ip) or client_ip == ip:
            valid = True
            logger.info(client_ip)
            break
    if not valid:
        abort(403)
'''

from feishu_auth.auth import fetch_auth_page


@app.route('/login')
def feishu_login():


        url=fetch_auth_page()

        return redirect(url)
@app.route('/feishu_login')
def auth():
    print(request.args)
    state=request.args.get('state',None)
    print(state)
    if state=='0':
        session['login_status']=True
        return redirect('/head')
    else:
        return redirect('/login')
@app.route('/login_state')
def check_login_state():
    s=session.get('login_status')
    if not s:
        s='no'
    else:
        s='yes'
    return s



@app.route("/head")
def hello_world():
    return "<p>Hello, This is QG's vaisual terminal!</p>"


@app.route('/add_indicator', methods=['GET', 'POST'])
def load_new_indicator(test=False):
    if test:
        return request.args
    if request.method == 'POST':
        payload = request.get_json()
        issueid = payload['issue']['id']
        issue = jira.issue(issueid)
        logger.info('issue name: %s' % issue.fields.__dict__['summary'])
        res_code, res_msg = QGCodeLoader(issue).load()

        res = 'res code : ' + str(res_code) + '  ' + res_msg
        jira.add_comment(issue, res)
        logger.critical(res + '\n')
        if res_code >= 0:
            jira.transition_issue(issue, '11')

        return json.dumps({'code': 0}, ensure_ascii=False)

    elif request.method == 'GET':
        return json.dumps({'msg': 'not allowed method!'})


@app.route('/update_indicator')
def update_indicator():

    issueid = request.args['issueid']
    logger.info('get issue id %s' % issueid)
    issue = jira.issue(issueid)
    logger.info('issue name: %s' % issue.fields.__dict__['summary'])
    res_code, res_msg = QGIndicatorUpdater(issue).update()


@app.route('/event', methods=['POST'])
def receive_message():
    req = request.get_json()
    '''
        'schema': '2.0',
        'header': {
            'event_id': '64320ead7859c354749098e9f81addc1',
            'token': 'Xs2kL847Q2tsnyBRISQtXee4xK81kYRX',
            'create_time': '1660728160810',
            'event_type': 'im.message.receive_v1',
            'tenant_key': '2c4fafa0738f175e',
            'app_id': 'cli_a10497168d3f1013'
        },
        'event': {
            'message': {
                'chat_id': 'oc_b983a0741cc9917f919a30824193c419',
                'chat_type': 'p2p',
                'content': '{"text":"你好"}',
                'create_time': '1660728160585',
                'message_id': 'om_90b454341b884e17b3756076d2545dc0',
                'message_type': 'text'
            },
            'sender': {
                'sender_id': {
                    'open_id': 'ou_e32afa3ec16eae9f334d27c02c037259',
                    'union_id': 'on_be8deecd121bf3ced909870cacbbb729',
                    'user_id': 'g14b6af7'
                },
                'sender_type': 'user',
                'tenant_key': '2c4fafa0738f175e'
            }
        }
    }

    sender=req['event']['sender']['sender_id']['open_id']
    print(req['event']['message']['content'])
    feishu.send_msg('自动回复',sender)
    return json.dumps({'code': 200}, ensure_ascii=False)
    '''
    try:
        challenge=req['challenge']
        print(req['challenge'])
        return json.dumps({'challenge':req['challenge']})
    except:
        sender=req['event']['sender']['sender_id']['open_id']
        content=req['event']['message']['content']
        #print(content)
        res_content=assistant(content,sender)
        print(res_content)
        
        feishu.send_msg(res_content,sender)
    return json.dumps({'code': 200}, ensure_ascii=False)


@app.route('/backbone',methods=['GET'])
    
def return_test_backbone():
    return render_template('backbone.html')





from ev_band.ev_band_app import ev_band_check,data_process
@app.route('/ev_band/',methods=['GET'])
def ev_band_fp():
    if session.get('login_status'):
        return(return_ev_band('688063.SH'))
    else:
        return redirect('/login')


@app.route('/ev_band/example',methods=['GET'])
def example():
    if session.get('login_status'):
        f=open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\example-li.o.json','r')
        j=json.loads(f.read())
        summary='理想汽车   LI.O'
        return render_template('ev_band-example-li.o.html',summary=summary,json=json.dumps(j))
    else:
        return redirect('/login')



@app.route('/ev_band/<code>',methods=['GET'])
def return_ev_band(code):
    if session.get('login_status'):
        code=ev_band_check(code)
        j,summary=data_process(code)
        if not code or not j:
            return render_template('ev_band1.html')
            
        else:
            #html_editor(code)
            
            #f= open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\688063.SH1.json', 'r')
            #content = f.read()
            a = json.loads(j)
            dataset=[a,]
            #print(j)
            #print(dataset)
            return render_template('ev_band.html',summary=summary,json=json.dumps(dataset))
    else:
        return redirect('/login')


app.run(host='0.0.0.0', port=82)
