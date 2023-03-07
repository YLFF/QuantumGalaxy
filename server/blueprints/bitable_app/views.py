# -*- coding: utf-8 -*-  

from . import bitapp
import sys
import io
from flask import request,redirect,url_for,jsonify
import json
from .models import fetch_table_records,fetch_app_tables,fetch_metadata
sys.path.append('E:\wangzhilin\QuantumGalaxy')


from log import get_logger
bitapplogger=get_logger('bitapp_log')
'''
def setup_io():
    sys.stdout = sys.__stdout__ = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = sys.__stderr__ = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)
setup_io()
'''
@bitapp.route('/',methods=['GET'])
def  fetch_bitapp_name():
    app_token=request.args.get('app_token')
    try:
        '''飞书返回类似400错误时basefetchfunc会因为没有r.json()而出错'''
        r=fetch_metadata(app_token)
        if r['code']==0:
            return jsonify(code=0,name=r['data']['app']['name'])
        else:
            return jsonify(r)
    except:return jsonify(code=-1,name='unknown',msg='飞书api调用错误，可能是文件不存在')
@bitapp.route('/tables',methods=['GET'])
def fetch_tables():
    app_token=request.args.get('app_token')
    r=fetch_app_tables(app_token)
    if r['code']==0:
        return jsonify(code=0,data=r['data']['items'])
    else:
        return jsonify(r)

@bitapp.route('/record',methods=['GET'])
def fetch_records():
    #print(request.args)
    app_token=request.args.get('app_token')
    table_id=request.args.get('table_id')
    graph_name=request.args.get('graph_name',None)
    if graph_name:

        filter='CurrentValue.[粗骨干权限]="是"' if graph_name=='粗骨干图' else 'CurrentValue.[参与子图].contains("%s")'%graph_name
    else:filter=None

    field_names=request.args.get('fields',None)
    #可行的请求例 r=fetch_table_records(app_token,table_id,filter='CurrentValue.[参与子图].contains("粗骨干图")',field_names='["节点名称","节点类型"]')
    r=fetch_table_records(app_token,table_id,filter=filter,field_names=field_names)
    #print(r)
    #print('wtf')
    if r['code']==0:
        
        more=r['data']['has_more']
        res=r['data'].get('items',[])
        print('has more:%s'%more)
        while more==True:
            page=r['data']['page_token']
            
            
            
            
            r=fetch_table_records(app_token,table_id,page_token=page,filter=graph_name,field_names=field_names)
            if r['code']==0:
                res+=r['data'].get('items')
                more=r['data']['has_more']
                print('has more:%s'%more)
            else:
                print(r)
                break
        bitapplogger.info('对%s表格%s子图找到%s记录'%(table_id,graph_name,len(res)))
        return jsonify(code=0,data=res)
    else:
        return jsonify(r)

