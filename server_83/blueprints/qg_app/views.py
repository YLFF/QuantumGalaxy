import json
from flask import request, redirect, jsonify, make_response
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

feishu = FeishuAPI()
userlogger = user_logger('user_log')


@qgapp.route('/set_cookie', methods=['POST', 'GET'])
def set_cookie():
    resp = make_response('success')

    resp.set_cookie("name", session.get('name'), domain='anewdomain')

    return resp


@qgapp.route('/login_status', methods=['POST', 'GET'])
def user_info():
    if session['login_status']:
        return jsonify({'login_status': 1, 'user': session.get('name')})
    else:
        return jsonify({'login_status': 0, 'user': 'noone'})


@qgapp.route('/atlas_query', methods=['POST', 'GET'])
def cypher2json():
    req = request.args
    print(req)

    exact_kw = req.get('exact_kw', None)
    vague_kw = req.get('vague_kw', None)

    code_kw = req.get('code_kw', None)
    expand_kws = req.getlist('expand_kws[]', None)

    if exact_kw and exact_kw != '':

        kw = exact_kw
        dic = build_neo_data(exact_kw, 'exact')
        dic['model'] = 'exact_kw'
    elif vague_kw and vague_kw != '':
        kw = vague_kw
        dic = build_neo_data(vague_kw, 'vague')
        dic['model'] = 'vague_kw'
    elif code_kw and code_kw != '':
        kw = code_kw
        dic = build_neo_data(code_kw, 'code')
        dic['model'] = 'code_kw'
    elif expand_kws and expand_kws[0] != '':
        print('im here')
        print(expand_kws[0])
        dic = {'model': 'expand_kws'}
        kw = expand_kws
        for kw in expand_kws:
            onedic = build_neo_data(kw, 'exact')
            dic.update(onedic)
    else:
        print('no valid kw detected! get param as :""%s' % req)
        return json.dumps('no valid kw detected! get param as :""%s' % req)
    userlogger.info('people:"%s" query:"%s"' % (session.get('name'), str(kw)))
    try:

        print(dic)
        return json.dumps(dic)
    except Exception as e:
        userlogger.error('error: %s' % e)
        return json.dumps({'model': 'error', 'nodes': [], 'links': []})


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
    try:
        challenge = req['challenge']
        print(req['challenge'])
        return json.dumps({'challenge': req['challenge']})
    except:
        sender = req['event']['sender']['sender_id']['open_id']
        content = req['event']['message']['content']

        #if content.startwith('chat')
        #print(content)
        #chat_url=url_for('.chatgpt.chat')
        chat_url = 'http://172.21.0.14:81/chatgpt/chat/'
        print(chat_url)
        res_content, res_code = requests.post(
            url=chat_url,
            data={
                "session_token":
                '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',
                "prompt": content
            })
        res_content = res_content.decode()
        print(res_content)

        feishu.send_msg(res_content, sender)
    return json.dumps({'code': 200}, ensure_ascii=False)
