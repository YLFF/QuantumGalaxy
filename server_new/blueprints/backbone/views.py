from . import backbone
#from .models import ev_band_check,data_process

from .models import *

from flask import render_template,redirect,abort,url_for,request
import json 

@backbone.route('/',methods=['GET'])
    
def return_test_backbone():
    return render_template('backbone.html')


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
    return render_template('backbone.html')