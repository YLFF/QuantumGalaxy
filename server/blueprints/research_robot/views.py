# -*- coding: utf-8 -*-  

from . import robot,robot_auth
import sys
import io
from flask import request,redirect,url_for
import json
from .models import app_send_msg,build_card_content,routine_pointview_list
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.feishu import text_group_msg
#情景想象小组
chat_id0='oc_e783012cb60666418c19084bceb6e4eb'
debug_chat_id='oc_7d319ba3f1b5b738fdc4ca455898af63'
from log import get_logger
robotlogger=get_logger('robot_log')
'''
def setup_io():
    sys.stdout = sys.__stdout__ = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = sys.__stderr__ = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)
setup_io()
'''



@robot.route('/send_message/<payload>',methods=['POST','GET'])
def send_message(payload):
    
    try:
        #title=payload['title']
        msg=payload['msg']
    except:
        return 'no  msg given'
    title=payload.get('title',None)
    if not title:
      
       title=''
    receive_type=payload.get('receive_type',None)
    if not receive_type:
      
       receive_type='chat_id'
    msg_type=payload.get('msg_type',None)
    if not msg_type:
        msg_type='interactive'
    
    receive_id=payload.get('receive_id',None)
    #print('receive_id:%s'%receive_id)
    if not receive_id:
        receive_id=chat_id0
    #print(receive_id)
    #receive_id=debug_chat_id
    robotlogger.info('send msg title:"%s" to id:"%s"'%(title,receive_id))
    if msg_type=='text':
        content=json.dumps({"text": msg})
    elif msg_type=='interactive':
        content=build_card_content(title,msg)
    r=app_send_msg(content=content,receive_type=receive_type,receive_id=receive_id,msg_type=msg_type)
    #print('\n\n%s\n\n'%receive_id)
    #return content
    return r
    #return content
def write_check_id(id):
    from QGI.mysql import MYSQL
    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    database='web_server'
    mysql=MYSQL(host,user,password,database)
    r=mysql.read_query('select * from event_list where event_id="%s"'%id)
    if r:
        mysql.close()
        return False
    else:
        mysql.write_query('INSERT INTO event_list (event_id) VALUES ("%s")'%id)
        mysql.close()
        return True

'''
an example for a event

{'schema': '2.0', 
'header': {'event_id': 'a04e86b385c15ffc6020ac4e8b000aab', 'token': '1Lle7bWWM7UtclBZGra9Rge0W7qi3XA3', 'create_time': '1670393757714', 'event_type': 'im.message.receive_v1', 'tenant_key': '2c4fafa0738f175e', 'app_id': 'cli_a114f87decf9d00b'},
 'event': {'message': {'chat_id': 'oc_7d319ba3f1b5b738fdc4ca455898af63', 'chat_type': 'group', 
    'content': '{"text":"@_user_1 yang"}', 
    'create_time': '1670393757449',
     'mentions': [{'id': {'open_id': 'ou_3da662f22130ad29770c5798b3eb803a', 'union_id': 'on_6553b97605d797cbaf787eb68fe23e6f', 'user_id': ''}, 'key': '@_user_1', 'name': '!研究助理Robot', 'tenant_key': '2c4fafa0738f175e'}], 
     'message_id': 'om_c7bc8aacf8436e6c920995d1dd664f38', 
     'message_type': 'text'}, 
    'sender': {'sender_id': {'open_id': 'ou_7beef07b6a99720064308a70e9536a35', 'union_id': 'on_be8deecd121bf3ced909870cacbbb729', 'user_id': 'g14b6af7'}, 'sender_type': 'user', 'tenant_key': '2c4fafa0738f175e'}}
 }
'''
@robot.route('/event',methods=['GET','POST'])
def analysis_event():

    from jira import JIRA
    jira = JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('bot2','jira_bot2'))
    j=request.get_json()
    content=j['event']['message']['content']
    content=eval(content)['text']
    if '@_all' in content:
        msg='"@_all" in content, ignore this msg'
        robotlogger.info(msg)
        return msg,200
    #print('get event from feishu')
    #print(j)
    event_id=j['header']['event_id']
    chat_id=j['event']['message']['chat_id']
    sender_id=j['event']['sender']['sender_id']['open_id']
    print(chat_id)
    if write_check_id(event_id):
            #print(j['event']['sender'])
        robotlogger.info('get a good request:\ncontent:%s\nchat_id:%s\nsender_id:%s\n'%(content,chat_id,sender_id))

        if j['header']['app_id']=='cli_a114f87decf9d00b':
            try:
                import re
                #name=content.split(' ')[1]
                name=re.sub('@_user_[0-9]','',content)
                name=name.replace(' ','')

                jql='project in (WORLDEPICSTUDY, COMPSTUDY) AND issuetype = 研究任务 AND status in (合并中, Done) AND summary ~ %s ORDER BY cf[10203] DESC'%name
                issues=jira.search_issues(jql)
            except :
                text_group_msg('jql不合法，获取到关键字为%s'%content) 
                return 'no issue found',200
            
            if issues:
                issueid=issues[0].key
            else:
                msg='没有找到研究成果,请检查关键字："%s"'%name
                send_message(payload={'title':'失败了！','msg':msg,'receive_id':chat_id,'msg_type':'text'})
                #text_group_msg('event页面没有查询到对应的issue，获取到关键字为%s'%name) 
                return 'no issue found',200
            url='http://82.156.248.152:81/fs/check_file?issueid=%s&receive_id=%s'%(issueid,chat_id)
            #print(url)
            import requests
            robotlogger.info('get an issue:"%s"from event analysis, goto checkfile'%issueid)
            r=requests.get(url=url)
            #print(r)
            #text_group_msg('非重复事件，event_id:%s'%(event_id))
        return 'good',200
    else:
        #text_group_msg('重复事件，搜索语句：%s，event_id:%s'%(content,event_id))
        return 'good but overtimes',200


@robot.route('/test/send_list',methods=['GET','POST'])
def test_send_list(id='oc_7d319ba3f1b5b738fdc4ca455898af63'):
    routine_pointview_list(receive_id=id)
    return 'good',200