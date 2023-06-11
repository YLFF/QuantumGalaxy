from . import live_editor
from flask import redirect,render_template,make_response,request,jsonify,session
from .models import *
@live_editor.route('/liveEditor',methods=['GET'])
def live_editor_index():
    return render_template('liveEditor.html')



@live_editor.route('/bitable_query',methods=['GET','POST'])
def bitable_query():
    args=request.args
    print('bitable_query:"%s"'%args)
    bitapp_token=args.get('bitapp_token')
    graph_name=args.get('graph_name')
    expand_ids=args.get('expand_ids')
    if expand_ids:
        expand_ids=expand_ids.split(',')
    #expand_ids=args.getlist('expand_ids')
    print(f"expand:{expand_ids}")
    #print(f"expand:{args.getlist('expand_ids')}")
    #print(f"expand1:{args.get('expand_ids')}")
    r=bitable_works(bitapp_token,graph_name)
    r['user_name']=session.get('name')
    r['graph_name']=graph_name
    r['bitapp_name']=bitable_name(bitapp_token)
    print(r['bitapp_name'])
    if expand_ids:
        r=filter_result(expand_ids,r)
    #return json.dumps(r)
    return jsonify(r)