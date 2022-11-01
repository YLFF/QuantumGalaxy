from .feishu_auth import fetch_access_token, fetch_auth_page,fetch_user_info
from . import login




from flask import render_template,redirect,abort,request,session,url_for
import json 




@login.route('/')
def feishu_login():
    if session.get('name'):
        return redirect(url_for('index'))
    else:
        

        url=fetch_auth_page()

        return redirect(url)
@login.route('/feishu_login')
def auth():
    #print(request.args)
    state=request.args.get('state',None)
    #print(state)
    if state=='0':
        code=request.args.get('code',None)
        token=fetch_access_token(code)
        user_info=fetch_user_info(token)
        session['name']=user_info['name']
        session['avatar_url']=user_info['avatar_url']
        #session['code']=code
        session['login_status']=True
        return redirect(url_for('index'))
    else:
        return redirect('/login')
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
