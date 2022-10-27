import json
import logging
import sys
from datetime import date, datetime, timedelta

from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)

from blueprints.ev_band import ev_band
from blueprints.backbone import backbone
from blueprints.login import login
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re

import numpy as np
import pandas as pd
from jira import JIRA
from QGI.feishu import *
from QGI.mysql import MYSQL
from utils import get_logger
logger = get_logger(__name__)
jira = JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('bot2', "jira_bot2"))#指标机器人


feishu=FeishuAPI()





ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84','61.149.70']
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
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



@ev_band.before_request
def check_auth():
        if session.get('login_status',None):

                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
            
        else:
                return redirect(url_for('login.feishu_login'))
@backbone.before_request
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






@app.route('/')
def index():
    
    name=session.get('name',None)
    avatar_url=session.get('avatar_url',None)
    return render_template('index.html',name=name,avatar_url=avatar_url)


app.config["EXPLAIN_TEMPLATE_LOADING"] = True
app.run(host='0.0.0.0', port=82)