from . import robot_auth
import sys
sys.path.append(r'E:\wangzhilin\QuantumGalaxy')
import json
from QGI.feishu import base_fetch_func,fetch_tenant_token
''' "i18n_elements": {
        "zh_cn": [
        {
            "tag": "div",
            "text": {
            "content": msg,
            "tag": "lark_md"
            }
        }
        ]
    }'''

def build_card_content(title,msg):
    content={
    "config": {
        "wide_screen_mode": True
    },
    "header": {
        "template": "blue",
        "title": {
        "content": title,
        "tag": "plain_text"
        }
    },
    "elements": [
    {
      "tag": "markdown",
      "content": msg
      
    },]
    }
    content=json.dumps(content)
    return content
def app_send_msg(content,receive_id='oc_7d319ba3f1b5b738fdc4ca455898af63',msg_type='interactive',receive_type='chat_id'):
    url='https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type='+receive_type
    token=fetch_tenant_token(robot_auth)
    #print(token)
    headers = {
        'Authorization':
        'Bearer ' + token,  # your access token
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    data={
    "receive_id": receive_id,
    "msg_type": msg_type,
    "content": content,
  
    }
    #print(data)
    data=json.dumps(data)
    r=base_fetch_func(url=url,headers=headers,data=data,method='post')
    if r['code']==0:

        return r['data']
    else:
        return r

def routine_pointview_list(receive_id='oc_e783012cb60666418c19084bceb6e4eb'):
    from jira import JIRA
    jira= JIRA('https://research.quantumgalaxy.cn/',
            basic_auth=('wangzhilin','wangzhilin'))
    import re
    filter=jira.filter(11544)
    jql=filter.jql
    try:
        jql1=re.sub('DESC','ASC',jql)
    except:
        cache=re.sub('ASC','DESC',jql)
        jql1=jql
        jql=cache

    issues=jira.search_issues(jql,maxResults=10)
    issues2=jira.search_issues(jql1,maxResults=5)
    issues2=issues2[::-1]
    from datetime import datetime,timedelta
    
    msg=''
    for issue in issues:
        print(issue.fields.summary)
        fields=issue.fields
        def get(attr):
            try:
                
                return fields.__getattribute__(attr) if fields.__getattribute__(attr) else None
            except:return None
        info='**'
        #code,name,person,emotion
        #confident, shouyi
        
        info+='%s'%get('customfield_10201')+'  ' #code
        info+='%s'%get('summary')+'  '
        
        info+='%s'%get('customfield_11003')+'**\n'#emotion
        
        
        try:
            info+='收益率：%s'%(round(get('customfield_11438')*100,2))+'%  '
        except:
            info+='收益率：无\n'
        person='%s'%get('customfield_11100')#person
        conf=get('customfield_11800')
        if conf:
            try:
                conf=conf.value+conf.child.value
            except:
                conf=conf.value
            conf=re.sub('[^a-z,A-Z]','',conf)
        else:
            conf=''
        
        start_day=get('customfield_10203')
        if start_day:
            
            start_day=datetime.strptime(start_day,'%Y-%m-%d')
            days=(datetime.today()-start_day).days
            info+='(%s  %s  %d天前)\n'%(person,conf,days)
        xinfo=get('customfield_11108')
        if xinfo:
            
            '''
            xinfo=re.sub('[0-9]+\-[0-9]+\-[0-9]+','',xinfo)
            x=re.findall('[0-9]+.[0-9]+',xinfo)
            if x[0]:
                info+='当前X值：%s'%x[0]+'\n'
                '''
            xinfo=re.sub('<br>',r'\n\t',xinfo)
            info+='\t%s'%xinfo+'\n'

            
        epic=get('customfield_11412')
        
        if epic:
            info+='所属世界线：'
            name=''
            epics=epic.split(', ')
            for i in epics:
                e=jira.issue(i)
                s='[**%s**] (%s) | '%(e.fields.summary,e.permalink())
                name+=s
            info+=name[:-2]+'\n'
        
        info+='[JIRA项目] (%s)'%issue.permalink()+'  '
        url1=get('customfield_11302')
        if url1:
            info+='[研究成果](%s)'%url1+'  '
        else:
            info+='研究成果（无）  '
        url2=get('customfield_11000')
        if url2:
            info+='[成果库] (%s)'%url2+'\n'
        else:
            info+='成果库（无）  '

        info+='\n --- \n'
        msg+=info
        #、、、JIRA链接、
        #print(info)
    msg+='\n --- \n'
    for issue in issues2:
        print(issue.fields.summary)
        fields=issue.fields
        def get(attr):
            try:
                
                return fields.__getattribute__(attr) if fields.__getattribute__(attr) else None
            except:return None
        info='**'
        #code,name,person,emotion
        #confident, shouyi
        
        info+='%s'%get('customfield_10201')+'  ' #code
        info+='%s'%get('summary')+'  '
        
        info+='%s'%get('customfield_11003')+'**\n'#emotion
        
        conf=get('customfield_11800')
        
        try:
            info+='收益率：%s'%(round(get('customfield_11438')*100,2))+'%  '
        except:
            info+='收益率：无\n'
        person='%s'%get('customfield_11100')#person
        if conf:
            try:
                conf=conf.value+conf.child.value
            except:
                conf=conf.value
            conf=re.sub('[^a-z,A-Z]','',conf)
        else:
            conf=''
        
        start_day=get('customfield_10203')
        if start_day:
            
            start_day=datetime.strptime(start_day,'%Y-%m-%d')
            days=(datetime.today()-start_day).days
            info+='(%s  %s  %d天前)\n'%(person,conf,days)
        xinfo=get('customfield_11108')
        if xinfo:
            
            '''
            xinfo=re.sub('[0-9]+\-[0-9]+\-[0-9]+','',xinfo)
            x=re.findall('[0-9]+.[0-9]+',xinfo)
            if x[0]:
                info+='当前X值：%s'%x[0]+'\n'
                '''
            xinfo=re.sub('<br>',r'\n\t',xinfo)
            info+='\t%s'%xinfo+'\n'

            
        epic=get('customfield_11412')
        
        if epic:
            info+='所属世界线：'
            name=''
            epics=epic.split(', ')
            for i in epics:
                e=jira.issue(i)
                s='[**%s**] (%s) | '%(e.fields.summary,e.permalink())
                name+=s
            info+=name[:-2]+'\n'
        
        info+='[JIRA项目] (%s)'%issue.permalink()+'  '
        url1=get('customfield_11302')
        if url1:
            info+='[研究成果](%s)'%url1+'  '
        else:
            info+='研究成果（无）  '
        url2=get('customfield_11000')
        if url2:
            info+='[成果库] (%s)'%url2+'\n'
        else:
            info+='成果库（无）  '

        info+='\n --- \n'
        msg+=info
        #、、、JIRA链接、
        #print(info)

    msg+='[查看所有观点] (https://research.quantumgalaxy.cn/issues/?filter=11544)'
    msg=msg.replace('None','')
    title='投资观点收益前十/后五榜单  %s'%datetime.today().strftime('%Y-%m-%d')
    content=build_card_content(title,msg)
    r=app_send_msg(content=content,receive_id=receive_id)
    return r
