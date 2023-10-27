from flask import Flask, request, redirect,abort,jsonify
import openai,json
import time
from tenacity import retry,wait_random_exponential,stop_after_attempt
ALLOWED_IPS=[
    '82.156.248',
    '172.26.0'

]
openai.api_key ='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'
app = Flask(__name__)




from log import Logger,get_logger

logger = Logger()
query_logger=get_logger('query logger')
@app.before_request
def limit_remote_addr():

    client_ip = str(request.remote_addr)
    #print(client_ip)
    valid = False
    for ip in ALLOWED_IPS:
        if client_ip.startswith(ip) or client_ip == ip:
            valid = True
            #logger.info(client_ip)
            break
    if not valid:
        abort(403)
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def davinci(prompt):
    response=openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  max_tokens=1024,
  temperature=0
)
    try:
    
        return (response)
    except:
        #print(response)
        return None
@app.route('/completion',methods=['post'])
def completion():
    #print(request.get_json())
    req=request.get_json()
    #print(req)
    req=json.loads(req)
    #print(req)
    prompt=req.get('prompt','请自我介绍')
    try:
        start=time.time()
        r=davinci(prompt) 
        if r:
            t=time.time()-start
            #print('openai time:%s'%t)
            query_logger.info(prompt)
            usage=r['usage']
            s=''
            for k,v in usage.items():
                s+=k+'='+str(v)+'  '
            query_logger.info(s)
            query_logger.info('MODEL:DAVINCI TIME:%.2f\n'%t)
            query_logger.info(r['choices'][0]['text'])
            return jsonify(code=0,res=r['choices'][0]['text'],tokens=usage['total_tokens'])
    except Exception as e:
        print(e)
        return jsonify(code=-1,res='openai接口问题')
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def chatgpt(message):
    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature=0,
    #max_tokens=4096,
    #stream=True,
    #model="text-davinci-003",
    #model="code-davinci-002",
    messages=[
            #{"role": "system", "content": "你是量子星河（QuantumGalaxy）数据应用，请用这个身份帮助用户解决问题"},
            #{"role": "user", "content": "你是谁？"},
            #{"role": "assistant", "content": "你在北京市西城区金融街"},
            #{"role": "assistant", "content": "量子星河是一家私募公司，位于北京市西城区金融街丰汇时代大厦。拥有自己的金融产品和知识与技术服务，量子星河数据应用即为其中的一项产品。"},
            {"role": "user", "content": message},
            
        ]
    )
    if not response['choices'][0]['message']['content']:
        raise
    try:
    
        return (response)
    except:
        print(response)
        return None
@app.route('/test',methods=['get'])
def test():
    r=chatgpt('hello')
    #print(r)
    if r.get('choices'):
        return jsonify(code=0,msg='OPENAI OK')
    else:return jsonify(code=-1,msg='OPENAI DOWN')
@app.route('/test1',methods=['get'])
def test1():
    import time
    time.sleep(5)
    return 'good'
@app.route('/chat',methods=['post'])
def chat():
    #print(request.get_json())
    req=request.get_json()
    #print(req)
    req=json.loads(req)
    print(req)
    msg=req.get('message','请自我介绍')
    try:
        start=time.time()
        r=chatgpt(msg) 
        if r:
            t=time.time()-start
            query_logger.info(msg)
            usage=r['usage']
            s=''
            for k,v in usage.items():
                s+=k+'='+str(v)+'  '
            query_logger.info(s)
            #query_logger.info('%s'%usage)
            query_logger.info('MODEL:gpt TIME:%.2f\n'%t)
            query_logger.info(r['choices'][0]['message']['content'])
            #print('openai time:%s'%t)
            return jsonify(code=0,res=r['choices'][0]['message']['content'],tokens=usage['total_tokens'])
    except Exception as e:
        print(e)
        #print(r['choices'][0])
        return jsonify(code=-1,res='openai接口问题')
@app.route('/classify',methods=['post','get'])
def classify():
    req=request.get_json()
    #print(req)
    question=json.loads(req).get('question',[{"role": "user", "content":'say "i didnt say anything"'}])
    messages=[
            {"role": "system", "content": "对用户提出的问题分类，第一类问公司股价变化，第二类问产品业务，第三类为其他。只需回答数字1/2/3，不需要其他介绍"},
            

            {"role": "user", "content": question},

        ]
    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    try:
    
        return (response['choices'][0]['message']['content'])
    except Exception as e:
        print(response)
        return e
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def cust_chat_api(messages):
    response=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    #stream=True,
    #model="text-davinci-003",
    #model="code-davinci-002",
    messages=messages
    )
    if not response['choices'][0]['message']['content']:
        raise
    return response
@app.route('/',methods=['get'])
def say_hi():
    return jsonify('hi')
@app.route('/cust_chat',methods=['post'])
def cust_chat():
    '''    messages=[
            {"role": "system", "content": "你是量子星河（QuantumGalaxy）数据应用，请用这个身份帮助用户解决问题,并在每个回答中提醒用户你是量子星河数据应用"},
            #{"role": "user", "content": "你是谁？"},
            #{"role": "assistant", "content": "你在北京市西城区金融街"},
            #{"role": "assistant", "content": "量子星河是一家私募公司，位于北京市西城区金融街丰汇时代大厦。拥有自己的金融产品和知识与技术服务，量子星河数据应用即为其中的一项产品。"},
            {"role": "user", "content": message},
            
        ]'''
    req=request.get_json()
    print(req)
    messages=json.loads(req).get('messages',[{"role": "user", "content":'say "i didnt say anything"'}])
    print(messages[-1])
    start=time.time()
    response=cust_chat_api(messages)
    try:
        t=time.time()-start
        query_logger.info(messages)
        usage=response['usage']
        s=''
        for k,v in usage.items():
            s+=k+'='+str(v)+'  '
        query_logger.info(s)
        query_logger.info('MODEL:gpt TIME:%.2f\n'%t)
        query_logger.info(response['choices'][0]['message']['content'])
        return jsonify(code=0,res=response['choices'][0]['message']['content'],tokens=usage['total_tokens'])
    except Exception as e:
        print(response)
        return str(e)
#print(chatgpt('hello'))

if __name__=="__main__":
    logger.init_app(app)
    #logger.critical('go')
    app.run(host='0.0.0.0', port=81)
