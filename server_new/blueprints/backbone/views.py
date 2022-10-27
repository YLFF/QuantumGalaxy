from . import backbone
#from .models import ev_band_check,data_process



from flask import render_template,redirect,abort
import json 

@backbone.route('/',methods=['GET'])
    
def return_test_backbone():
    return render_template('backbone.html')

