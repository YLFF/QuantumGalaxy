
from . import ev_band
from .models import ev_band_check,Code2JS,fetch_all_position,New_band



from flask import render_template,redirect,abort,session, template_rendered,url_for,request
import json 




@ev_band.route('/',methods=['GET'])
def redi_index():
        return redirect(url_for('ev_band.ev_band_fp'))
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
        band_info,js,model=worker.work() 
        #j -> list
        #j,summary=data_process(code)
        if  not js:
            return '查询出错'
            
        else:
            #html_editor(code)
            if model=='xn':
                    model='M=Xn+A模式'
            else:
                    model='M=X模式'
            num=len(js)
            #f= open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\688063.SH1.json', 'r')
            #content = f.read()
            js = json.dumps(js)
            band_info=json.dumps(band_info)
            model=json.dumps(model)
            #print(j)
            #print(dataset)
            return render_template('ev_band.html',summary=summary,json=js,num=num,info=band_info,model=model)

from datetime import datetime

def draw_ev_band(code,summary,data):
        
        print(code,summary,data)
        worker=New_band(code,data)
        band_info,js,model=worker.work() 
        num=len(js)
        #f= open(r'E:\wangzhilin\QuantumGalaxy\server\static\ev_band\688063.SH1.json', 'r')
        #content = f.read()
        js = json.dumps(js)
        band_info=json.dumps(band_info)
        model=json.dumps(model)
        return render_template('ev_band.html',summary=summary,json=js,num=num,info=band_info,model=model)

@ev_band.route('/draw_band',methods=['GET','POST'])
def draw_band():
        if session['name'] in ['王之霖','张凌宇']:
                code=request.args.get('code',None)
                if not code:
                        return render_template('ev_band_draw.html')
                else:
                        try:
                                code=request.args.get('code',None)
                                name=request.args.get('name',None)
                                summary=code +' '+name
                                data=[{'pc':request.args.get('pc',None),'po':request.args.get('po',None),'xc':request.args.get('xc',None),'xo':request.args.get('xo',None),
                                'start_date':datetime.strptime(request.args.get('start',None),'%Y-%m-%d'),'target_date':datetime.strptime(request.args.get('target',None),'%Y-%m-%d'),}]
                                return draw_ev_band(code,summary,data)
                        except:
                                return '输入有误，请返回'
        else:
                return "YOU'VE REACHED A FORBIDDEN AREA!"