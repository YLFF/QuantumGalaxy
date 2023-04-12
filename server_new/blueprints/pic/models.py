import requests
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.mysql import MYSQL
from datetime import date
import pandas as pd
import numpy as np
from QGI.feishu import *

def find_file(token,id):
    import os
    root_dir=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\pic\static'
    file_dir=os.path.join(root_dir,token)
    files=os.listdir(file_dir)
    file_name=None
    for file in files:
        name=os.path.splitext(file)
        if name[0]==id:
            file_name=name[0]+name[1]
    return  file_dir,file_name
   
