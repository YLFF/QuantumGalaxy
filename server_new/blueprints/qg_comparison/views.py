from . import cmpr
#from .models import ev_band_check,data_process

from .models import work,conflicts2text,get_graph_data,get_xml_data,internal_check

from flask import render_template,redirect,abort,url_for,request,session,g,send_from_directory,make_response,jsonify
import json 
'''在首页输入名称和字符串并跳转，进行检查后到确认页面向用户展示解析结果，进行确认后把相关解析结果存储到后端'''

    
@cmpr.route('/',methods=['POST','GET'])
#@backbone_check.route('/index')
def cmpr_index():
    print(request.form)
    bitapp_id=request.form.get('bitapp_id',None)
    xml_raw=request.form.get('graph',None)
    #print('len:"%s"'%len(raw))
    region=request.form.get('region',None) #'sth' or ''
    rough_backbone='粗骨干图' if request.form.get('rough') else None#'on' or None
    except_ind=request.form.get('except_ind',None)
    except_cop=request.form.get('except_cop',None)
    

    if not bitapp_id:

            return render_template('cmpr.html')
    else:
            xml_data=get_xml_data(xml_raw)
            session['xml']=xml_data
            graph_data=get_graph_data(bitapp_id,region,rough_backbone,except_cop,except_ind)
            #raw
            #session['check_result'],session['graph_data']=xml2graph_worker(raw,session['backbone_name'])
            try:
                internal_text=internal_check(bitapp_id)
            except Exception as e:
                internal_text=''
                print('exception when internalcheck:',e)
            print('write raw data')
            r=work(xml_data,graph_data)
            if r['code']==0:
                session['raw']=r['res']
            #print(session.keys())
                return render_template('cmpr_result.html',conflicts=conflicts2text(r['res']),raw=r['res'],internal=internal_text)
            else:
                  return jsonify(r)
@cmpr.route('/download',methods=["GET"])
def download():
    import pandas as pd
    from os import path
    data=session.get('xml')
    df=pd.DataFrame(data=data['vertex']).T[['name','x','y']]

    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\qg_comparison\files'
    file_name='%s_comparison.csv'%session.get('name','qg')
    file_path=path.join(root,file_name)
    df.to_csv(file_path)
    return send_from_directory(root, file_name, as_attachment=True)
@cmpr.route('/raw',methods=['GET'])
def raw():
     return jsonify(session.get('raw'))