import requests
'''用户点开微信应用主页（https://open.weixin.qq.com/connect/oauth2/authorize?appid=ww236240b9fd8dc95f&redirect_uri=http%3A//scope.qua
ntumgalaxy.cn/&response_type=code&scope=snsapi_base&state=0&agentid=wx#wechat_redirect）
后，会直接经过oauth,带用户code和state=0参数带到重定向页面
用code可以获取用户信息'''
WX_CORD_ID='ww236240b9fd8dc95f'
WX_APP_SECRET='uSRAoEVWKTuFTW-yPAgTjTHPVOFdW30qvrf76NHTHfc'
def wx_fetch_access_token():
    url='https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    req=requests.get(url,params={'corpid':WX_CORD_ID,'corpsecret':WX_APP_SECRET})
    #print(req.json())
    token=req.json()['access_token']
    return token
def wx_get_user_info(code):
    token=wx_fetch_access_token()
    code=code
    url='https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token=%s&code=%s'%(token,code)
    r=requests.get(url)
    return r
    '''eg info：
    	{"UserId":"WangZhiLin","DeviceId":"56f55e05-e4e6-498e-bf8c-f44183233c45","errcode":0,"errmsg":"ok"}
        '''
def get_external_user(exid):
    url='https://qyapi.weixin.qq.com/cgi-bin/externalcontact/get?access_token=%s&external_userid=%s'%(fetch_access_token(),exid)
    r=requests.get(url)
    '''{'errcode': 0,
 'errmsg': 'ok',
 'external_contact': {'external_userid': 'wmbJDbTgAATs2yCKKTDGIR4hXsytRr3w',
  'name': '张凌宇 量子星河',
  'type': 1,
  'avatar': 'http://wx.qlogo.cn/mmhead/XzhF92tBceyvAw47iceKNqGvsw2tVEZxibGp1cmvxexU1yly3qnlm5gw/0',
  'gender': 0},
 'follow_user': [{'userid': 'ZhangLingYu',
   'remark': '张凌宇 量子星河',
   'description': '',
   'createtime': 1676361133,
   'tags': [],
   'remark_mobiles': ['18610621302'],
   'add_way': 2,
   'oper_userid': 'ZhangLingYu'}]}'''
    return r