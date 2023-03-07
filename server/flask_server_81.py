#from crypt import methods
import sys
import logging
from apps import assistant
from blueprints.fsback import fsback
from blueprints.research_robot import robot
#from blueprints.chatgpt import chatgpt
from blueprints.qg_app import qgapp
from blueprints.bitable_app import bitapp
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
from models import *
from flask_cors import CORS
from utils import chatbot
from jira import JIRA

jira = JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('bot2', "jira_bot2"))

from flask import request, render_template, redirect, abort, url_for,session
import json
from flask import Flask
from datetime import datetime, timedelta

ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84','61.149.70','123.118.184.143','54.86.50']
app = Flask(__name__)
cors = CORS(app, resources={r"/qgapp/*": {"origins": "*"}})
app.config["JSON_AS_ASCII"] = False
app.config['SCHEDULER_API_ENABLED'] = True
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
from log import Logger,get_logger

main_logger = Logger()

@app.before_request
def limit_remote_addr():

    client_ip = str(request.remote_addr)
    print(client_ip)
    valid = False
    for ip in ALLOWED_IPS:
        if client_ip.startswith(ip) or client_ip == ip:
            valid = True
            #logger.info(client_ip)
            break
    if not valid:
        abort(403)

logger=get_logger('main')

app.register_blueprint(bitapp)
app.register_blueprint(fsback)
app.register_blueprint(robot)
app.register_blueprint(qgapp)
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



@app.route('/backbone',methods=['GET'])
    
def return_test_backbone():
    return render_template('backbone.html')



@app.route('/invest_pers/insert')
def insert_perspective():
    issueid=request.args.get('issueid',None)
    if issueid:
        try:
            r=invest_per_work(issue_id=issueid)

            logger.info(r)
            r='good'
            
        except:
            r='had error when handle issueid:%s to insert a perspective'%issueid
            logger.error(r)
    else:
        r='did not receive an issueid'
        logger.error()
    return r

from ev_band.ev_band_app import ev_band_check,data_process
@app.route('/ev_band/',methods=['GET'])
def ev_band_fp():

        return(return_ev_band('688063.SH'))



@app.route('/ev_band/example',methods=['GET'])
def example():

        f=open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\example-li.o.json','r')
        j=json.loads(f.read())
        summary='理想汽车   LI.O'
        return render_template('ev_band-example-li.o.html',summary=summary,json=json.dumps(j))




@app.route('/ev_band/<code>',methods=['GET'])
def return_ev_band(code):

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

from aps import scheduler

scheduler.init_app(app)
main_logger.init_app(app)
scheduler.start()
app.run(host='0.0.0.0', port=81)