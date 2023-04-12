import json
from flask import request,redirect
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
feishu=FeishuAPI()
#from utils import chatbot
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
@qgapp.route('/event', methods=['POST'])
def receive_message():
    req = request.get_json()
    '''
        'schema': '2.0',
        'header': {
            'event_id': '64320ead7859c354749098e9f81addc1',
            'token': 'Xs2kL847Q2tsnyBRISQtXee4xK81kYRX',
            'create_time': '1660728160810',
            'event_type': 'im.message.receive_v1',
            'tenant_key': '2c4fafa0738f175e',
            'app_id': 'cli_a10497168d3f1013'
        },
        'event': {
            'message': {
                'chat_id': 'oc_b983a0741cc9917f919a30824193c419',
                'chat_type': 'p2p',
                'content': '{"text":"你好"}',
                'create_time': '1660728160585',
                'message_id': 'om_90b454341b884e17b3756076d2545dc0',
                'message_type': 'text'
            },
            'sender': {
                'sender_id': {
                    'open_id': 'ou_e32afa3ec16eae9f334d27c02c037259',
                    'union_id': 'on_be8deecd121bf3ced909870cacbbb729',
                    'user_id': 'g14b6af7'
                },
                'sender_type': 'user',
                'tenant_key': '2c4fafa0738f175e'
            }
        }
    }

    sender=req['event']['sender']['sender_id']['open_id']
    print(req['event']['message']['content'])
    feishu.send_msg('自动回复',sender)
    return json.dumps({'code': 200}, ensure_ascii=False)
    '''
    if req.get('challenge'):
        challenge=req['challenge']
        print(req['challenge'])
        return json.dumps({'challenge':req['challenge']})
    else:
        sender=req['event']['sender']['sender_id']['open_id']
        event_id=req['header']['event_id']
        
        if write_check_id(event_id):
            if not sender in ['ou_e32afa3ec16eae9f334d27c02c037259','ou_bdb8583689f98ddc96484441b8477975','ou_6055b4f9ede3b6d4a3ac9f303b17971c','ou_6fe1b9026fc41be0414c723f4a1d174b','ou_5257a5c4f845c57e45a054f275e2f9b2']:
                #ou_bdb8583689f98ddc96484441b8477975
                
                #print()
                content=req['event']['message']['content']
                #print(len(content))
                chat_id=req['event']['message']['chat_id']

                #if content.startwith('chat')
                #print(content)
                #chat_url=url_for('.chatgpt.chat')
                res_content=xm2_checker(content)
                r=feishu.send_msg(res_content,sender)
                #print(r)

            else:
                try:
                    msg=req['event']['message']['content']
                    #print(msg)
                    try:
                        l=eval(msg)
                        print(l)
                        l1=eval(l.get('text'))
                        if type(l1)==list:
                            print(l1)
                            r=requests.post('http://43.153.23.232:81/cust_chat',json=json.dumps({'messages':l1}))
                        else:
                            r=requests.post('http://43.153.23.232:81/chat',json=json.dumps({'message':msg}))
                    except:
                        r=requests.post('http://43.153.23.232:81/chat',json=json.dumps({'message':msg}))
                    
                    content=r.json()['res']
                    r=feishu.send_msg(content,sender)
                    
                except Exception as e:
                    content='had problem in bot:"%s"'%e
                    r=feishu.send_msg(content,sender)
                
                '''
                try:

                    
                    prompt = req['event']['message']['content']
                    #{'text:"abcdefg"                  #
                   
                    a=json.loads(prompt)
                    prompt=a['text']
                    if prompt=='reset':
                        print('?')
                        chatbot.reset_chat()
                        content='reset chat'
                    else:
                        content = ""

                        for data in chatbot.ask(
                        prompt
                        ):
                            content = data["message"]
                    print(content)
                    r=feishu.send_msg(content,sender)
                    
                except Exception as e:
                    content='had problem in bot:"%s"'%e
                    r=feishu.send_msg(content,sender)
                    '''
        else:
                print('overtimed requset')    
    return json.dumps({'code': 200}, ensure_ascii=False)
