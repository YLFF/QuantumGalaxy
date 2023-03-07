from .feishu_auth import fetch_access_token, fetch_auth_page,fetch_user_info
from . import login
from datetime import datetime
from base64 import b64decode,b64encode


from .mysql_auth import my_auth
from flask import render_template,redirect,abort,request,session,url_for,Response
import json 
from .wx_auth import WX_APP_SECRET,WX_CORD_ID,wx_fetch_access_token,wx_get_user_info,get_external_user
import logging
from utils import get_logger,get_mysql
logger=get_logger('login logger',)
def login_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(
        r"E:\wangzhilin\QuantumGalaxy\server_8383_prod\logs\login.log",
        'a',
        encoding='utf-8')
    fh.setLevel(logging.INFO)
    #ch = logging.StreamHandler()
    #ch.setLevel(chlevel)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    #ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
login_logger=login_logger('login logger')
@login.route('/')
def feishu_login():
    if session.get('login_status'):
        return redirect(url_for('index'))
    else:
        

        url=fetch_auth_page()

        return redirect(url)
@login.route('/feishu_login')
def auth():
    #print('init!')
    #print(request.args)
    state=request.args.get('state',None)
    #print(state)
    if state=='0':
        #print('here!!')
        code=request.args.get('code',None)
        token=fetch_access_token(code)
        user_info=fetch_user_info(token)
        session['name']=user_info['name']
        session['avatar_url']=user_info['avatar_url']
        #login.logger.info('login as a')
        session['login_source']='feishu'
        logger.info('login as %s from source: %s'%(session['name'],session['login_source']))
        #session['code']=code
        
        session['login_status']=True
        return redirect(url_for('index'))
    else:
        return redirect('/login')
@login.route('/my_login',methods=['POST','GET'])
def wx_login1():
    if request.method=='get':
        '''微信登陆跳转'''
        args=request.args
        if args.get('secret'):
            #session['name']=args['name']
            s=args.get('secret')
            
            mysql=get_mysql('web_server')
            r=mysql.read_query('select stamp from login_stamp where stamp="%s" and used=0'%s)
            if len(r)>0:
                mysql.write_query('update login_stamp set used=1 where stamp="%s"'%s)
                s=r[0][0]
                s=s.encode('utf-8')
                timestamp,name,source=b64decode(s).decode("utf-8").split('+')
                #login.logger.info('login as a')
                print('s:"%s"'%s)
                #session['code']=code
                session['name']=name
                session['login_source']=source
                session['login_status']=True
                logger.info('login as %s'%session['name'])
                
                return redirect('http://82.156.248.152:8383/')
            else:
                return 'login info expired!'
        else:
                return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=ww236240b9fd8dc95f&redirect_uri=http%3A//scope.quantumgalaxy.cn/login/wx_login&response_type=code&scope=snsapi_base&state=0&agentid=wx#wechat_redirect')  
    else:
        '''内嵌数据库登陆'''
        form=request.form
        userinfo=form.get('userinfo','nothing')
        mysql=get_mysql('web_server')
        user_secret=b64encode(userinfo.encode('utf8')).decode('utf-8')
        user=my_auth(user_secret)
        if user:
            session['name']=user
            session['login_source']='mysql'
            session['login_status']=True
            logger.info('login as %s from source: %s'%(session['name'],session['login_source']))
            return redirect(url_for('index'))
        else:
            session.clear()
            return render_template('abort.html')
            #abort(Response('您似乎没有进入星图系统的权限，请与本公司人员联系'))
        #try:print('form:"%s"'%request.form)
        #except:pass
        #try:print('json:"%s"'%request.get_json())
        #except:pass
@login.route('/wx_login')
def wx_login():
    '''内部有userid，外部客户有external_userid'''
    '''url=https://open.weixin.qq.com/connect/oauth2/authorize?appid=ww236240b9fd8dc95f&redirect_uri=http%3A//scope.quantumgalaxy.cn&response_type=code&scope=snsapi_base&state=0&agentid=wx#wechat_redirect'''
    state=request.args.get('state',None)
    if state=='0':
        code=request.args.get('code',None)
        #print('code="%s"'%code)
        #return code
        userinfo=wx_get_user_info(code).json()
        print('userinfo:"%s"'%userinfo)
        if userinfo['errcode']==0:
            cookies=request.cookies
            print('cookies:"%s"'%cookies)
            if userinfo.get('userid',None):
                info=userinfo.get('userid','unknown user')
                session['login_source']='wx_internal'
                session['name']=info
            elif userinfo.get('external_userid'):
                external_info=get_external_user(userinfo.get('external_userid')).json()
                session['login_source']='wx_external'
                session['name']=external_info['external_contact']['name']
                session['follow_name']=''
                #r.json()['external_contact']
                '''跟进人信息，未入库暂时省略'''
                #for follow in external_info['follow_user']:
                #    session['followname']+=follow['userid']+','
                #session['followname']=session['followname'][:-1]
            else:
                '''非内部/非客户'''
                session.clear()
                return render_template('abort.html')
                #abort(Response('您似乎没有进入星图系统的权限，请与本公司人员联系'))
            session['login_status']=True
            logger.info('login as %s from source: %s'%(session['name'],session['login_source']))
            
            print('session:"%s"'%session)
            return redirect(url_for('index'))
            #print('wx_redirect url:"%s"'%url_for('index',_external=True))
            
            #rep=Response(redirect(url_for('index')))
            #rep.set_cookie()

            '''制作密钥'''
            '''
            user=session['name']
            source=session['login_source']
            timestr=datetime.now().timestamp()
            secret=b64encode((str(timestr)+'+'+user+'+'+source).encode("utf-8"))
            secret=secret.decode('utf-8')
            #print(secret)
            mysql=get_mysql('web_server')
            mysql.write_query('insert into login_stamp (stamp) values("%s")'%secret)
            mysql.close()
            return redirect('http://82.156.248.152:8383/login/my_login?secret=%s'%(secret))'''
        else:
            return json.dumps(userinfo)
    else:
        return redirect('https://open.weixin.qq.com/connect/oauth2/authorize?appid=ww236240b9fd8dc95f&redirect_uri=http%3A//scope.quantumgalaxy.cn/login/wx_login&response_type=code&scope=snsapi_base&state=0&agentid=wx#wechat_redirect')  
@login.route('/login_state')
def check_login_state():
    s=session.get('login_status')
    if not s:
        s='no'
    else:
        s='yes'
    return s
@login.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
