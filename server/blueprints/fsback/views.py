# -*- coding: utf-8 -*-  
from .feishu_util import *
from . import fsback
from flask import jsonify
import sys
import io
'''
def setup_io():
    sys.stdout = sys.__stdout__ = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True)
    sys.stderr = sys.__stderr__ = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', line_buffering=True)
setup_io()
'''
from log import get_logger
fsbacklogger=get_logger('fs_back')
@fsback.route('/refresh/get',methods=["GET"])
def get_user_token():
    if global_var.get_value('user_access_token'):
        return global_var.get_value('user_access_token')
    else:
        return 'no token!'
@fsback.route('/login',methods=['GET','POST'])
def feishu_login():

        

    url=fetch_auth_page()

    return redirect(url)
@fsback.route('/refresh/refresh')
def refresh():
    refresh_token=global_var.get_value('refresh_token')
    #print(refresh_token)
    r=refresh_user_token(refresh_token)
    
    if r['code']==0:
            r=r['data']
            global_var.set_value('user_access_token',r['access_token'])
            global_var.set_value('refresh_token',r['refresh_token'])
            #print(global_var._global_dict)
            #print('good')
            fsbacklogger.debug('refreshed')
            return '1'
    else:
            return '0'
@fsback.route('/refresh/',methods=['GET','POST'])
def get_code():
    state=request.args.get('state',None)
    #print(state)
    if state=='0':
        code=request.args.get('code',None)
        #print('预登陆:'+code)
        r=fetch_user_token(code)
        if r['code']==0:
            r=r['data']
            global_var.set_value('user_access_token',r['access_token'])
            global_var.set_value('refresh_token',r['refresh_token'])
            #print(global_var._global_dict)
            refresh()
    else:
        r=None
    #print(global_var._global_dict['user_access_token'])
    return 'finished'
def analaze_folder(r,dic):
    
    for file in r['data']['files']:
                type=file.get('type')
                if type in ['doc','docx']:
                    dic[file.get('token')]=(file.get('url'),file.get('name'))
                    
    return dic
from QGI.feishu import post_group_msg
def star2holder(s:str,max_n=4):
    import re
    r'''对issue描述，每行开头的jira占位符 “*/#” 替换为对应数量的 \t,匹配规则为 (\n *)(\*{1,})( +)'''
    #s=re.sub('#+','',s)
    s=re.sub('\n *','\n',s)
    for i in range(max_n):
        pattern=r'(\n *)([\*#]{'+str(i)+r'})( +)'
        target=r'\n '+ '    '*i+' '
        s=re.sub(pattern,target,s)
    
    return s
@fsback.route('/fold_meta',methods=['GET','POST'])
def fold_api():
    if request.args:
        #print(request.args)
        token=request.args.get('token')
    elif request.form:
        token=request.form.get('token')
    try:
        r=fetch_folder_meta(token)
        return r
    except:
        return jsonify({
                "code": -1,
                "data": {
                    "files": [],
                    "has_more": False
                },
                "msg":"no token!"
                })
@fsback.route('/fold_children',methods=['GET'])
def fold_children():
    if request.args.get('fld_token'):
        token=request.args.get('fld_token')
        r=fetch_folder_children(token)
        return r
    else:return jsonify(code=-1,message='no token')

def build_send_msg_card(text,title,receive_id=None):
    #print('%s'%receive_id)
    data={'msg':text,'title':title}
    if receive_id:
        data['receive_id']=receive_id
    #r=base_fetch_func(url,data=data,method='post')
    from blueprints.research_robot.views import send_message
    #print(data.keys())
    r=send_message(payload=data)

    return r

def handle_issue(issue,jira,issueid):
    import re
    if issue.fields.project.key=='COMPSTUDY':
        try:
            parent=jira.issue(issue.fields.parent.key)
        except:
            text_group_msg('找不到父任务',webhook=webhook_dict['Debug群juno'])
            return False
        issue_key=issue.key
        fld_url=issue.fields.__dict__.get('customfield_11000',None)
        
        file_url=issue.fields.__dict__.get('customfield_11302',None)
        summary=issue.fields.summary
        
        try:
            summary_name=re.findall(r'[0-9,a-z,A-Z]*\.[0-9,a-z,A-Z]*',s)[0]
        except:
            summary_name=''
            
        code=issue.fields.__dict__.get('customfield_10201',None)
        try:
            people=issue.fields.customfield_11100
            if type(people)==list:
                person=[person.displayName for person in people]
                s=''
                for p in person:
                    s+=p+','
                person=s[:-1]
            else:
                person=people.displayName
        except:
            person='无'
        url=issue.permalink()
        
        conf=issue.fields.__dict__.get('customfield_11800',None)
        if conf:
            try:
                conf=conf.value+conf.child.value
            except:
                conf=conf.value
            conf=re.sub('[^a-z,A-Z]','',conf)
        else:
            conf=''
        title='公司研究成果 - %s (%s)'%(summary,code)
        msg='**研究主责人**：%s    %s\n'%(person,conf)
        msg+='**相关链接**：[**jira项目地址**] (%s) | '%(url)
        if file_url:
            msg+='[**研究成果地址**] (%s) | '%(file_url)
        else:
            msg+='**研究成果地址**：❌ 无 | '
        if fld_url:
            msg+='[**成果库地址**] (%s)\n'%(fld_url)
        else:
            msg+='**成果库地址**： ❌ 无\n'
        
        epic=parent.fields.__dict__.get('customfield_11412',None)
        msg+='**所属世界线**：'
        if epic:
            name=''
            epics=epic.split(', ')
            for i in epics:
                e=jira.issue(i)
                s='[**%s**] (%s) | '%(e.fields.summary,e.permalink())
                name+=s
            msg+=name[:-2]+'\n'
        else:msg+='无\n'
        annu_earns=parent.fields.__dict__.get('customfield_11438',None)
        if annu_earns:
            annu_earns=round(annu_earns,3)
            msg+='**全情景年化收益率**：%s\n'%annu_earns

        evband=parent.fields.__dict__.get('customfield_11108',None)

        if evband:

            evband=evband.replace('<br>','\n\t')
            evband='\t'+evband
            msg+='**X和市值258分位**：\n%s\n'%evband
        else:msg+='**X和市值258分位**：无\n'
        desc=issue.fields.__dict__.get('description',None)
        if desc:
            if not re.search('[0-9]',desc):
                msg+='**主要内容 ❌  缺失 ❌  !!**\n'
            else:
                desc=star2holder(desc)
                desc=desc.replace(r'*','')
                #desc=re.sub(r'\*([^\*]+)\*',r'\1',desc)
                #desc=desc.replace('\n','\n\t')
                desc=desc
                msg+='\n --------------\n**主要内容**：\n%s\n'%desc
                msg+='\n --------------\n'
        else:msg+='**主要内容 ❌ 缺失 ❌ !!**\n'
        msg+='**成果库检查结果**：\n'
        dic={}
        if file_url and fld_url:
            
            fld=re.search('fld\w*', fld_url,)
            file=re.search('doc(x|s)/\w*', file_url,)
            if fld and file:
                fld_token=fld[0]
                file_token=file[0][5:]
            #print(fetch_folder_meta(fld_token))
                r=fetch_folder_meta(fld_token)
                #print(r)
                if r['code']==0:
                    fld_name=r['data']['name']
                else :
                        msg=msg[:-13]
                        errormsg='调用文件夹遍历api失败，自动刷新token并重试 .\njira info:%s'%summary
                        errormsg+='\n feishu api response:%s'%r['msg']
                        text_group_msg(msg=errormsg,webhook=webhook_dict['Debug群juno'])
                        r=refresh()
                        print(r)
                        if r=='1':
                            #check_file(issueid=issueid)
                            text_group_msg(msg='token刷新成功')

                            return {'res':'notgood'},msg,title
                        else:
                            return redirect(url_for('fsback.feishu_login'))
                if summary_name in fld_name:
                    result1=True
                else:
                    result1=False
                    msg+=f'❌ ❌ ❌  代码匹配失败！jira项目名为：{summary},文件夹代码为：{fld_name}\n'
                page_token=None
                while True:
                    r=fetch_folder_children(fld_token,page_token=page_token)
                    if r['code']==0:
                        dic=analaze_folder(r,dic)
                                
                        if not r['data']['has_more']:
                            break
                        else:
                            page_token=r['data']['next_page_token']
                    else :
                        msg=msg[:-13]
                        errormsg='调用文件夹遍历api失败，自动刷新token并重试 .\njira info:%s'%summary
                        errormsg+='\n feishu api response:%s'%r['msg']
                        text_group_msg(msg=errormsg,webhook=webhook_dict['Debug群juno'])
                        r=refresh()
                        print(r)
                        if r=='1':
                                                      #check_file(issueid=issueid)
                            text_group_msg(msg='token刷新成功')

                            return {'res':'notgood'},msg,title                        
                        else:
                            return redirect(url_for('fsback.feishu_login'))
                file_info=dic.get(file_token)
                #print(file_info)
                
                
                if file_info:
                    result2=True
                    urls=None
                else:     
                    result2=False
                    msg+='❌ ❌ ❌  文件检查失败！成果库查找不到对应文档，请确认文档保存位置正确/是否为快捷方式'
                    
                    urls=[file_url,fld_url]  
                if result1 and result2:
                    msg=msg[:-1]
                    msg+='成果库归档检查通过！'
                
            else:
                
                msg+='❌ ❌ ❌  字段网址似乎不合规，请确认jira中“研究成果地址”和“成果库地址”已正确填写'
                
                urls=[file_url,fld_url]
            #print(msg)
        else:
            
            msg+='❌ ❌ ❌  字段信息似乎不完整，请确认jira中“研究成果地址”和“成果库地址”都已填写'
            urls=None    
    elif issue.fields.project.key=='WORLDEPICSTUDY':

        issue_key=issue.key
        fld_url=issue.fields.__dict__.get('customfield_11000',None)
        
        file_url=issue.fields.__dict__.get('customfield_11302',None)
        summary=issue.fields.summary
        
        try:
            summary_name=re.findall(r'[\u4e00-\u9fa5]+',summary)[0]
        except:
            summary_name=''
            
        
        try:
            people=issue.fields.customfield_11100
            if type(people)==list:
                person=[person.displayName for person in people]
                s=''
                for p in person:
                    s+=p+','
                person=s[:-1]
            else:
                person=people.displayName
        except:
            person='无'
        url=issue.permalink()
        
        title='世界线研究成果 - %s '%(summary)
        msg='**研究主责人**：%s\n'%person
        msg+='**相关链接**： \n'
        msg+='[**jira项目地址**] (%s) | '%(url)
        if file_url:
            msg+='[**研究成果地址**] (%s) | '%(file_url)
        else:
            msg+='**研究成果地址**：❌ 无 | '
        if fld_url:
            msg+='[**成果库地址**] (%s)\n'%(fld_url)
        else:
            msg+='**成果库地址**： ❌ 无\n'

        parent=issue.fields.__dict__.get('customfield_11415',None)
        children=issue.fields.__dict__.get('customfield_11414',None)
        msg+='**相关世界线**：\n'
        if not (parent or children):
            msg+='无\n'
        else:
            if parent:
                msg+='父世界线——'
                name=''
                parents=parent.split(', ')
                for i in parents:
                    e=jira.issue(i)
                    s='[**%s**] (%s) | '%(e.fields.summary,e.permalink())
                    name+=s
                msg+=name[:-2]+'\n'
            if children:
                msg+='子世界线——'
                name=''
                children=children.split(', ')
                for i in children:
                    e=jira.issue(i)
                    s='[**%s**] (%s) | '%(e.fields.summary,e.permalink())
                    name+=s
                msg+=name[:-2]+'\n'
        desc=issue.fields.__dict__.get('description',None)
        if desc:

                desc=star2holder(desc)
                #desc=re.sub(r'\*([^\*]+)\*',r'\1',desc)
                desc=desc.replace(r'*','')
                desc=desc.replace('\n','\n\t')
                desc='\t'+desc
                msg+='\n --------------\n**主要内容**：\n%s\n'%desc
                msg+='\n --------------\n'
        else:msg+='**主要内容 ❌ 缺失 ❌ !!**\n'

    
        msg+='**成果库检查结果**：\n'
        dic={}
        if file_url and fld_url:
            
            fld=re.search('fld\w*', fld_url,)
            file=re.search('doc(x|s)/\w*', file_url,)
            if fld and file:
                fld_token=fld[0]
                file_token=file[0][5:]
            #print(fetch_folder_meta(fld_token))
                r=fetch_folder_meta(fld_token)
                #print(r)
                if r['code']==0:
                    fld_name=r['data']['name']

                page_token=None
                while True:
                    r=fetch_folder_children(fld_token,page_token=page_token)
                    if r['code']==0:
                        dic=analaze_folder(r,dic)
                                
                        if not r['data']['has_more']:
                            break
                        else:
                            page_token=r['data']['next_page_token']
                    else :
                        if int(r['msg'])==1061007:
                            '''文件夹不存在,回复文件查找错误'''
                            dic={}
                            break
                            
                        else:
                            msg=msg[:-13]
                            errormsg='调用文件夹遍历api失败，请刷新token并重试 .\njira info:%s'%summary
                            errormsg+='\n feishu api response:%s'%r['msg']
                            text_group_msg(msg=errormsg,webhook=webhook_dict['Debug群juno'])
                            r=refresh()
                            print(r)
                            if r=='1':
                                #check_file(issueid=issueid)
                                text_group_msg(msg='token刷新成功')

                                return {'res':'notgood'},msg,title
                            else:
                                return redirect(url_for('fsback.feishu_login'))
                file_info=dic.get(file_token)
                #print(file_info)
                
                
                if file_info:
                    result1=True
                    msg=msg[:-1]
                    msg+='成果库归档检查通过！'
                    urls=None
                else:     
                            
                    msg+='❌ ❌ ❌  文件检查失败！成果库查找不到对应文档，请确认文档保存位置正确/是否为快捷方式'
                    
                    urls=[file_url,fld_url]  
                    
                
            else:
                
                msg+='❌ ❌ ❌  字段网址似乎不合规，请确认jira中“研究成果地址”和“成果库地址”已正确填写'
                
                urls=[file_url,fld_url]
            #print(msg)
        else:
            
            msg+='❌ ❌ ❌  字段信息似乎不完整，请确认jira中“研究成果地址”和“成果库地址”都已填写'
            urls=None
        pass
        #print(msg,urls)
    else:
        text_group_msg('jira issue类别错误，查询的issuetype为：%s'%issue.fields.project.name,webhook=webhook_dict['Debug群juno'])
        return False
    
    return dic,msg,title
@fsback.route('/check_file',methods=['GET','POST'])

def check_file(issueid=None,receive_id=None):
    '''发过来研究任务的子任务，其中世界线/258分位在父任务字段里，父任务需要从fields.parent重新找issue'''
    #print(request.args)
    from jira import JIRA
    import re

    #print(request.args)
    jira = JIRA('https://research.quantumgalaxy.cn/',
                basic_auth=('bot2', "jira_bot2"))
    if not issueid:
        issueid=request.args.get('issueid',None)
    if not receive_id:
        receive_id=request.args.get('receive_id',None)
    import time
    time.sleep(5)
    try:
        issue=jira.issue(issueid)
        
    except:
        text_group_msg(msg='jira连接错误或根据id查询的jira issue。查询id为:%s'%issueid,webhook=webhook_dict['Debug群juno'])
        return 'no found issue'
    try:
        dic,msg,title=handle_issue(issue,jira,issueid)
    except:
        return 'error wher handle issue'
    #print('%s'%receive_id)
    r=build_send_msg_card(text=msg,title=title,receive_id=receive_id)
    #print(r)
    return dic