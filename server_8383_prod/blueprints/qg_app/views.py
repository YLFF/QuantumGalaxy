import json
from flask import request,redirect,jsonify,make_response,render_template
from . import qgapp
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *
from QGI.neoapi import Neo4j
from .models import *

from flask import session
import logging
feishu=FeishuAPI()
userlogger=user_logger('user_log')


#@qgapp.route('/liveEditor',methods=['GET'])
def live_editor():
    return render_template('liveEditor.html')


#@qgapp.route('/set_cookie',methods=['POST','GET'])
def set_cookie():
    resp = make_response('success')

    resp.set_cookie("name", session.get('name'),domain='.scope.quantumgalaxy.cn')
    

    return resp

#@qgapp.route('/bitable_query',methods=['GET','POST'])
def bitable_query():
    args=request.args
    print('bitable_query:"%s"'%args)
    bitapp_token=args.get('bitapp_token')
    graph_name=args.get('graph_name')
    r=bitable_works(bitapp_token,graph_name)
    r['user_name']=session.get('name')
    r['graph_name']=graph_name
    r['bitapp_name']=bitable_name(bitapp_token)
    #return json.dumps(r)
    return jsonify(r)

@qgapp.route('daily_index',methods=['POST','GET'])
def fetch_daily_index():
    url='http://82.156.248.152:81/fs/fold_meta?token=fldcnEdjJdrG4RNcWYfLMKZmAFd'
    r=requests.get('http://82.156.248.152:81/fs/fold_meta?token=fldcnEdjJdrG4RNcWYfLMKZmAFd')
    print(r.json())
    return r.json()
#@qgapp.route('from_cypher/day_market',methods=['POST','GET'])
def fetch_day_market():
    cypher=day_market_cypher()
    dic=build_neo_data(model='cypher',cypher=cypher)
    dic['model']='cypher'
    return json.dumps(dic)
#@qgapp.route('from_cypher/season_market',methods=['POST','GET'])
def fetch_season_market():
    cypher=season_market_cypher()
    dic=build_neo_data(model='cypher',cypher=cypher)
    dic['model']='cypher'
    return json.dumps(dic)
@qgapp.route('from_cypher/filter',methods=['POST','GET'])
def cypher_filter():
    req=request.args
    if req.get('item') and req.get('threshold'):
        try:
            cypher=build_filter_cypher(item=req.get('item'),threshold=req.get('threshold'))
            dic=build_neo_data(model='cypher',cypher=cypher)
            dic['model']='cypher'
            userlogger.info('people:"%s" from "%s" model "filter" query:"%s"'%(session.get('name'),session.get('login_source','unknown'),(req.get('item')+'   '+req.get('threshold'))))
            return json.dumps(dic)
        except:
            cypher=build_filter_cypher()
            dic=build_neo_data(model='cypher',cypher=cypher)
            dic['model']='cypher'
            return json.dumps(dic)

    else:return jsonify(model='error',nodes=[],links=[])
@qgapp.route('from_cypher/path',methods=["POST","GET"])
def cypher_path():
    req=request.args

    '''
    match p=shortestPath((n1)-[*..6]-(n2)) where n1.name='钢材' and n2.name='不钢' return length(p)
    match p=(n1)-[*0..6]-(n2) where n1.name='高炉炼铁' and n2.name='钢材' return nodes(p) as n
    match p=(n1)-[*0..6]-(n2) where n1.name='高炉炼铁' and n2.name='钢材' return relationships(p) as r'''
    pass


@qgapp.route('/login_status',methods=['POST','GET'])
def user_info():
    if session['login_status']:
        return jsonify({'login_status':1,'user':session.get('name'),'user_source':session.get('login_source')})
    else:
        return jsonify(login_status=0)
@qgapp.route('/login_status',methods=['POST','GET'])
def return_user_info():
    return jsonify(user_name=session.get('name'),is_login=session.get('login_status'),user_source=session.get('login_source'))
@qgapp.route('/atlas_query',methods=['POST','GET'])
def cypher2json():
    req=request.args
    print(req)
    #默认展开一层节点，可选2层
    tiers=req.get('tiers',1)
    print(tiers)
    exact_kw=req.get('exact_kw',None)
    vague_kw=req.get('vague_kw',None)

    code_kw=req.get('code_kw',None)
    if code_kw:
        code_kw=code_kw.upper()
    expand_kws=req.getlist('expand_kws[]',None)
    path_kws=req.getlist('path_kws[]',None)
    if exact_kw and exact_kw!='':

        kw=exact_kw
        dic=build_neo_data(exact_kw,'exact',tiers=tiers)
        dic['model']='exact_kw'
    elif vague_kw and vague_kw!='':
        kw=vague_kw
        print(tiers)
        dic=build_neo_data(vague_kw,'vague',tiers=tiers)
        dic['model']='vague_kw'
    elif code_kw and code_kw!='':
        kw=code_kw
        dic=build_neo_data(code_kw,'code',tiers=tiers)
        dic['model']='code_kw'
    elif expand_kws and expand_kws[0]!='':
        print('im here')
        print(expand_kws[0])
        dic={'model':'expand_kws'}
        kw=expand_kws
        for kw in expand_kws:
            onedic=build_neo_data(kw,'exact',tiers=tiers)
            dic.update(onedic)
    elif path_kws and len(path_kws)==2:
        kw=str(path_kws)
        dic=build_neo_data(model='path',name=path_kws,tiers=tiers)
        dic['model']='path'
    else:
        print('no valid kw detected! get param as :""%s'%req)
        return json.dumps('no valid kw detected! get param as :""%s'%req)
    userlogger.info('people:"%s" from "%s" model "%s" query:"%s"'%(session.get('name'),session.get('login_source','unknown'),dic.get('model','unknown'),str(kw)))
    try:
        
        print(dic)
        return json.dumps(dic)
    except Exception as e:
        userlogger.error('error: %s'%e)
        
        return json.dumps({'model':'error','nodes':[],'links':[]})
