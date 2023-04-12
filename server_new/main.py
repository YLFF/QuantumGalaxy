import json
import logging
import sys
from datetime import date, datetime, timedelta

from flask import (Flask, abort, redirect, render_template, request, session,jsonify,
                   url_for)
from flask_session import Session
from blueprints.map import map
from blueprints.backbone_check import backbone_check
from blueprints.ev_band import ev_band
from blueprints.backbone import backbone
from blueprints.live_editor import live_editor
from blueprints.login import login
from blueprints.pic import pic
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re
from flask_apscheduler import APScheduler
import numpy as np
import pandas as pd
from jira import JIRA
from QGI.feishu import *
from QGI.mysql import MYSQL
from utils import get_logger,openai_test
logger = get_logger(__name__)
'''
jira = JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('bot2', "jira_bot2"))#指标机器人
'''

feishu=FeishuAPI()

'''flask logger'''

from flask import has_request_context, request
from flask.logging import default_handler



ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84','61.149.70']
app = Flask(__name__)
app.config['SCHEDULER_API_ENABLED']=True
app.config["JSON_AS_ASCII"] = False
app.config['SCHEDULER_API_ENABLED'] = True
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_FILE_DIR']=r'E:\wangzhilin\QuantumGalaxy\server_new\cookies'
Session(app)

#app.logger.removeHandler(default_handler)

userlogger=get_logger('user log')
@app.before_request
def user_logger():
        name=session.get('name',None)
        if name:
                userlogger.info(name)

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
@backbone_check.before_request
def check_auth():
        if session.get('login_status',None):
                
                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
                
            
        else:
                return redirect(url_for('login.feishu_login'))

@map.before_request
def check_auth():
        if session.get('login_status',None):

                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
            
        else:
                return redirect(url_for('login.feishu_login'))

@ev_band.before_request
def check_auth():
        if session.get('login_status',None):

                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
            
        else:
                return redirect(url_for('login.feishu_login'))
@backbone.before_request
@live_editor.before_request
@pic.before_request
def check_auth():
        if session.get('login_status',None):

                code=session.get('code',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
            
        else:
                return redirect(url_for('login.feishu_login'))
app.register_blueprint(login)
app.register_blueprint(backbone)
app.register_blueprint(ev_band)
app.register_blueprint(backbone_check)
app.register_blueprint(live_editor)
app.register_blueprint(map)
app.register_blueprint(pic)
from log import Logger

logger = Logger()

'''
from flask import current_app
@app.route('/favicon.ico')
def get_fav():
    print(__name__)
    return current_app.send_static_file('favicon.ico')'''

@app.route('/')
def index():
    
    name=session.get('name',None)
    avatar_url=session.get('avatar_url',None)
    return render_template('index.html',name=name,avatar_url=avatar_url)

@app.route('/openai_status',methods=['get'])
def openai_status():
        r=openai_test()
        return jsonify(r)

#app.config["EXPLAIN_TEMPLATE_LOADING"] = True

from aps import scheduler

scheduler.init_app(app)

scheduler.start()

logger.init_app(app)

app.run(host='0.0.0.0', port=82,debug=True)

