
from . import ev_band
from .models import ev_band_check,data_process,Code2JS,fetch_all_position



from flask import render_template,redirect,abort,session, template_rendered,url_for,request
import json 





@ev_band.route('/index',methods=['GET'])
def ev_band_fp():
        code=request.args.get('code',None)
        if not code:
                r=fetch_all_position()
                

                return render_template('ev_band_index.html',info=r)
        else:
                return redirect(url_for('ev_band.return_ev_band',code=code))



@ev_band.route('/example',methods=['GET'])
def example():

        f=open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\example-li.o.json','r')
        j=json.loads(f.read())
        summary='理想汽车   LI.O'
        return render_template('ev_band-example-li.o.html',summary=summary,json=json.dumps(j))




@ev_band.route('/<code>',methods=['GET'])
def return_ev_band(code):

        code=ev_band_check(code)
        worker=Code2JS(code)
        summary=worker.fetch_summary()
        band_info,js=worker.work() 
        #j -> list
        #j,summary=data_process(code)
        if  not js:
            return '查询出错'
            
        else:
            #html_editor(code)
            num=len(js)
            #f= open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\688063.SH1.json', 'r')
            #content = f.read()
            js = json.dumps(js)
            band_info=json.dumps(band_info)
            #print(j)
            #print(dataset)
            return render_template('ev_band.html',summary=summary,json=js,num=num,info=band_info)
