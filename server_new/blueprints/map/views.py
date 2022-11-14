from . import map


import json

from flask import render_template,redirect,abort,session, template_rendered,url_for,request
from .models import get_data

@map.route('/',methods=['GET'])
def get_map():
        dataset_p,name2pinyin,image_dict=get_data()
        name2pinyin=json.dumps(name2pinyin)
        image_dict=json.dumps(image_dict)
        dataset_p=json.dumps(dataset_p)
        return render_template('map.html',name2pinyin=name2pinyin,image_dict=image_dict,dataset_p=dataset_p)
@map.route('/1',methods=['GET'])
def get_map1():
        return render_template('map1.html')