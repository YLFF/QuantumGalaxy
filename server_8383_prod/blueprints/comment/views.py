
from . import comment

from utils import get_mysql


from flask import render_template,redirect,abort,request,session,url_for,jsonify
import json 
from datetime import datetime,timedelta
import logging
from utils import get_logger
#logger=get_logger('login logger',)
#mysql=get_mysql(database='web_server')
def write_one_comment(content,linkid,nodeid):
    mysql=get_mysql('web_server')
    r=mysql.write_query('insert into atlas_comments (user_name,time,content,node_id,link_id) value \
         ("%s","%s","%s","%s","%s")'%(session.get('name'),datetime.now(),content,nodeid,linkid))
    mysql.close()
    return True

@comment.route('write_comment',methods=['POST'])
def write_comment():
    '''收到前端发来的评论 {nodeid:[], linkid:[], content: ""} 检查是否发送过快，添加时间和用户名，保存到服务器'''
    '''因为有列表，需要发json来解析'''
    '''
    print(session.items())
    print('data')
    print(request.data)
    print('form')
    print(request.form)
    print('dict')
    print(dict)
    form=json.loads(request.data)'''
    '''传来格式：MultiDict([('content', '这是一套测试用的评论！\n这是评论的第二行'), ('nodeid[]', '1'), ('nodeid[]', '2'), ('nodeid[]', '3'), ('nodeid[]', '4'), ('linkid[]', '4'), ('linkid[]', '5'), ('linkid[]', '6'), ('linkid[]', '7')])'''
    form=request.form
    #form={'content':'a test comment','nodeid':[73,886,994],'linkid':[9453,1705]}
    print(form)
    if not (form.get('content') and (form.get('node_name[]') or form.get('link_name[]'))):
        res_content='表单填写有误，正文/节点id/边id不完整'
        linkid=[]
        nodeid=[]
        content=form.get('content')
        write_one_comment(content,linkid,nodeid)
        res_code=1
    else:
        content,linkid,nodeid=form['content'],form.getlist('link_name[]'),form.getlist('node_name[]')
        if not(type(content)==str and type(linkid)==list and type(nodeid)==list):
            res_content='表单填写有误，正文/节点id/边id数据结构有不正确'
            linkid=[]
            nodeid=[]
            content=form.get('content')
            write_one_comment(content,linkid,nodeid)
            res_code=2
        else:
            if session.get('last_comment_time'):
                print(session['last_comment_time'])
                delta=datetime.now()-session['last_comment_time']
                if delta<timedelta(seconds=30):
                    res_content='提交评论过于频繁，请至少间隔30秒'
                    res_code=3
                else:
                    write_one_comment(content,linkid,nodeid)
                    res_content='提交评论成功'
                    res_code=0
                    session['last_comment_time']=datetime.now()
            else:
                session['last_comment_time']=datetime.now()
                print(session['last_comment_time'])
                write_one_comment(content,linkid,nodeid)
                res_content='提交评论成功'
                res_code=0
                print(session.items())
    print(res_content)
    return jsonify(code=res_code,content=res_content)
@comment.route('/fetch_comment',methods=['GET','POST'])
def fetch_comment():
    '''获取特定位置的节点'''
    '''需要调数据库结构，可以方便取得特定id位置的评论'''
    
    pass
