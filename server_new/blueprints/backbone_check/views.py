from . import backbone_check
#from .models import ev_band_check,data_process

from .models import xml2graph_worker

from flask import render_template,redirect,abort,url_for,request,session,g,send_from_directory,make_response,jsonify
import json 
'''在首页输入名称和字符串并跳转，进行检查后到确认页面向用户展示解析结果，进行确认后把相关解析结果存储到后端'''
def pop_session_attr(name):
    if session.get(name,None):
        attr=session.pop(name)
        return attr
    else:
        return None
@backbone_check.route('/',methods=['POST','GET'])
#@backbone_check.route('/index')
def backbone_checker():
    
    backbonename=request.form.get('name',None)
    raw=request.form.get('graph',None)
    #print('len:"%s"'%len(raw))
    

    if not backbonename:

            return render_template('backbone_check.html')
    else:
            print(len(raw))
            print('clear session..........')
            for name in ['backbone_name','backbone_raw','check_result','graph_data']:
                pop_session_attr(name)
            
            session['backbone_name']=backbonename
            #raw
            session['check_result'],session['graph_data']=xml2graph_worker(raw,session['backbone_name'])
            print('write raw data')
            #print(session.keys())
            return redirect(url_for('backbone_check.xml2graph_page'))

@backbone_check.route('/xml2graph')
def xml2graph_page():
    #try:
        #print('before processing')
        #print(session.keys())
        
        
        #print('after processing')
        #print(session['backbone_name'])
        #print(session.keys())
        #print(session['check_result'])
        return redirect(url_for('backbone_check.confirm'))
    #except Exception as e:
    #   print(e)
    #   return '解析出错'
    
@backbone_check.route('/confirm')
def confirm():
    
    #from QGI.feishu
    #print(session['backbone_name'])
    #print(session['graph_data'])
    
    #session.pop('backbone_raw')
    #name=session.pop('backbone_name')
    try:
        result=session.pop('check_result')
        print('comfirming')
        print(session.keys())
        return render_template('check_result.html',name=session['backbone_name'],result=result)
    except Exception as e:
        print(e)
        return redirect(url_for('backbone_check.backbone_checker'))
@backbone_check.route('/raw')
def raw():
    return jsonify(session['graph_data'])
@backbone_check.route('/scout_doc',methods=["GET"])
def scout_doc():
    import pandas as pd
    from os import path
    data=session.get('graph_data')
    r=''
    for k,v in data['vertex'].items():
        if v['category']=='Company':
            r+="%s（%s）"%(v['name'],v['code'])
    

    
    return r
@backbone_check.route('/download_csv/node',methods=["GET"])
def download_node_csv():
    import pandas as pd
    from os import path
    data=session.get('graph_data')
    df=pd.DataFrame(data=data['vertex'])
    df=df.T
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\backbone_check\files'
    file_name='%s_node.csv'%session.get('backbone_name')
    file_path=path.join(root,file_name)
    df.to_csv(file_path)
    return send_from_directory(root, file_name, as_attachment=True)
@backbone_check.route('/download_csv/indicator',methods=["GET"])
def download_indicator_csv():
    import pandas as pd
    from os import path
    data=session.get('graph_data')
    df=pd.DataFrame(data=data['indicator'])
    df=df.T
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\backbone_check\files'
    file_name='%s_indicator.csv'%session.get('backbone_name')
    file_path=path.join(root,file_name)
    df.to_csv(file_path)
    return send_from_directory(root, file_name, as_attachment=True)

@backbone_check.route('/download_csv/link',methods=["GET"])
def download_link_csv():
    import pandas as pd
    from os import path
    data=session.get('graph_data')
    df=pd.DataFrame(data=data['edge'])
    df=df.T
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\backbone_check\files'
    file_name='%s_link.csv'%session.get('backbone_name')
    file_path=path.join(root,file_name)
    df.to_csv(file_path)
    return send_from_directory(root, file_name, as_attachment=True)
@backbone_check.route('/save_graph')
def save_graph():
    import json
    data=session.get('graph_data')
    jsondata=json.dumps(data)
    name=session.get('backbone_name')
    from os import path
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\backbone_check\files'
    file='%s.json'%name
    filepath=path.join(root,file)
    f=open(filepath,'w')
    f.write(jsondata)
    f.close()
    print('saved to file:%s'%filepath)
    #print(session.keys())

    return 'success'
    