
from . import ev_band
from .models import ev_band_check,Code2JS,fetch_all_position,New_band,New_band2


from flask import abort
from datetime import datetime
from flask import render_template,redirect,abort,session, template_rendered,url_for,request,jsonify
import json 


from utils import get_logger
logger=get_logger('ev_band logger',)

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
def draw_band_index(code='000300.SH'):
        '''return a front page with default code as 000300.SH
        '''
        worker=New_band2('000300.SH',{'start_date':'2023-01-01','target_date':'2023-12-31','start_upper':5100,'start_lower':4500,'target_upper':4500,'target_lower':3500,'name':'示例：沪深300'})
        r=worker.work(model='price')
        info=r.pop('info')
        code=r.pop('code')
        info['code']=code
        print(len(r['source']))
        info=[info]
        data=[r]
        print(info)
        return render_template('ev_band_v2.html',data=data,info=info)
        
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
@ev_band.route('/draw_bandv2',methods=['GET','POST','PUT'])
def draw_bandv2():
        if session['name'] not in ['王之霖','张凌宇']:
                return abort(403,"YOU'VE REACHED A FORBIDDEN AREA!")
        code=request.args.get('code',None)
        logger.info(request.args)
        logger.info('processing')
        if not code:
                return draw_band_index()
        #zip request agrs to data, if key not in request args, return 400 error
        data={key:request.args.get(key,None) for key in ['start_date','target_date','start_upper','start_lower','target_upper','target_lower','name']}
        if not all(data.values()):
                #give the none value key
                return abort(400,f"输入有误，请返回,缺少{[key for key,value in data.items() if not value]}")
        try:
                use_default_start_arg=request.args.get('use_default',None)
                use_default_start=use_default_start_arg=='true'
                worker=New_band2(code,data,use_default_start=use_default_start)
                r=worker.work()
                if 'error info' in r.keys():
                        return abort(400,r['error info']['error'])
                info=r.pop('info')
                code=r.pop('code')
                info['code']=code
                print(len(r['source']))
                info=[info]
                data=[r]
                print(info)
                #print(data)
                #return jsonify(r)
                return render_template('ev_band_v2.html',data=data,info=info)
        # if exception, return traceback as json
        except Exception as e:
                import traceback
                #print('here?')
                #logger.error(e)
                traceback_str = traceback.format_exc()
                logger.error(e)
                logger.error(traceback_str)
                return abort(400,description='输入信息有误，请返回。   error info:'+str(e))
                return jsonify({'error':str(e)},{'traceback':traceback_str})
                #return abort(400,str(e))
#open an api endpoint for draw_bandv2, return json dic data rather than html
#data with a res code, 0 for success, 1 for error, when success, return data and info, when error, return error info
@ev_band.route('/draw_bandv2_api',methods=['GET','POST','PUT'])
def draw_bandv2_api():
        if session['name'] not in ['王之霖','张凌宇']:
                return jsonify({'res':1,'error':"YOU'VE REACHED A FORBIDDEN AREA!"})
        logger.info(request.args)
        logger.info('processing')
        code=request.args.get('code',None)
        if not code:
                return jsonify({'res':2,'error':'code is None'})
        #zip request agrs to data, if key not in request args, return 400 error
        data={key:request.args.get(key,None) for key in ['start_date','target_date','start_upper','start_lower','target_upper','target_lower','name']}
        if not all(data.values()):
                #give the none value key
                return jsonify({'res':3,'error':f"输入有误，请返回,缺少{[key for key,value in data.items() if not value]}"})
        try:
                use_default_start_str=request.args.get('use_default',None)
                use_default_start=use_default_start_str=='true'
                worker=New_band2(code,data,use_default_start=use_default_start)
                r=worker.work()
                if 'error info' in r.keys():
                        return jsonify({'res':4,'error':r['error info']['error']})
                info=r.pop('info')
                code=r.pop('code')
                info['code']=code
                print(len(r['source']))
                info=[info]
                data=[r]
                print(info)
                #print(data)
                #return jsonify(r)
                return jsonify({'res':0,'data':data,'info':info})
        # if exception, return traceback as json
        except Exception as e:
                import traceback
                #print('here?')
                #logger.error(e)
                traceback_str = traceback.format_exc()
                logger.error(e)
                logger.error(traceback_str)
                
                return jsonify({'res':5,'error':'输入信息有误，请检查代码、市值信息。   error info:'+str(e)})
                return jsonify({'error':str(e)},{'traceback':traceback_str})
                #return abort(400,str(e))
@ev_band.route('/draw_band',methods=['GET','POST'])
def draw_band():
    if session['name'] not in ['王之霖','张凌宇']:
        return abort(403,"YOU'VE REACHED A FORBIDDEN AREA!")

    code = request.args.get('code')

    if not code:
        return render_template('ev_band_draw.html')
    try:
        params = {key: request.args.get(key) for key in ['name', 'pc', 'po', 'xc', 'xo']}
        dates = {key: datetime.strptime(request.args.get(key), '%Y-%m-%d') if request.args.get(key) else None for key in ['start', 'target']}
        #change keys :'start'->'start_date','target'->'target_date'
        dates = {key + '_date': value for key, value in dates.items()}
        
        params.update(dates)
        #params['summary'] = code + ' ' + request.args.get('name')
        #refactor the last line with f_string
        params['summary'] = f'{code} {request.args.get("name")}'
        
        return draw_ev_band(code, params['summary'], [params])
    except:
        #return '输入有误，请返回'
        return abort(400,"输入有误，请返回")

def draw_band_old():
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
                                return abort(400,"输入有误，请返回")
        else:
                #return 403,"YOU'VE REACHED A FORBIDDEN AREA!"
                return abort(403,"YOU'VE REACHED A FORBIDDEN AREA!")