from . import backbone
#from .models import ev_band_check,data_process

from .models import *

from flask import render_template,redirect,abort,url_for,request
import json 

@backbone.route('/example',methods=['GET'])
    
def return_test_backbone():
    return render_template('backbone1.html')

@backbone.route('/')
@backbone.route('/index')
def backbone_fp():
        name=request.args.get('name',None)
        if not name:
                r=get_backbone_index()
                

                return render_template('backbone_index.html',names=r)
        else:
                return redirect(url_for('backbone.return_backbone',name=name))

@backbone.route('/<name>',methods=['GET'])
def return_backbone(name):
        try:
                b=Backbone2JS(name)

                b._get_backbone_from_neo()
                js=b.gen_js()
                name=json.dumps(name)
                js=json.dumps(js)
        except:
                return('查询出错')
        return render_template('backbone.html',json=js,name=name)