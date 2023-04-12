import sys
import logging

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
from config import args
from models import *
from flask_cors import CORS

from jira import JIRA

from flask import request, render_template, redirect, abort, url_for,session,Response,jsonify
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

@app.route('/index',methods=['post','get'])
def index():
    if request.method=='get':
        return Response(render_template('index.html'))
    else:

        question=request.form.get('question',None)
        if question:
            gptapp=GPTAPP()
            r=gptapp.work(question)
            return jsonify(r)
        else:return Response(render_template('index.html'))
@app.route('/test_chat',methods=['post'])
def test_chat():
    content=json.loads(request.json)
    content=content.get('message','完美世界')
    req={'id': '9999', 'messages': [{'role': 'user', 'content':content }], 'company_code': []}
    res=chat_api_handler(req)
    return jsonify(res)

@app.route('/chat',methods=['post'])
def chat():
    if request.get_json():
        req=request.get_json()
        #print(req)
        if type(req)==dict:
            pass
        else:
            req=json.loads(req)
    else:
        print('data')
        print(request.data)
        print('form')
        print(request.form)
        return jsonify(code=-3,msg="didn't get valid json parameters")
    print(req)
    res=chat_api_handler(req)
    return jsonify(res)
@app.route('/test')
def test():
    print('test')
    try:
        r=requests.get('http://43.153.23.232:81/test',timeout=(5, 10))
        r=r.json()
        if r['code']==0:
            r['msg']='ALL OK'
    except:
        r={'code':-2,'msg':'US SERVER DOWN'}
    print(r)
    return jsonify(r)
@app.route('/test1',methods=['get'])
def test1():
    import time
    time.sleep(5)
    return 'good'
@app.route('/')
@app.route('/limited_chat',methods=['post'])
def limited_chat():
    if request.get_json():
        req=request.get_json()
        print(req)
        if type(req)==dict:
            pass
        else:
            req=json.loads(req)
    target=req.get('target',{'code':'002353.SZ'})
    code=target.get('code','002353.SZ')
    id=req.get('id','unknown')
    credits=1
    model='chat'
    #code=request.args.get('code','0941.HK')
    r=company_intro(code)
    message=[{'content':r.pop('res'),'role':'assistant'}]
    
    return jsonify(id=id,total_tokens=r['tokens'],credits=credits,model=model,message=message)
def main():
    print('QGGPT SERVER')
    print('srart with config:')
    print(args)
    #print(type(args.debug))
    #print(args.debug==True)
    if args.debug:
        app.run(host='0.0.0.0', port=8484,debug=True)
    else:
        app.run(host='0.0.0.0', port=84)
if __name__=='__main__':
    main()
