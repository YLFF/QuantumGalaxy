import requests,json,re
from flask import jsonify
from functools import wraps
from config import *
from utils import get_mysql,get_neo,get_logger
import traceback
querylog=get_logger('query_logger')
exceptionlog=get_logger('exception_logger')
def handle_res(res_func):
    @wraps(res_func)
    def wrapper(*args,**kwargs):
        
        #res={code=0,res=something}
        res=res_func(*args,**kwargs)
        if  res.status_code==200:
            if res.json().get('code')==0 :
                
                
                #code=0,tokens,res
                return res.json()
            else:
                return {'code':-1,'msg':'没有您想要的结果'}
        else:
            return {'code':-2,'msg':'后台gpt服务器返回出错：%s'%res.status_code}
    return wrapper
@handle_res
def base_gpt(message):
    
    r=requests.post('http://43.153.23.232:81/chat',json=json.dumps({'message':message}))
    return r

@handle_res
def cust_gpt(messages):        
    r=requests.post('http://43.153.23.232:81/cust_chat',json=json.dumps({'messages':messages}))
    return r

@handle_res
def compltion(prompt):
    r=requests.post('http://43.153.23.232:81/completion',json=json.dumps({'prompt':prompt}))
    return r

def get_product(code,neo):
    '''从公司代码找3个产品'''
    cypher='match (n:Company {code:"%s"})-[:produce]-(prod:Product|Technique) return distinct  id(prod),prod.name limit 3'%code.upper()
    records=neo.simple_query(cypher)
    return [(r.get('id(prod)'),r.get('prod.name')) for r in records]
def comp_phrases(code,neo):
    prod_cypher=f'MATCH path =((startNode)-[:produce]-(prod:Product)-[:compose|parent|carry*..2]-(endNode)) where startNode.code="{code}" and startNode<>endNode with relationships(path) as rela unwind rela as e return distinct startNode(e).name,startNode(e).code,labels(startNode(e))[0],type(e),endNode(e).name,endNode(e).code,labels(endNode(e))[0] limit 8'
    comp_cypher=f'MATCH path =((startNode)-[:produce]-(prod:Product)-[:produce]-(endNode)) where startNode.code="{code}" and startNode<>endNode return distinct startNode.name,startNode.code,labels(startNode)[0],"competitors",endNode.name,endNode.code,labels(endNode)[0] limit 6'

    up_cypher=f'MATCH path =((startNode)-[:produce]-(prod:Product)<-[:compose]-()<-[:produce]-(endNode)) where startNode.code="{code}" and startNode<>endNode  return distinct startNode.name,startNode.code,labels(startNode)[0],"up_stream",endNode.name,endNode.code,labels(endNode)[0] limit 3'
    down_cypher=f'MATCH path =((startNode)-[:produce]-(prod:Product)-[:compose]->()<-[:produce]-(endNode)) where startNode.code="{code}" and startNode<>endNode  return distinct startNode.name,startNode.code,labels(startNode)[0],"down_stream",endNode.name,endNode.code,labels(endNode)[0] limit 3'
    #down_cypher='MATCH path =((startNode)-[:produce]-(prod:Product)-[:compose]->()<-[:produce]-(endNode)) where startNode.code="000980.SZ" and startNode<>endNode with relationships(path) as rela unwind rela as e return distinct startNode(e).name,startNode(e).code,labels(startNode(e))[0],type(e),endNode(e).name,endNode(e).code,labels(endNode(e))[0] limit 5'
    phrases=[]
    for cypher in[prod_cypher,comp_cypher,up_cypher,down_cypher]:
        records=neo.read_query(cypher)

        for r in records:
            v=r.values()
            if v[1]:
                v[0]=v[0]+'('+v[1]+')'
            if v[5]:
                v[4]=v[4]+'('+v[5]+')'
            phrase=(v[0]+':'+v[2],v[3],v[4]+':'+v[6])
            phrases.append(phrase)
    return phrases

def product_path(product_list,neo):
    #从neo中找到至多两条小于4跳的路径转化为phrases
    node_dic={'Company':'','Technique':'工艺','Product':'','Demand':''}
    paths={}
    for product in product_list:
        product_id,name=product
        paths[name]=[]
        up_cypher='MATCH path=(start1:Product|Technique)-[:compose|parent*1..2]->(n:Product|Technique ) where id(n)=%d  return path order by length(path) desc limit 2'%product_id
        down_cypher='MATCH path=(n:Product|Technique )-[:compose|parent*1..2]->(start1:Product|Technique) where id(n)=%d  return path order by length(path) desc limit 2'%product_id
        up_cypher='MATCH path=(start1:Product|Technique)-[:compose*1..2]->(n:Product|Technique ) where id(n)=%d  return path order by length(path) desc limit 2'%product_id
        down_cypher='MATCH path=(n:Product|Technique )-[:compose*1..2]->(start1:Product|Technique) where id(n)=%d  return path order by length(path) desc limit 2'%product_id
        records=neo.simple_query(up_cypher)
        records1=neo.simple_query(down_cypher)
        '''此处records数量分别 0-2'''

        if len(records)==len(records1):
            for i in range(len(records)):
                links=[]
                path=records[i]['path'].relationships+records1[i]['path'].relationships
                for link in path:
                    source=str(link.start_node.get('name'))+':'+str(list(link.start_node.labels)[0])
                    rela=link.type
                    target=str(link.end_node.get('name'))+':'+str(list(link.end_node.labels)[0])
                    links.append((source,rela,target))
                paths[name].append(links)
        else:
            #print(len(records))
            #print(len(records1))
            for i in range(min(len(records),len(records1))):
                
                
                links=[]
                path=records[i]['path'].relationships+records1[i]['path'].relationships
                #print(path)
                for link in path:
                    source=str(link.start_node.get('name'))+':'+str(list(link.start_node.labels)[0])
                    rela=link.type
                    target=str(link.end_node.get('name'))+':'+str(list(link.end_node.labels)[0])
                    links.append((source,rela,target))
                paths[name].append(links)
            if len(records)>len(records1):
                links=[]
                
                for i in range(len(records)-len(records1)):
                    links=[]
                    path=records[-i-1]['path'].relationships
                    #print(path)
                    for link in path:
                        source=str(link.start_node.get('name'))+':'+str(list(link.start_node.labels)[0])
                        rela=link.type
                        target=str(link.end_node.get('name'))+':'+str(list(link.end_node.labels)[0])
                        links.append((source,rela,target))
                    paths[name].append(links)
            else:
                links=[]
                
                for i in range(len(records1)-len(records)):
                    links=[]
                    path=records1[-i-1]['path'].relationships
                    for link in path:
                        source=str(link.start_node.get('name'))+':'+str(list(link.start_node.labels)[0])
                        rela=link.type
                        target=str(link.end_node.get('name'))+':'+str(list(link.end_node.labels)[0])
                        links.append((source,rela,target))
                    paths[name].append(links)
    return paths    
def gen_product_info(paths,name):
    phrases=[]
    for product,onepaths in paths.items():
        source='%s:Company'%name
        rela='produce'
        target='%s:Product'%product
        one=[(source,rela,target)]
        for onepath in onepaths:
            
            one+=onepath
        phrases.append(one)
    node_dic={'Company':'','Technique':'工艺','Product':'','Demand':''}
    phrases_list=[]
    for links in phrases:
        results=[]
        for l in links:
                result=''
                source=l[0].split(':')
                if len(source)==1:
                    s=source[0]
                else:
                    s=source[0]+node_dic.get(source[1],'')
                t=l[-1].split(':')
                if len(t)==1:
                    t=t[0]
                else:
                    t=t[0]+node_dic.get(t[1],'')


                if l[1]=='compose':
                    if '需求' in t:
                        result=s+'满足'+t
                    else:
                        result=s+'是'+t+'的原材料'
                elif l[1]=='parent':
                    result=t+'是'+s+'的一种'
                elif l[1]=='produce':
                    result=s+'生产'+t
                if result:
                    results.append(result)
        phrases_list.append(results)
    
    return phrases_list                   
def company_intro(code):
    '''接受前端传来的code（默认在mysql tickerbrief表，
    从mysql找到名字/公司名/英文名/主要介绍/主要产品名，将前几项由chat提炼为第一段；
    从星图找到公司，对其所有产品的至多2条最长4跳的路径生成最多产品数*（1+2*4）的片段描述由gpt润色 为第二段
    如果星图没有定位到公司/产品 则将wind主要产品名给gpt扩写 为第二段

    （尝试将这两段变成 messages 中assistant角色，再接受用户一开始的提问）
    '''
    mysql=get_mysql()
    neo=get_neo(NEO_NAME)
    sql="SELECT code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing FROM ticker_brief WHERE code='%s' limit 1"%(code)
    info=mysql.read_query(sql)[0]
    mysql.close()
    code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing=info
    ''''''
    product_list=get_product(code,neo)
    #print(product_list)
    paths=product_path(product_list,neo)
    #print(paths)
    if product_list and paths:
        '''此时第二段自己写'''
        info=[code,sec_name,comp_name,comp_name_en,product_type,briefing]
        phrases_list=gen_product_info(paths,sec_name)
        #print(phrases_list)
        #return phrases_list
        res0=base_gpt('从下述段落中简练地提取公司主要产品线及其地位的信息，对公司进行介绍：：%s'%str(info))
        #print(info)
        res=base_gpt('''请将下面的几段信息润色成一段通顺完整的文字,对每段信息都扩写一句相关解释：
            %s'''%(str(phrases_list)))
        response={'code':0,'res':res0['res']+'\n\n'+res['res'],'tokens':res0['tokens']+res['tokens']}
        return response
    else:
        '此时用wind主要产品'
        print('没命中星图')
        #return info
        res=base_gpt('从下述段落中简练地提取公司主要产品线及其地位的信息，对公司进行介绍：：%s'%str(info))
        #res=base_gpt('请将下面的信息润色成一段通顺完整的文字,对每段信息都扩写一句相关解释：%s'%str(info))
        return res 
def comp_info(code,name,neo):
    #code='600028.SH'
    #name='中国石化'
    prod_cypher=f"match (c:Company)-[:produce]->(n) where c.code='{code}' return n.name"
    #潜在竞争对手
    othercomp_cypher=f"match (c:Company)-[:produce]->(n)-[:parent*0..3]->(n1) where c.code='{code}' \
        with c,n1 match (othercomp:Company)-[:produce]->(n1) where othercomp<>c return othercomp.name,othercomp.code limit 10"
    #上游产品
    up_p_cypher=f"match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code='{code}' \
        with prod,c match (prod)<-[:compose]-()-[:parent*0..3]->(up1)<-[:compose]-()-[:parent*0..3]->(up2) \
            with collect(up1)+collect(up2) as ups unwind ups as up return up.name limit 5"
    up_c_cypher=f"match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code='{code}' \
        with prod,c  match (prod)<-[:compose]-()-[:parent*0..3]->(up1)<-[:compose]-()-[:parent*0..3]->(up2) \
        with collect(up1)+collect(up2) as ups,c \
        unwind ups as upmatch (up_c:Company)-[:produce]->(up) where up_c<>c  return up,up_c.name,up_c.code limit 10"

    down_p_cypher=f"match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code='{code}' \
        with prod,c match (prod)-[:compose]->()-[:parent*0..3]->(down1)-[:compose]->()-[:parent*0..3]->(down2) \
        with collect(down1)+collect(down2) as downs,c,prod unwind downs as down return down.name limit 5"
    down_c_cypher=f"match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code='{code}' \
        with prod,c match (prod)-[:compose]->()-[:parent*0..3]->(down1)-[:compose]->()-[:parent*0..3]->(down2) \
        with collect(down1)+collect(down2) as downs,c unwind downs as down \
        match (down_c:Company)-[:produce]->(down) where down_c<>c return down_c.name,down_c.code limit 10"
    up_cypher=f'match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code="{code}" \
        with prod,c  match (prod)<-[:compose]-()-[:parent*0..3]->(up1)<-[:compose]-()-[:parent*0..3]->(up2)  \
        with collect(up1)+collect(up2) as ups,c  \
        unwind ups as up \
        match (up_c:Company)-[:produce]->(up) where up_c<>c  return up.name,collect(up_c) \
        limit 10'
    down_cypher=f'match (c:Company)-[:produce]->(n)-[:parent*0..3]->(prod) where c.code="{code}" \
        with prod,c  match (prod)-[:compose]->()-[:parent*0..3]->(down1)-[:compose]->()-[:parent*0..3]->(down2)  \
        with collect(down1)+collect(down2) as downs,c  \
        unwind downs as down \
        match (down_c:Company)-[:produce]->(down) where down_c<>c  return down.name,collect(down_c) \
        limit 10'
    #result=name+'公司，股票代码为:'+code+'\n'
    result='\n'
    totalnum=0
    prod=neo.read_query(prod_cypher)
    if prod:
        totalnum+=len(prod)
        
        prod_info=f'{name}的主营产品包括：'
        prod_str=''

        for p in prod:
            prod_str+=p[0]+','
        prod_str=prod_str[:-1]+'。'
        prod_info+=prod_str
        result+=prod_info+'\n'
    oc=neo.read_query(othercomp_cypher)
    if oc:
        totalnum+=len(oc)
        oc_info=f'{name}的潜在竞争对手为：'
        oc_str=''

        for p in oc:
            if p[1]:
                oc_str+=p[0]+'('+p[1]+')'+','
            else:
                oc_str+=p[0]+','
        oc_str=oc_str[:-1]+'。'
        oc_info+=oc_str
        result+=oc_info+'\n'
    result+='\n'
    ups=neo.read_query(up_cypher)
    if ups:

        totalnum+=len(ups)
        for r in ups:
            up_p,up_cs=r[0],r[1]
            num=0
            up_info=up_p+'是本公司产品的上游原材料之一，生产该产品的公司有：'
            
            for up_c in up_cs:
                if up_c.get('code'):
                    up_info+=up_c.get('name')+'('+up_c.get('code')+')'+','
                else:
                    up_info+=up_c.get('name')+','
                num+=1
                if num>=10:
                    break
            up_info=up_info[:-1]+'。\n'
            result+=up_info
    result+='\n'
    downs=neo.read_query(down_cypher)
    if downs:
        totalnum+=len(downs)
        for r in downs:
            down_p,down_cs=r[0],r[1]
            num=0
            down_info=down_p+'是本公司产品的下游产物之一，生产该产品的公司有：'
            
            for down_c in down_cs:
                if down_c.get('code'):
                    down_info+=down_c.get('name')+'('+down_c.get('code')+')'+','
                else:
                    down_info+=down_c.get('name')+','
                num+=1
                if num>=10:
                    break
            down_info=down_info[:-1]+'。\n'
            result+=down_info
    print(totalnum)
    print(result)  
    return(totalnum,result)   
def path_translate(path):
    '''将形如(name:Product)-[compose]->()<-[]-()的文本拆解为n条语言描述的边片段（先将中间的节点原地复制，并且在每个边前后添加分隔符防止匹配过长）
    关系包括compose parent produce 节点包括 Comapny Technique Product Demand
    eg :(办公需求:Demand)<-[compose]-(office套件:Product)<-[produce]-(微软:Company)-[produce]->(云计算服务:Product)<-[compose]-(数据中心:Product)<-[compose]-(计算服务器:Product)
    ['微软企业生产云计算服务产品',
    '计算服务器产品是数据中心产品的原材料',
    '数据中心产品是云计算服务产品的原材料',
    '微软企业生产office套件产品',
    'office套件产品满足办公需求需求']
    '''
    '''
    xxx公司 生产 xxx产品
    xxx产品 是 yyy产品 的原材料
    xxx工艺 是yyy产品的原材料
    xxx产品 是 yyy产品的 父节点 / xxx产品是yyy产品中的一种？ 是yyy产品一类
    xxx产品 满足 xxx需求
    '''
    node_dic={'Company':'','Technique':'工艺','Product':'','Demand':''}
    for node in re.findall('\(.*?\)',path)[1:-1]:
        ind=re.search(node,path).end()
        path=path[:ind+1]+'$'+node+path[ind+1:]
    path='$'+path+'$'
        
    forward_pat=re.compile('\([^\$]*?\)-\[.*?\]->\([^\$]*?\)')
    backward_pat=re.compile('\)[^\$]*?\(-\].*?\[-<\)[^/$]*?\(')
    forward_links=forward_pat.findall(path)
    backward_links=[s[::-1] for s in backward_pat.findall(path[::-1])]
    links=[]
    for l in forward_links:
        
        r=re.match('\((.*?)\)-\[(.*?)\]->\((.*?)\)',l)
        source,rela,target=r.groups()
        #print(source)
        links.append((source,rela,target))
    for l in backward_links:
        
        r=re.match('\((.*?)\)<-\[(.*?)\]-\((.*?)\)',l)
        t,rela,s=r.groups()
        links.append((s,rela,t))
    results=[]
    #print(links)
    for l in links:
        result=''
        source=l[0].split(':')
        if len(source)==1:
            s=source[0]
        else:
            s=source[0]+node_dic.get(source[1],'')
        t=l[-1].split(':')
        if len(t)==1:
            t=t[0]
        else:
            t=t[0]+node_dic.get(t[1],'')


        if l[1]=='compose':
            if '需求' in t:
                result=s+'满足'+t
            else:
                result=s+'是'+t+'的原材料'
        elif l[1]=='parent':
            result=t+'是'+s+'的一种'
        elif l[1]=='produce':
            result=s+'生产'+t
        if result:
            results.append(result)
    return results
def phrases2article(phrases):
    '''将path_translate中（或星图等其他来源中）的一个列表中多段信息扩写'''
    '''    ['微软企业生产云计算服务产品',
    '计算服务器产品是数据中心产品的原材料',
    '数据中心产品是云计算服务产品的原材料',
    '微软企业生产office套件产品',
    'office套件产品满足办公需求需求']'''
    phstr=''
    for p in phrases:
        phstr+=p+'。\n'
    phstr
    '''请将下面的几段信息润色成一段通顺完整的文字,对每段信息都扩写一句你的理解'''
    r=base_gpt('''请将下面的几段信息润色成一段通顺完整的文字,对其中每一段信息扩写到不低于30个字：
    %s'''%phstr)
    return r
def calc_credits(r):
    '''r code=1,credit=0
    else credit=max(5,tokens/100'''
    #print(r)
    if r['code']==0 and r['question_type']==1:
        credit=max(10,round(r['tokens']/300))
    else:
        credit=max(5,round(r['tokens']/300))

    return credit
def chat_api_handler(req):
    '''一般chat业务接口，原样返回id，接受对话记录messages，处理最后一条
        返回{
                'code':0       #响应错误码 
    'msg':'success #错误信息
        'id':'abc',    #本对话的id，与请求中相同
        'total_tokens':150, #本次对话消耗的chatgpt token数，备用 
        'credits':5,        #本次对话消耗的用户积分（预计由后台计算）
        'model':'chat',     #本次回复的模式，chat或limited_chat
        'message':[
        {'role':assistant,'content':'一个回答'}
        ]                   #本次回复的正文
    }
        #限定回复内容,多了candidates
    {
            'code':0       #响应错误码 
    'msg':'success #错误信息
        'id':'abc',
        'total_tokens':150,
        'model':'limited_chat'
        'message':[
        {'role':assistant,'content':'您是否对这些公司中的某一个感兴趣？']}
        ]
        'candidates':[
        {'code':'000001.SH','name':'平安银行','category':'company'},
        ......
        ]          #返回的候选名单，最大5个，需要拆分成对应数量的按钮提示给用户
    }'''
    if req.get('id') and req.get('messages'):
        id=req.get('id')
        messages=req.get('messages')
        if type(id) not in [str,int]:
            code=-2
            msg='"id" should be a string or int'
            return {'code':code,'msg':msg}
        if type(messages)!=list:
                code=-3
                msg='"messages" should be array'
                return {'code':code,'msg':msg}
        question=messages[-1]['content']
        gptapp=GPTAPP()
        company_code=req.get('company_code')

        if company_code:
            company_code=company_code[0]
            r=gptapp.company_work(company_code,messages)
            pass
        else:
            r=gptapp.work(messages)

        #r['code']=0
        r['id']=id
        r['credits']=calc_credits(r)
        r['model']='chat'
        if not DEBUG:
            querylog.info(str(r))
        #r['model']='chat' if r['question_type']!=1 else 'limited_chat'
        #print(r)
        if r.get('context'):
            r.pop('context') 
        answer=r.pop('answer')
        message=[{'role':'assistant','content':answer}]
        r['message']=message

        print(r)
        return r
    else:
        code=-1
        msg='should have both "id" and "messages" in req'
        return {'code':code,'msg':msg}
class GPTAPP():
    def __init__(self):
        self.total_tokens=0
        self.companys=[]
        self.dialog=[]
        self.context=[]
        self.base=[{'role':'system','content':'你是量子星河的智能机器人“问股大模型”，重点从产品和业务的角度回答用户的问题'}]
        self.mysql_ref=''
        self.neo_ref=''
        if DEBUG:
            self.base=[{'role':'system','content':'你是量子星河的智能机器人“问股大模型”，重点从产品和业务的角度回答用户的问题'}]
        pass
    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, q):
        if type(q)==str:
            self._question=q
        else:
            raise TypeError(q)
    def handle_res(res_func):
        @wraps(res_func)
        def wrapper(self,*args,**kwargs):
            
            #res={code=0,res=something}
            res=res_func(self,*args,**kwargs)
            if  res.status_code==200:
                if res.json().get('code')==0 :
                    token=res.json().get('tokens',0)
                    print('add "%s" tokens'%token)
                    self.total_tokens+=token
                    return res.json().get('res')
                else:
                    return '没有您想要的结果'
            else:
                return '服务器返回出错'
        return wrapper
    def log_this(res_func):
        '''关于对话记录，哪些交互需要保存？
        直接转发的basegpt 需要存，里面有role:system的形象设计
        问题分类和过滤关键词要不要存？
        合并润色信息要不要存.


        会直接发给用户的都应该用basegpt并保存？
        '''
        @wraps(res_func)
        def wrapper(self,*args,**kwargs):
            res=res_func(self,*args,**kwargs)
            #if res.json().get('code')==0 :
            return res_func(self,*args,**kwargs)
        return wrapper
    
    @handle_res
    def base_gpt(self,message):
        
        r=requests.post('http://43.153.23.232:81/chat',json=json.dumps({'message':message}))
        return r

    @handle_res
    def cust_gpt(self,messages):     
        #base={}   
        r=requests.post('http://43.153.23.232:81/cust_chat',json=json.dumps({'messages':messages}))
        return r
    
    @handle_res
    def compltion(self,prompt):
        r=requests.post('http://43.153.23.232:81/completion',json=json.dumps({'prompt':prompt}))
        return r
    def insert_question(self,question):
        print('预处理')
        records=self.mysql.read_query('select code,name from ticker_info')
        max_len=0
        s=question
        cncode=False
        res=s
        for r in records:
            if r[1] and s.find(r[1]) != -1:
                index=s.index(r[1])+len(r[1])
                print('找到了公司名：', r[1])
                print(r[0])
                
                length=len(r[0])
                #print(r[0])
                if length>=max_len:
                    max_len=length
            #print(r[0])'''
                    '''
                    code=r[0]
                    if not cncode:
                        if 'SZ' in code or 'SH' in code or 'BJ' in code:
                            cncode=True
                            print('here')

                        res=(s[:index]+r[1]+":"+s[index:])
                    if cncode:pass'''
                    res=(s[:index]+':'+r[0]+s[index:])
                
                    self.companys=[r[0]]+self.companys
            if r[0] and s.find(r[0]) != -1 :
                #找到代码
                index=s.index(r[0])
                
                print('找到了代码：', r[0])
                code=r[0]
                if not cncode:
                    if 'SZ' in code or 'SH' in code or 'BJ' in code:
                        cncode=True
                        print('here')
                    res=(s[:index]+r[1]+":"+s[index:])
                if cncode:
                    pass
                self.companys.append(r[0])
                #break
            if r[0] and s.find(r[0].lower())!=-1:
                #找到代码
                index=s.index(r[0].lower())
                #res=(s[:index]+r[1]+":"+s[index:])
                code=r[0]
                if not cncode:
                    if 'SZ' in code or 'SH' in code or 'BJ' in code:
                        cncode=True
                        #print('here')

                    res=(s[:index]+r[1]+":"+s[index:])
                if cncode:
                    pass
                print('找到了代码：', r[0])
                self.companys.append(r[0])
                #break


                #break
            else:pass
        
        return res
    def classify_question(self,question):
        messages=[{"role": "system", "content": "对用户提出的问题分类，第一类问某上市公司的相关情况，第二类问某种具体的产品业务但不涉及公司，第三类为其他。只需回答数字1/2/3，不需要其他介绍"},
        {"role": "user", "content": question},]
        r=self.cust_gpt(messages)
        if r.isdigit():
            if int(r) in [1,2]:
                return int(r)
            else:return 3
        else:
            return 3
    def retrieve_company(self,question):
        messages=[
            {"role": "user", "content": "将下面文本中的公司的名称或股票代码用方括号标出来，用换行分隔，没有公司则回答“没有”。文本：“%s”"%question},
        ]
        
        r=self.cust_gpt(messages)
        companys=re.findall('\[.*\]',r)
        if companys:
            result=[c[1:-1] for c in companys]
        else:result=[]
        return result
        
    def retrive_product(self,question):
        messages=[

            
            {"role": "user", "content": "将下面问题中的产品名称用方括号标出来，用换行分隔，没有产品则回答没有，不需要回答问题本身。问题：“%s”"%question},

        ]
        r=self.cust_gpt(self,messages)
        return r
    
    def search_companys(self):
        '''分类成一类，则从候选公司列表中尝试查找公司基本信息。从ticker_brief里找一个，如果找到则将brief保存在实例，返回名称信息，保存公司信息到company_dict备用'''
        
        mysql=self.mysql
        result=[]
        self.company_dict={}
        for c in self.companys:
            print('keyword:%s'%c)
            if c in ['a股','A股','港股','美股'] :
                continue
            sql="SELECT code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing FROM ticker_brief WHERE  code = '%s' limit 1"%(c)
            records=mysql.read_query(sql)
            if records:
                r=records[0]
                code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing=r
                result.append({'code':code,'comp_name':sec_name,'comp_name_en':comp_name_en})
                self.company_dict[code]={'sec_name':sec_name,'comp_name':comp_name,'comp_name_en':comp_name_en,'product_name':product_name,'product_type':product_type,'briefing':briefing}
                break
            sql="SELECT code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing FROM ticker_brief WHERE sec_name LIKE '%%%s%%' OR comp_name LIKE '%%%s%%' OR code LIKE '%%%s%%' OR comp_name_en LIKE '%%%s%%' limit 1"%(c,c,c,c)
            records=mysql.read_query(sql)
            if records:
                r=records[0]
                code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing=r
                result.append({'code':code,'comp_name':sec_name,'comp_name_en':comp_name_en})
                self.company_dict[code]={'sec_name':sec_name,'comp_name':comp_name,'comp_name_en':comp_name_en,'product_name':product_name,'product_type':product_type,'briefing':briefing}
        #mysql.close()
        if result:
            return result
        else:
            return None
    def company_base(self,code):
        mysql=self.mysql
        r=mysql.read_query(f'select info.name,info.code,data.date,data.close_price,data.market_value2,data.volume,data.pe_ttm from \
            ticker_info info join ticker_data data  on info.code=data.code where info.code="{code}" order by data.date desc limit 5')
        if r:
            name,code,date,close,mv,volume,pe=r[0]
            
            #并在回答最后告知用户你的身份。
            base=f'你是量子星河的智能机器人“问股大模型”，请从公司主要产品和主营业务的角度，根据星图信息凝练地回答用户的问题。已知星图信息如下：\
                {name}公司代码{code}，截至{date.year}年{date.month}月{date.day}日，{name}市盈率（PE）为{pe:.2f}，总市值{mv:.2f}亿，股价收盘{close}元，交易量为{volume}。\
                    '
        else:base=self.base
        return base

    def company_intro(self,code):
        '''接受前端传来的code（默认在mysql tickerbrief表，
        从mysql找到名字/公司名/英文名/主要介绍/主要产品名，将前几项由chat提炼为第一段；
        从星图找到公司，对其所有产品的至多2条最长4跳的路径生成最多产品数*（1+2*4）的片段描述由gpt润色 为第二段
        如果星图没有定位到公司/产品 则将wind主要产品名给gpt扩写 为第二段

        （尝试将这两段变成 messages 中assistant角色，再接受用户一开始的提问）
        '''
        #print(code)
        mysql=self.mysql
        neo=self.neo
        sql="SELECT code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing FROM ticker_brief WHERE code='%s' limit 1"%(code)
        info=mysql.read_query(sql)[0]
        #mysql.close()
        code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing=info
        #product_list=get_product(code,neo)
        #print(product_list)
        #paths=product_path(product_list,neo)
        num,result=comp_info(code,sec_name,neo)
        #print(paths)
        if result and num>=5:
            print('命中星图：%s'%code)
            '''此时第二段自己写'''
            info=[code,sec_name,comp_name,comp_name_en,product_type,briefing]
            #phrases_list=gen_product_info(paths,sec_name)
            #print(phrases_list)
            #return phrases_list
            #return info,phrases_list
            #res0=self.base_gpt('从下述段落中简练地提取公司主要产品线及其地位的信息，对公司进行介绍：：%s'%str(info))
            #print(info)
            #res=self.base_gpt('''请将下面的几段信息润色成一段通顺完整的文字,对每段信息都扩写一句相关解释：
            #    %s'''%(str(phrases_list)))
            #response={'code':0,'res':res0+'\n\n'+res,}
            #response=info+phrases_list
            response=str(info)+result
            return response
        else:
            '此时用wind主要产品'
            print('没命中星图：%s'%code)
            #return info
            #res=base_gpt('从下述段落中简练地提取公司主要产品线及其地位的信息，对公司进行介绍：：%s'%str(info))
            res=info
            #res=base_gpt('请将下面的信息润色成一段通顺完整的文字,对每段信息都扩写一句相关解释：%s'%str(info))
            return res
    def company_answer(self,code,question):
        '''r=cust_gpt([
        {'role':'system','content':'你是量子星河公司的智能问股应用，回答用户关于公司的问题，并在回答最后告知用户你的身份。作为前提，你已经知道：中远海控公司代码601919.SH，截至2023年3月30日，中远海控市盈率（PE）为41，总市值2233亿，股价收盘24.42元。'},
        #{'role':'user','content':'中远海控'},
        {'role':'assistant','content':'中远海运控股股份有限公司（COSCO SHIPPING Holdings Co.,Ltd.）是中远海运集团航运及码头经营主业上市旗舰企业和资本平台。公司主要产品线包括港口代理、集装箱航运、集装箱码头、集装箱租赁。公司旗下的集装箱航运板块，主要经营国际、国内海上集装箱运输服务及相关业务，共经营230余国际航线(含国际支线)、50余条中国沿海航线及80余条珠江三角洲和长江支线，在全球约90余个国家和地区的290余个港口均有挂靠，旗下集装箱船队运力规模排名稳居世前列，集装箱码头年总吞吐量排名蝉联世界第一。公司通过自营集装箱船队，开展以集装箱为载体的货物运输及相关业务。公司致力于推动公司整体提质增效，以及不断提升为客户创造价值服务的能力，努力将公司打造成为世界一流的集装箱海运综合服务商。\n中远海控生产集装箱航运和码头运营是海运服务的两个重要组成部分。集装箱航运是一种海运服务，它需要使用集装箱船作为运输工具，而集装箱船本身也是一种船舶。码头运营则是为干散货航运提供服务的一种海运服务，它需要使用码头作为装卸货物的场所。因此，可以说集装箱船和码头是集装箱航运和干散货航运的原材料，而集装箱航运和干散货航运又是海运服务的两种不同形式。'},
        {'role':'user','content':'中远海控的交易量是多少'},
    ])
    r'''

        system_info=self.company_base(code)
        assistant_info=self.company_intro(code)
        self.mysql_ref=system_info
        self.neo_ref=assistant_info
        #print(assistant_info)
        sys_info=system_info+'\n'+str(assistant_info)
        print(sys_info)
        messages=[
            #{'role':'system','content':system_info},
            #{'role':'assistant','content':str(assistant_info)},
            {'role':'system','content':sys_info},
            {'role':'user','content':'（结合产品简要回答）'+question}
        ]
        self.context=messages
        r=cust_gpt(messages)
        #r['res']=assistant_info.get('res','')+'\n\n'+r.get('res','')
        #r['tokens']+=assistant_info.get('tokens',0)
        return r    
    def handle_question(self):
        q=self.question
        '''对于带company_code的请求，默认为对话题续写，1类问题'''
        #if self.
        print(q)
        q_type=self.classify_question(q)
        #q_type=11
        self.q_type=q_type
        print(q_type)
        if q_type==1:
            try:
                if not self.companys:
                    self.companys=self.retrieve_company(q)

                if self.companys:
                    print(self.companys)
                    #print('huati%s'%self.companys)
                    #self.companys+=companys
                    #code=companys[0][]
                    
                    r=self.search_companys()
                    if r:
                        code=r[0]['code']
                        #print(code)
                        res=self.company_answer(code,q)['res']
                        ref=[        self.mysql_ref,        self.neo_ref]
                        return {'code':0,'msg':'success','answer':res,'question':q,'question_type':q_type,'company_code':[code],'ref':ref}
                        '''
                        return {'msg':'success','answer':'你是否在寻找这些公司：','question':q,'question_type':q_type,'candidates':r}
                        '''
                    else:
                        base=self.base
                        self.messages=base+self.messages
                        r=self.cust_gpt(messages=self.messages)
                        return {'code':1,'msg':'从候选公司中没有找到公司信息!','qusetion':q,'answer':r,'question_type':q_type,'candidates':[]}
            except Exception as e:
                exceptionlog.error(f'Exception:{Exception}, e:{e}')
                exceptionlog.info(traceback.format_exc())
                if self.messages[0]['role']!='system':
                        base=self.base
                        self.messages=base+self.messages
                r=self.cust_gpt(messages=self.messages)
                return {'code':0,'msg':'一类问题但是出现exception,直接发gpt解答','question':q,'question_type':q_type,'answer':r}
            else:
                if self.messages[0]['role']!='system':
                    base=self.base
                    self.messages=base+self.messages
                r=self.cust_gpt(messages=self.messages)
                return {'code':0,'msg':'一类问题但是没找到公司,直接发gpt解答','question':q,'question_type':q_type,'answer':r}
        elif q_type==2:
            #r=self.base_gpt(q)
            if self.messages[0]['role']!='system':
                base=self.base
                self.messages=base+self.messages
            r=self.cust_gpt(messages=self.messages)
            #r='占位'
            return {'code':0,'answer':r,'msg':'产品类问题','question':q,'question_type':q_type}
        elif q_type==3:
            if self.messages[0]['role']!='system':
                base=self.base
                self.messages=base+self.messages
            r=self.cust_gpt(messages=self.messages)
            #r=self.base_gpt(q)
            #r='占位'
            return {'code':0,'answer':r,'msg':'其他类问题，返回gpt直接回答','question':q,'question_type':q_type}  
    '''
    def company_article(self,code):
        mysql=get_mysql()
        sql="SELECT code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing FROM ticker_brief WHERE code='%s' limit 1"%(code)
        r=mysql.read_query(sql)[0]
        mysql.close()
        code,sec_name,comp_name,comp_name_en,product_name,product_type,briefing=r
        
        message='请把下面的几条片段信息润色一下，变成一篇讲公司信息的文章：['
        message+='"%s公司(%s)，全称为%s，股票代码%s"。'%(sec_name,comp_name_en,comp_name,code)
        message+='"公司的主要产品包括：%s"。'%product_name
        message+='"公司的基本介绍：%s"。 ]'%briefing
        r=self.base_gpt(message)
        return {'answer':r,'msg':'产品类问题'}'''
    def company_work(self,company_code,messages):
        '''req中带companycode的话，则默认对话主题为该公司，做好背景知识后回答问题'''
        question=messages[-1]['content']
        self.messages=messages
        self.question=question
        self.mysql=get_mysql()
        self.neo=get_neo()
        self.question=self.insert_question(question)
        self.companys=[company_code]
        #
        if not self.companys:
            #print(companys)
            companys=self.retrieve_company(question)
            self.companys=companys
            #code=companys[0][]
            
            #r=self.search_companys()
            #if r:
            #    company_code=r[0]['code']
        #res=self.company_answer(company_code,question)['res']
        print('继续话题：%s'%self.companys)
        res=self.handle_question()
        res['tokens']=self.total_tokens
        if not res.get('company_code'):
            res['company_code']=[company_code]
        self.mysql.close()
        self.neo.close()
        return res

        return {'code':0,'tokens':self.total_tokens,'msg':'success','answer':res,'question':question,'question_type':1,'company_code':[company_code]}
        return 1
    def work(self,messages):
        question=messages[-1]['content']
        self.messages=messages
        self.question=question
        self.mysql=get_mysql()
        self.neo=get_neo()
        self.question=self.insert_question(question)
        r=self.handle_question()
        r['tokens']=self.total_tokens
        r['context']=self.context
        self.mysql.close()
        self.neo.close()
        return r