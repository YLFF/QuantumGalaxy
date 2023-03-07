import json
import logging
import sys
from datetime import date, datetime, timedelta

from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for)
from flask_session import Session
from blueprints.qg_app import qgapp
from blueprints.login import login
from blueprints.comment import comment
sys.path.append('E:\wangzhilin\QuantumGalaxy')
import re
from flask_apscheduler import APScheduler
import numpy as np
import pandas as pd
from jira import JIRA
from QGI.feishu import *
from QGI.mysql import MYSQL
from utils import get_logger
from flask_cors import CORS
logger = get_logger(__name__)
import argparse


'''flask logger'''

from flask import has_request_context, request
from flask.logging import default_handler



ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84','61.149.70']
app = Flask(__name__)
cors = CORS(app, resources={r"/qgapp/*": {"origins": "*"}})
app.config["JSON_AS_ASCII"] = False
app.config['SCHEDULER_API_ENABLED'] = True
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_FILE_DIR']=r'E:\wangzhilin\QuantumGalaxy\server_83\cookies'
Session(app)

#app.logger.removeHandler(default_handler)

userlogger=get_logger('user log')
@app.before_request
def user_logger():
        name=session.get('name',None)
        if name:
                userlogger.info(name)
#@app.before_request
def check_auth():
        if session.get('login_status',None):
                
                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
                
            
        else:
                return redirect(url_for('login.feishu_login'))


from log import Logger

logger = Logger()

'''
from flask import current_app
@app.route('/favicon.ico')
def get_fav():
    print(__name__)
    return current_app.send_static_file('favicon.ico')'''


@qgapp.before_request
def check_auth():
        if session.get('login_status',None):
                
                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
                
            
        else:
                return redirect(url_for('login.feishu_login'))
app.register_blueprint(login)
app.register_blueprint(qgapp)
app.register_blueprint(comment)
@app.route('/')
def index():
        if session.get('login_status',None):
                return render_template('index1.html')
        else:
                return redirect(url_for('login.feishu_login'))
    #name=session.get('name',None)
    #avatar_url=session.get('avatar_url',None)
    #return render_template('index.html',name=name,avatar_url=avatar_url)


#app.config["EXPLAIN_TEMPLATE_LOADING"] = True


logger.init_app(app)



def main():

                #print('debug=False')
                app.run(host='0.0.0.0',port=8383,debug=True)

main()