from . import graph2xml
from flask import redirect,render_template,make_response,request,jsonify,session,send_from_directory,url_for
from .models import *

@graph2xml.route('/',methods=['GET'])
def graph2xml_index():
    
    

    
    
    return render_template('graph2xml.html')

@graph2xml.route('/result',methods=['POST'])
def result():
    print(request.form)
    bitapp_id=request.form.get('id')
    region=request.form.get('region') #'sth' or ''
    rough_backbone='粗骨干图' if request.form.get('rough') else None#'on' or None
    except_ind=request.form.get('except_ind')
    except_cop=request.form.get('except_cop')

    raw=bitable_works(bitapp_id,subgraph_name=rough_backbone)
    if raw['code']==0:
        if region.strip():
            raw=filter_region(raw,region.strip())
        #print(type(rew))
        if except_cop:
            raw=filter_category(raw,'企业')
        if except_ind:
            raw=filter_category(raw,'指标')
        session['result']=raw
        session['id']=bitapp_id
        
        res=string_work(raw)
        return render_template('xml_result.html',result=res,bitapp_id=bitapp_id,region=region,rough=True if rough_backbone else False,except_cop=True if except_cop else False,except_ind=True if except_ind else False)
    else:
        print(raw)
        return jsonify('bitapp error')





@graph2xml.route('/download',methods=["GET"])
def download():
    import pandas as pd
    from os import path
    data=session.get('result')
    id=session.get("id")
    print(id)
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\graph2xml\files'
    file_name=f'{id}.txt'
    file_path=path.join(root,file_name)
    with open(file_path,'w',encoding='utf-8') as f:
        f.write(data)
    return send_from_directory(root, file_name, as_attachment=True)
@graph2xml.route('/work',methods=['GET','POST'])
def work():
    #args=request.args
    #bitapp_id=args.get('id')
    req=json.loads(request.get_json())
    bitapp_id=req.get('bitapp_id','')
    
    region=req.get('region') #'sth' or ''
    rough_backbone='粗骨干图' if req.get('rough_backbone') else None#'on' or None
    except_ind=req.get('except_ind')
    except_cop=req.get('except_cop')

    raw=bitable_works(bitapp_id,subgraph_name=rough_backbone)
    if raw['code']==0:
        if region.strip():
            raw=filter_region(raw,region.strip())
        #print(type(rew))
        if except_cop:
            raw=filter_category(raw,'企业')
        if except_ind:
            raw=filter_category(raw,'指标')




    result=raw
    #print(args)
    
    if result:
        

        #print(result)
        return jsonify(code=0,bitapp_id=bitapp_id,result=result)
    else:
        return jsonify(code=-1)
    
