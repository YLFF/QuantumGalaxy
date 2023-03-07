


import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.feishu import *

from flask import render_template,redirect,abort,request,session,url_for
import json 
from urllib import parse
import logging
from . import global_var
def get_logger(name):
    logger = logging.getLogger(name)
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
logger=get_logger('login logger',)


def fetch_auth_page(redirect_url=None,state=0):
    
    app_id='cli_a10497168d3f1013'
    
    #'redirect_uri':r'http%3A%2F%2F82.156.248.152%3A82%2Ffeishu_login',
    redirect_uri='http%3A%2F%2F82.156.248.152%3A81%2Ffs%2Frefresh'
    
    state=0
    url=f'https://open.feishu.cn/open-apis/authen/v1/index?redirect_uri={redirect_uri}&app_id={app_id}&state={state}'
    return url
def fetch_app_token():
    url='https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    headers={'content-type':'application/json'}
    data={
  "app_id": "cli_a10497168d3f1013",
  "app_secret": "iFiFkOUqetraRTVCfZlbhdmxFWNkwg2h"
}

    r=base_fetch_func(url,headers,data=json.dumps(data),method='post')
    
    if r['code']==0:
        return r['app_access_token']
    else:
        return r
def fetch_user_token(code):
    url='https://open.feishu.cn/open-apis/authen/v1/access_token'
    
    #print(app_token)
    headers={
            'content-type': 'application/json; charset=utf-8',
            "Authorization": "Bearer " +fetch_app_token()
        }
    
    data={'grant_type':"authorization_code",
    'code':code}
    r=base_fetch_func(url,headers,data=json.dumps(data))
    
    
    return r
def refresh_user_token(code):
    url='https://open.feishu.cn/open-apis/authen/v1/refresh_access_token'
    
    headers={
            'content-type': 'application/json; charset=utf-8',
            "Authorization": "Bearer " +fetch_app_token()
        }
    data={'grant_type':"refresh_token",
    'refresh_token':code}
    r=base_fetch_func(url,headers,data=json.dumps(data))
    
    
    return r
def fetch_folder_children(fld_token,page_token=None):
    url='https://open.feishu.cn/open-apis/drive/v1/files'
    headers={'Authorization':'Bearer '+global_var.get_value('user_access_token')}
    #print(fld_token)
    params={'page_size':200,
        'folder_token':fld_token}
    if page_token:
        params['page_token']=page_token
    r=base_fetch_func(url,headers,params=params,method='get')
    return r

def fetch_folder_meta(fld_token):
    '''can't get info if the user(token belongs) has no permission'''
    url='https://open.feishu.cn/open-apis/drive/explorer/v2/folder/'+fld_token+'/meta'
    headers={'Authorization':'Bearer '+global_var.get_value('user_access_token'),'Content-Type':"application/json; charset=utf-8"}
    r=base_fetch_func(url,headers=headers,method='get')
    
    return r