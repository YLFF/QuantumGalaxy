import sys
import logging

sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
import re
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np

def get_logger():
    logger = logging.getLogger('logger')
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

logger = get_logger()
from flask import request, render_template, redirect, abort
import json
from flask import Flask

ALLOWED_IPS = ['82.156.232', '127.0.0', '172.21.0', '123.58.10','1.203.157','32.112.76']

ROOT_PATH=r'E:\wangzhilin\QuantumGalaxy\backbone\server'
#STATIC_PATH=r'E:\wangzhilin\\QuantumGalaxy\backbone\server'
import os
STATIC_PATH=os.path.join(ROOT_PATH,'static')

app = Flask(__name__,static_folder=STATIC_PATH,root_path=ROOT_PATH)


@app.before_request
def limit_remote_addr():
    
    client_ip = str(request.remote_addr)
    print(client_ip)
    valid = False
    for ip in ALLOWED_IPS:
        if client_ip.startswith(ip) or client_ip == ip:
            valid = True
            logger.info(client_ip)
            break
    if not valid:
    
        abort(403)


@app.route("/head")
def hello_world():
    return "<p>Hello, This is QG backbone monitor</p>"



@app.route('/test', methods=['GET'],)
def return_test_backbone():
    return render_template('index.html')


app.run(host='0.0.0.0', port=82)
