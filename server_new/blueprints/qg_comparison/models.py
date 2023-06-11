import requests,json
from copy import deepcopy
from ..live_editor.models import bitable_works
def get_files(fold_token):
    #logger.info('开始检查文件，文件夹地址为　https://quantumgalaxy.feishu.cn/drive/folder/%s'%fold_token)
    r0=requests.get('http://82.156.248.152:81/fs/fold_meta?token=%s'%fold_token).json()
    
    r1=requests.get('http://82.156.248.152:81/fs/fold_children?fld_token=%s'%fold_token).json()
    if r0['code']==0 and r1['code']==0:
        files=r1['data']['files']
        data={}
        for file in files:
            if file['name'] not in ['电力储能骨干核心表Demo','xx骨干核心表模板及范例']:
            #if file['type']=='bitable' and '核心表' in file['name'] and file['name']!='xx骨干核心表Demo':
            #if True:
                data[file['name']]=file['token']
            else:
                 pass
                #logger.warning('排除该文件，类型:%s,名称:%s'%(file['type'],file['name']))
        num=len(data)
        
        #logger.info('检查文件夹成功，共查到%d张多维表格参与联查，如下：'%num)
        #for d in data.keys():
            #logger.info(d)
        
        return {'code':0,'data':data}
    else:
        #logger.info('检查文件夹失败，检查地址')
        return {'code':r0['code'],'data':r0}
def get_mark(backbone_mark):
    if backbone_mark:
        mark=[]
        
        for record in backbone_mark:
            fields=record['fields']
            #print(fields)
            if fields['本骨干标记']:
                mark.append(fields['骨干名'])
        if mark:
            if len(mark)==1:
                return (True,mark[0])

            else:
                return (False,'找到复数勾选骨干：%s'%mark)
        else:
            return (False,'没有勾选骨干标记')
    else:
        return (False,'没有勾选本骨干')
def internal_check(bitapp_token):
    '''对多维表格data进行内部检查，梳理出所有外部节点和其对应边，其中孤立外部节点加入error，多层外部节点加入warning，其他加入external,并把原data中其他数据分类到
    'internal_links':[],'external_links':[],'warning_links':[],'error_nodes':[],'internal_nodes':[],'external_nodes':[],
    加上骨干标记'''
    fold='fldcn2VlYvt8Efb9PqZwO51GWud'
    files=get_files(fold)
    if files['code']==0:
            files=files['data']
    #files
    data=bitable_works(bitapp_token)
    #data
    resulttext='对多维表格内部进行检查：<br>'
    result={'internal_links':[],'external_links':[],'warning_links':[],'error_links':[],'error_nodes':[],'internal_nodes':[],'external_nodes':[]}
    r,mark=get_mark(data['backbone_mark'])
    if r:
        #logger.critical('本骨干标记：')
        #logger.critical(mark)
        resulttext+=f'本骨干标记：{mark}<br>'
        result['backbone_mark']=mark
    else:
        body='检查到骨干定义表问题：%s<br>'%mark
        resulttext+=body
        #report_df=append_df(report_df,['error',body,mark,True])
        return None,None
    
    #result.update(data)
    for link in data['links']:
        if not link['category'] in ['原材料','储运','父节点','供应','同位','生产','反映']:
            link['error']=True
            result['error_links'].append(link)
            body='该边的关系有误：“%s”<br>'%link['category']
            resulttext+=body
            #report_df=append_df(report_df,['error',body,mark,True])
        for o in data['nodes']:
            if o['bitapp_id']==link['target']:
                link['target_name']=o['name']
            if o['bitapp_id']==link['source']:
                link['source_name']=o['name']
        if not (link.get('target_name') and link.get('source_name')):
            link['error']=True
            result['error_links'].append(link)
            body='出现边没有找到对应的起/终点，可能是因为起终点没有勾选粗骨干权限。id:"%s",起点："%s" 终点:"%s"<br>'%(link.get('bitapp_id'),link.get('source_name_ref','unknown'),link.get('target_name_ref','unknown'))
            resulttext+=body
            #report_df=append_df(report_df,['error',body,mark,True])
            
    for node in data['nodes']:
        if not node['more_info'].get('external_backbone'):
            result['internal_nodes'].append(node)
        else:
            
            id=node['bitapp_id']
            backbone=node['more_info'].get('external_backbone')

            if backbone:
                backbone=backbone[0]
            check=0
            if not files.get(backbone,None):
                '''该外部节点的‘所属外部骨干’字段与文件目录files比对结果，因此要求字段内骨干名与files名一致，不然认为没有找到外骨干'''
                '''涉及errornode的边移入errorlink'''
                resulttext+='“%s”节点没有找到对应的外部骨干：“%s”<br>'%(node['name'],backbone)
                #error
                result['error_nodes'].append(node)
                for link in data['links']:
                    if link['source']==id or link['target']=='id':
                        if link['source']==id :
                            other=link['target']
                            for o in data['nodes']:
                                if o['bitapp_id']==other :
                                    #link['source_name']=node['name']
                                    #link['target_name']=o['name']
                                    link['external_backbone_name']=backbone
                                    #link['external_backbone']=files.get(backbone,'未知')
                        else:
                            other=link['source']
                            for o in data['nodes']:
                                if o['bitapp_id']==other :
                                    #link['source_name']=o['name']
                                    #link['target_name']=node['name']
                                    link['external_backbone_name']=backbone
                                    #link['external_backbone']=files.get(backbone,'未知')
                        result['error_links'].append(link)
                        body='因“%s”节点没有找到对应外部骨干，与其相连的边也出错,不参与联调：[%s]-(%s)->[%s]<br>'%(node['name'],link['source_name'],link['category'],link['target_name'])
                        resulttext+=body
                        #report_df=append_df(report_df,['error',body,mark,True])
                        link['error']=True
            else:
                result['external_nodes'].append(node)

                for link in data['links']:
                    
                        if link['source']==id :
                            
                            #从data中除去该边，只留纯外边
                            other=link['target']
                            for o in data['nodes']:
                                if o['bitapp_id']==other :
                                        
                                        
                                        link['source_name']=node['name']
                                        link['target_name']=o['name']
                                        link['external_backbone_name']=backbone
                                        #link['external_backbone']=files.get(backbone,'未知')
                                        if not (o['more_info'].get('external_backbone') or o['category']=='指标'):
                                            #说明另一点为内部
                                            link1=deepcopy(link)
                                            link1.pop('source')
                                            #logger.info('检查到与“%s”骨干间的正确星图边界：[%s]-(%s)->[%s]'%(backbone,link['source_name'],link['category'],link['target_name']))
                                            result['external_links'].append(link1)
                                            check=max(check,2)
                                            
                                        else:
                                        
                                            if not link.get('checked'):
                                                result['warning_links'].append(link)
                                                #说明另一点为外部,该边加入warning
                                                body='检查到本骨干之外的,属于“%s”骨干的边，该边不参与冲突检查：[%s]-(%s)->[%s]<br>'%(backbone,link['source_name'],link['category'],link['target_name'])
                                                resulttext+=body
                                                #logger.warning(body)
                                                #report_df=append_df(report_df,['warning',body,mark,True])
                                            check=max(check,1)
                                        continue
                            link['checked']=True

                                
                                
                        elif link['target']==id:
                            
                            other=link['source']
                            for o in data['nodes']:
                                if o['bitapp_id']==other:
                                        
                                        
                                        link['source_name']=o['name']
                                        link['target_name']=node['name']
                                        link['external_backbone_name']=backbone
                                        #link['external_backbone']=files.get(backbone,'未知')
                                        if not (o['more_info'].get('external_backbone') or o['category']=='指标'):
                                            #说明另一点为内部,该边加入external
                                            link1=deepcopy(link)
                                            link1.pop('target')
                                            #logger.info('检查到与“%s”骨干间的正确星图边界：[%s]-(%s)->[%s]'%(backbone,link['source_name'],link['category'],link['target_name']))
                                            result['external_links'].append(link1)
                                            check=max(check,2)
                                            
                                        else:
                                            
                                            if not link.get('checked'):
                                                
                                                result['warning_links'].append(link)
                                                #说明另一点为外部,该边加入warning
                                                body='检查到本骨干之外的,属于“%s”骨干的边，该边不参与冲突检查：[%s]-(%s)->[%s]<br>'%(backbone,link['source_name'],link['category'],link['target_name'])
                                                resulttext+=body
                                                #logger.warning(body)
                                                #report_df=append_df(report_df,['warning',body,mark,True])
                                            check=max(check,1)
                                        continue
                            link['checked']=True
                        else:
                            #result['internal_links'].append(link)
                            #print('''所有边均未触发则error 该外部节点为孤立，未连入当前骨干''')
                            pass
                            
                            '''所有边均未触发则error 该外部节点为孤立，未连入当前骨干'''
                        
                if check==2:
                    #ok
                    pass
                elif check==1:
                    #warning
                    pass
                else:
                    body='检查到孤立外骨干节点，该点为内部错误，不参与冲突检查：%s<br>'%node['name']
                    print(body)
                    resulttext+=body
                    #report_df=append_df(report_df,['error',body,mark,True])
                    #error
                    result['error_nodes'].append(node)
                    pass
    for link in data['links']:
                if not link.get('checked'):
                    if not link.get('error'):
                        #没有check表示起终点均不是外部
                        result['internal_links'].append(link)
    #print(resulttext)
    return resulttext
#data1=deepcopy(data)
#internal_check(data1)
            
def get_xml_data(raw):
    r=requests.post('http://82.156.248.152:82/backbone_check/work',json=json.dumps({'name':'','graph':raw}))
    xml_data=r.json()['data']
    for k,v in xml_data['vertex'].items():
        v['category']=v['cate_ch']
    #{'data': {'edge': {}, 'other': [], 'vertex': {}}, 'result': ''}
    return xml_data
def get_graph_data(bitapp_id,region,rough_backbone,except_cop,except_ind):
    #bitapp_id='bascnzsAjUXwr4gUkaIpqi8BBaf'
    r=requests.post('http://82.156.248.152:82/xml/work',json=json.dumps({'bitapp_id':bitapp_id,'region':region,'rough_backbone':rough_backbone,'except_cop':except_cop,'except_ind':except_ind}))
    graph_data_raw=r.json()
    if graph_data_raw['code']==0:
        nodes=deepcopy(graph_data_raw['result']['nodes'])
        links=deepcopy(graph_data_raw['result']['links'])
        vertex={}
        edge={}
        for node in nodes:
            bitapp_id=node.pop('bitapp_id')
            vertex[bitapp_id]=node
        for link in links:
            bitapp_id=link.pop('bitapp_id')
            link['name']=link.pop('category')
            edge[bitapp_id]=link
        graph_data={'vertex':vertex,'edge':edge}
        
        return graph_data
    else:
        return {'vertex':{},'edge':{}}
    


def issame(props):
   return True if props[0]==props[1] else False
def compare_node(nodes:list):
   #[xmlnode,graphnode]
   x,g=nodes
   try:
      if x.get('code'):
         if issame([x['name'],g['name']]) and issame([x['category'],g['category']]) and issame([x['code'],g.get('code')]):
            return True
         else:return False
      else:
         if issame([x['name'],g['name']]) and issame([x['category'],g['category']]) and not g.get('code'):
            return True
         else:return False
   except Exception as e:
      print(e)
      return False
#找流程图中节点

def compare_data(xml_data,graph_data,conflicts):
    for xml_vid,xml_v in xml_data['vertex'].items():
        get_samenode=False

        #找每个节点的对应节点
        for graph_vid,graph_v in graph_data['vertex'].items():
            
            if compare_node([xml_v,graph_v]):
                get_samenode=True
                #print(xml_v['name'])

                #遍历并找节点的相邻边
                for xml_eid,xml_edge in xml_data['edge'].items():
                    if xml_edge['source']==xml_vid or xml_edge['target']==xml_vid:

                        xml_direction=1 if xml_edge['source']==xml_vid else -1
                        try:
                            #当边被识别但起点终点有问题时会找不到
                            
                            xml_source=xml_data['vertex'][xml_edge['source']]
                            xml_target=xml_data['vertex'][xml_edge['target']]
                        except:
                            conflicts['error'].append(xml_edge)
                            print('*'*20+str(xml_edge))
                            continue

                        xml_edgename=xml_edge['name']

                        #print('待比对边：',xml_source['name'],'-',xml_edgename,'->',xml_target['name'])
                        
                        #遍历并找对应节点的相邻边
                        get_sameedge=False
                        for graph_eid,graph_edge in graph_data['edge'].items():
                            
                            if graph_edge['source']==graph_vid or graph_edge['target']==graph_vid:
                                #print(graph_edge)
                                graph_direction=1  if graph_edge['source']==graph_vid else -1
                                try:
                                    #同样问题，有边无点
                                    graph_source=graph_data['vertex'][graph_edge['source']]
                                    graph_target=graph_data['vertex'][graph_edge['target']]
                                except:
                                    #print(str(graph_edge)+'*&'*20)
                                    continue
                                graph_edgename=graph_edge['name']
                                #print(graph_source,graph_edgename,graph_target)
                                #print([xml_source,graph_source])
                                #print(compare_node([xml_source,graph_source]) and compare_node([xml_target,graph_target]))
                                if compare_node([xml_source,graph_source]) and compare_node([xml_target,graph_target]) and graph_edgename==xml_edgename:
                                    get_sameedge=True
                                    #print('找到一致边')
                                    pass
                                    
                        if not get_sameedge:
                            #没有对应的时候需要找到 有冲突的点和边
                            #print('\n该边没有对应，是流程图多出来的\n')
                            
                            
                            if xml_direction==1:
                                #此时target为冲突边界的点
                                xml_data['vertex'][xml_edge['target']]['checked']=-1
                                #print(xml_source['name'],'***','-',xml_edgename,'->',xml_target['name'],'***')
                                conflicts['borderline'].append({'direction':xml_direction,'source':xml_source,'target':xml_target,'relation':xml_edgename})
                            else:
                                
                                xml_data['vertex'][xml_edge['source']]['checked']=-1
                                #print('***',xml_source['name'],'-',xml_edgename,'->','***',xml_target['name'])
                                conflicts['borderline'].append({'direction':xml_direction,'source':xml_source,'target':xml_target,'relation':xml_edgename})
                                #print(xml_data['vertex'][xml_edge['target']])
        




        if get_samenode:
            xml_data['vertex'][xml_vid]['checked']=1


        #else:print('流程图多余节点：',xml_v['name'])
    for xml_vid,xml_v in xml_data['vertex'].items():
        if xml_v.get('checked'):
            #print(xml_v.get('checked'))
            pass
        else:
            print('流程图多余节点：',xml_v['name'])
            conflicts['others'].append(xml_v)
    return conflicts
def work(xml_data,graph_data):
    
    conflicts={'borderline':[],'others':[],'error':[]}

    if not xml_data['vertex']:
        return {'code':-1,'res':'流程图解析失败'}
    elif not graph_data['vertex']:
        return {'code':-2,'res':'多维表格解析失败'}
    else:


        xml_conflicts=compare_data(xml_data,graph_data,deepcopy(conflicts))
        for k,v in xml_conflicts.items():
            for vv in v:
                vv['origin']='xml'
        graph_conflicts=compare_data(graph_data,xml_data,deepcopy(conflicts))
        for k,v in graph_conflicts.items():
            for vv in v:
                vv['origin']='graph'

        conflicts['borderline']=xml_conflicts['borderline']+graph_conflicts['borderline']
        conflicts['others']=xml_conflicts['others']+graph_conflicts['others']
        conflicts['error']=xml_conflicts['error']+graph_conflicts['error']
        return {'code':0,'res':conflicts}
def conflicts2text(conflicts):
    #<font color="#FF0000">我是红色字体</font> 
    '''需要分开并排序xml和graph来源的'''
    result=''
    if conflicts['error']:
        result+='<br><font color="#FF0000">***流程图中存在以下不合法元素未进行比对，请先在飞书流程图审核工具检查***</font><br>'
        for e in conflicts['error']:
            result+=str(e)+'<br>'
        result+='<br> <br>'
    if conflicts['borderline']:

        for b in conflicts['borderline']:
            if b['origin']=='xml':
                result+='流程图中有冲突边&nbsp;&nbsp;'
                if b['direction']==1:
                    result+=f"""{b['source']['name']}:{b['source']['category']}-<font color="#FF0000">{b['relation']}-&gt;{b['target']['name']}:{b['target']['category']}</font>"""
                else:
                    
                    result+=f"""<font color="#FF0000">{b['source']['name']}:{b['source']['category']}-{b['relation']}-&gt;</font>{b['target']['name']}:{b['target']['category']}"""
            else:
                result+='多维表中有冲突边&nbsp;&nbsp;'
                if b['direction']==1:
                    result+=f"""{b['source']['name']}:{b['source']['category']}-<font color="#0000FF">{b['relation']}-&gt;{b['target']['name']}:{b['target']['category']}</font>"""
                else:
                    
                    result+=f"""<font color="#0000FF">{b['source']['name']}:{b['source']['category']}-{b['relation']}-&gt;</font>{b['target']['name']}:{b['target']['category']}"""
            result+='<br>'
    
    if conflicts['others']:
        result+='<br>***先修改完所有冲突边，并重新比对后再关注冲突点***<br>'
        for o in conflicts['others']:
            if o.get('code'):o['name']+='('+o['code']+')'
            if o['origin']=='xml':
                result+='<font color="#FF0000">流程图中有冲突点</font>&nbsp;&nbsp;'
            else:
                result+='<font color="#0000FF">多维表中有冲突点</font>&nbsp;&nbsp;'

            
            result+=f"{o['name']}:{o['category']}"+'<br>'

            #result=conflicts['others']

    if not conflicts['borderline'] and not conflicts['others'] and not conflicts['error']:
        result+='当前流程图与多维表格所选范围的内容完全一致，没有冲突'
    return result



