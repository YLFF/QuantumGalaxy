import sys

from importlib_metadata import method_cache

sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.feishu import *
from urllib import parse


def fetch_auth_page(redirect_url=None,state=0):
    url='https://passport.feishu.cn/suite/passport/oauth/authorize?'
    params={'client_id':feishu_auth['app_id'],
    
    #'redirect_uri':r'http%3A%2F%2F82.156.248.152%3A82%2Ffeishu_login',
    'redirect_uri':r'http%3A%2F%2F82.156.248.152%3A82%2Flogin%2Ffeishu_login',
    'response_type':'code',
    'state':'0'
    
    }
    if state!=0:
        params['state']=state

    if redirect_url:
        redirect_url=parse.quote(redirect_url)
        params['redirect_uri']=redirect_url
    for k,v in params.items():
        url+=k+'='+v+'&'
    return url[:-1]
    #r=base_fetch_func(url=url,headers=None,params=params,method='get')
    #https://passport.feishu.cn/suite/passport/oauth/authorize?client_id=CLIENT_ID&redirect_uri=http%3A%2F%2F127.0.0.1%3A8888&response_type=code&state=state123456

#print(parse.quote('www.你好.com'))

def fetch_access_token(code):
    url='https://passport.feishu.cn/suite/passport/oauth/token'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
            
        }
    data={
    "grant_type": "authorization_code",
    "code": code,
    'client_id':feishu_auth['app_id'],
    'client_secret':feishu_auth['app_secret'],
    'redirect_uri':r'http://82.156.248.152:82/login/feishu_login',
    }
    r=base_fetch_func(url,headers,method='post',data=data)
    token=r['access_token']
    #name=
    return token
def fetch_user_info(token):
    url='https://passport.feishu.cn/suite/passport/oauth/userinfo'
    headers={'Authorization':	'Bearer  %s'%token}
    r=base_fetch_func(url,headers,method='get')
    print(r)
    return r