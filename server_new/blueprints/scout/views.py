from . import scout
from flask import redirect,render_template,make_response,request,jsonify,session,send_from_directory,url_for
from .models import *
from os import path
@scout.route('/',methods=['POST','GET'])
def scout_index():
    codetext=request.form.get('codetext',None)
    if not codetext:
        return render_template('scout.html')
    else:
        #尝试拆分成列表，执行主任务，保存excel，返回结果页
        codelist=codetext.split(',')
        if len(codelist)<2:
            return jsonify('没有找到代码，请检查输入框的内容是否满足格式')
        else:
            scouthelper=ScoutHelper(codelist)
            scouthelper.main()
            session['r']=scouthelper.result
            session['filename']=scouthelper.filename
            #print('session:'session)
            #print(session.r)
            #print(session.filename)
            return render_template("scout_result.html",result=session['r'])
        

@scout.route('/download',methods=["GET"])
def download_file():
    print(session)
    
    root=r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\scout\files'
    filename=session.get('filename')
    file_path=os.path.join(root,filename)

    return send_from_directory(root, filename, as_attachment=True)

    
    
 
