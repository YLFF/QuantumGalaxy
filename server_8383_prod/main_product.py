import json
import logging
import sys
from datetime import date, datetime, timedelta

from flask import (Flask, abort, redirect, render_template, request, session,
                   url_for,Response)
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
from config import args

'''flask logger'''

from flask import has_request_context, request
from flask.logging import default_handler


ALLOWED_IPS = ['82.156', '127.0.0', '172.21.0', '123.58.10','36.112.76','221.216.208.84','61.149.70']
app = Flask(__name__)
#
cors=CORS(app,origins='*',allow_headers='x-requested-with,content-type',supports_credentials=False)
#app.config['SERVER_NAME'] = 'scope.quantumgalaxy.cn'
app.config["JSON_AS_ASCII"] = False
app.config['SCHEDULER_API_ENABLED'] = True
app.config["SECRET_KEY"] = "core-quantumgalaxy"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_FILE_DIR']=r'E:\wangzhilin\QuantumGalaxy\server_83\cookies'
#app.config['SESSION_COOKIE_DOMAIN']='adomain'
Session(app)
from flask.sessions import SessionInterface


#app.logger.removeHandler(default_handler)

userlogger=get_logger('user log')
@app.before_request
def user_logger():
        name=session.get('name',None)
        source=session.get('login_source','unknown')
        if name:
                userlogger.info('"%s" from  source: "%s"'%(name,source))
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
@comment.before_request
def check_auth():
        if session.get('login_status',None):
                
                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
                
            
        else:
                return redirect(url_for('login.feishu_login'))

@qgapp.before_request
def check_auth():
        print('qgappsession:"%s"'%session)
        if session.get('login_status',None):
                
                name=session.get('name',None)
                #print('status:%s'%session.get('login_status',None))
                #print('code:%s'%code)
                
            
        else:
                
                #pass
                return redirect(url_for('login.feishu_login'))

#@login.after_request
def after_request(res):
    from flask import make_response
    resp = make_response(res)
    #resp.set_cookie(key='domain',value='test',domain='http://82.156.248.152/')
    res.headers['Access-Control-Allow-Origin'] = 'http://localhost:80' 
    res.headers["Access-Control-Allow-Headers"] = "Content-Type" 
    res.headers['Access-Control-Allow-Credentials'] = 'true'  #有这个,可以cookie跨域
    #res.headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS" #对于复杂请求必须加
    return resp
    
app.register_blueprint(login)
app.register_blueprint(qgapp)
app.register_blueprint(comment)
@app.route('/index')
@app.route('/')
def index():
        if not session.get('next'):
                next=request.args.get('next',None)
                session['next']=next
        print(session)
        
        
        if session.get('login_status',None):
                if session['next']=='bitapp':
                        session.pop('next')
                        rep=redirect(url_for('qgapp.live_editor'))
                else:
                        rep=Response(render_template('index.html'))
                '''
                rep.set_cookie(key='session1',value='test',domain='quantumgalaxy.cn')
                print(rep.)
                
                FS=SessionInterface().open_session(app,session)
                print(FS)
                print(FS.get_cookie_domain(app))
                print(FS.get_cookie_path(app))'''
                return rep
                
                #return render_template('index.html')
        else:
                                
                client_ip = str(request.remote_addr)
                #print(client_ip)
                wx = False
                for ip in ['127.0.0.1','82.156.248.152']:
                        if client_ip.startswith(ip) or client_ip == ip:
                                wx=True
                if wx:
                        '''本地请求=nginx转发来的域名请求->进入内建鉴权系统'''
                        #state=request.args.get('state',None)
                        
                        #code=request.args.get('code',None)
                        #url=url_for('login.wx_login')
                        #print('rediurl:"%s"'%url)
                        ###记得删掉下面
                        #return redirect(url_for('login.feishu_login'))
                        return render_template('login.html')
                else:
                        print(session)
                        return redirect(url_for('login.feishu_login'))
    #name=session.get('name',None)
    #avatar_url=session.get('avatar_url',None)
    #return render_template('index.html',name=name,avatar_url=avatar_url)


#app.config["EXPLAIN_TEMPLATE_LOADING"] = True
@app.route("/trigger", methods=["GET", "POST"])
@app.route("/qg_dcf_fetch_curve", methods=["GET", "POST"])
def triggered():
    import pymysql
    result_string = "后台运行出错，请向Rick反应该问题"
    #tenant_token = fetch_tenant_token()
    json_str = '{"cny1y":1.9568,"cny2y":2.2494,"cny3y":2.3299,"cny5y":2.5252,"cny10y":2.7709,"usd1y":2.09,"usd2y":2.65,"usd3y":2.80,"usd5y":2.88,"usd10y":2.86}'


    codes = {
        "usd1y": "G002600769",
        "usd2y": "G002600770",
        "usd3y": "G002600771",
        "usd5y": "G002600772",
        "usd10y": "G002600774",
        "cny1y": "L001618528",
        "cny2y": "L001619976",
        "cny3y": "L001618529",
        "cny5y": "L001619472",
        "cny10y": "L001619518",
    }

    result = {}

    try:
        connection = pymysql.connect(
            host="localhost",
            user="Local_Editor",
            password="QuantumGalaxy",
            database="qgdbs"
        )

        with connection:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `value` FROM `ths_edb_data` WHERE `code`=%s ORDER BY `date` DESC LIMIT 1"
                for t, c in codes.items():
                    cursor.execute(sql, (c,))
                    result[t] = cursor.fetchone()[0]

                sql = "SELECT `date` FROM `ths_edb_data` WHERE `code`=%s ORDER BY `date` DESC LIMIT 1"
                cursor.execute(sql, (codes["cny1y"],))
                result["cnydate"] = "%s" % cursor.fetchone()[0]

                sql = "SELECT `date` FROM `ths_edb_data` WHERE `code`=%s ORDER BY `date` DESC LIMIT 1"
                cursor.execute(sql, (codes["usd1y"],))
                result["usddate"] = "%s" % cursor.fetchone()[0]

        json_str = json.dumps(result)
    except Exception as e:
        print(e)

    return Response(json_str, mimetype='applicaition/json')

logger.init_app(app)



def main():
        print(args)
        if args.debug:
                print('debug=True')
                app.run(host='0.0.0.0',port=83,debug=True)
        else:
                print('debug=False')
                app.run(host='0.0.0.0',port=8383)

main()