from urllib.parse import unquote
import re,html
def item_reader(s:str):
    
    #print(s)
    try:
        
        if re.findall('vertex="1"',s):
            
            if (not re.findall('diagramName',s)) or  re.findall('diagramName="RoundedRectangle"',s):
                print(s)    
                external='外部节点' if  re.findall('diagramName="RoundedRectangle"',s) else None
                info=re.search('id="(.*?)" value="(.*?)" .*fillColor=(.*?);.*x="(.*?)".*y="(.*?)".*',s)
                id,name,color,x,y=info.group(1),info.group(2),info.group(3),info.group(4),info.group(5)
                try:
                    
                    name=html.unescape(name)
                    #print(name)
                    if '<br' in name or '</div' in name:
                        a=re.search('(.*?)<(br|/div).*?>(.*)',name)
                        if a:
                         
                            name,code=a.groups()[0],a.groups()[2]
                            
                            name=re.sub('<.*?>','',name)
                            code=re.sub('<.*?>','',code)
                            return {'id':id,'type':'vertex','name':name,'color':color,'code':code,'x':x,'y':y,'external':external}
                        else:return {'id':'unknown','type':'error','string':s}
                    else:
                        name=re.sub('<.*?>','',name)
                        return {'id':id,'type':'vertex','name':name,'color':color,'x':x,'y':y,'external':external}
                except:
                    return {'id':id,'type':'error','string':s}
            
                
        elif re.findall('edge="1"',s):
            info=re.search('id="(.*?)" value="(.*?)".*source="(.*?)" target="(.*?)"',s)
            id,name,source,target=info.group(1),info.group(2),info.group(3),info.group(4)
            try:
                name=html.unescape(name)
                if '<br' in name:
                        '''some edge like "<br style="font-size: 15px;">"'''
                        a=re.search('(.*?)<br.*?>(.*)',name)
                        if a:
                         
                            name,info=a.groups()[0],a.groups()[1]
                            name=re.sub('<.*?>','',name)
                            return {'id':id,'type':'edge','name':name,'source':source,'target':target,'info':info}
                        else:return {'id':'unknown','type':'error','string':s}
                else:
                    
                    name=re.sub('<.*?>','',name)
                    
                    return {'id':id,'type':'edge','name':name,'source':source,'target':target}
            except:
                return {'id':id,'type':'error','string':s}
        else:
            return {'id':'unknown','type':'error','string':s}
    except:
        return{'id':'unknown','type':'error','string':s}
def graph_recognizer(s:str):
    '''复制飞书流程图（本质为mxgraph描述）并解析成点和边元素,生成图json？和文字报告'''
    
    

    input=unquote(s, 'utf-8')
    items=re.findall('<mxCell .*?/>',input)
    #拆分出n个可识别，有id的元素 其中有value的合法，再其中有vertex/edge且能获取相关信息的为正确元素
    valid_items=[]
    invalid_items=[]
    for i in items:
        if 'value'   in i:
            valid_items.append(i)
        else:
            invalid_items.append(i)

    data={}
    vertexes={}
    edges={}
    others=[]
    for i in valid_items:
        try:
            item=item_reader(i)
            t=item.pop('type')
            id=item.pop('id')
            if t=='vertex':
                vertexes[id]=item
                
            elif t=='edge':
                edges[id]=item
            else:
                others.append(item)
        except:
            invalid_items.append(i)

    data['vertex']=vertexes
    data['edge']=edges
    data['other']=others
    return data
def data_mapper(data):
    '''将节点通过颜色分类，将边的起终点id对应为节点名,将边的关系存储为英文'''
    '''工艺 #999999
    需求 #CC0000
    产品 #0362A1
    公司 #ffffff'''
    color2type={'#ffffff':'Company','#FFFFFF':'Company',
        '#0362A1':'Product',
        '#CC0000':'Demand',
        '#999999':'Technique','#CCCCCC':'Technique',
        '#FFB570':'Indicator','#FFFFCC':'Indicator'}
    nodetype={'Company':'企业','Product':'产品','Demand':'需求','Indicator':'指标','Technique':'工艺',}
    edgetype={'原材料':'compose','父节点':'parent','生产':'produce','反映':'measure','measure':'measure','供应':'supply','储运':'carry','同位':'peer'}
    for dic in data['vertex'].values():
        try:
            dic['category']=color2type[dic['color']]
            dic['cate_ch']=nodetype[dic['category']]
            
        except:
            dic['category']='unknown'
        dic.pop('color')
    for dic in data['edge'].values():
        try:
            #dic['rela']=edgetype[dic['name']]
            pass
        except:
            dic['rela']=dic['name']
        try:
            dic['sourcename']=data['vertex'][dic['source']]['name']
        except:
            dic['sourcename']=dic['source']
        try:
            dic['targetname']=data['vertex'][dic['target']]['name']
        except:
            dic['targetname']=dic['target']
    return data
def data2text(data):
    num_i=len(data['indicator'])
    num_v=len(data['vertex'])
    num_e=len(data['edge'])
    num_o=len(data['other'])
    num=num_v+num_e+num_o+num_i
    text='解析飞书流程图结果如下:\n总获取到合法数据%s条\n'%num
    text+='正确节点%s个\n'%num_v
    for v in data['vertex'].values():
        text+= v['name']+'\t'+v['category']+'\n'
    text+='\n\n'
    text+='正确指标%s个\n'%num_i
    for v in data['indicator'].values():
        text+= v['name']+'\t'+v['code']+'\n'
    text+='\n\n'
    text+='正确边%s个\n'%num_e
    for v in data['edge'].values():
        text+= v['sourcename']+'--['+v['name']+']->'+v['targetname']+'\n'
    text+='\n\n'
    text+='存疑数据%s条\n'%num_o
    for v in data['other']:
        text+=html.escape(str(v))+'\n'

    text = text.replace('\n','<br/>')



    #text = text.replace(' ',"&nbsp;");


    return text
def add_backbone(data,name):
    for v in data['vertex'].values():
        v['backbone']=name
    return data
def data_check(data):
    ''' 换行（有代码问题） 重复连线问题 公司和指标无代码问题'''
    error_vertex=[]
    error_edge=[]
    checkedge=[]
    for k,v in data['vertex'].items():
        if v['category']=='unknown':
            #errordata=testdata['vertex'].pop(k)
            error_vertex.append(k)
            errordata=v
            errordata['error']='节点类别无法匹配，可能是元素有误'
            data['other'].append({k:errordata})            
        if v.get('code') and v['category'] not in ['Indicator','Company']:
            #errordata=testdata['vertex'].pop(k)
            error_vertex.append(k)
            errordata=v
            errordata['error']='非公司/指标节点带有code，可能是存在人工换行，请检查'
            data['other'].append({k:errordata})
        if v['category'] in ['Indicator','Company'] and not v.get('code'):
            error_vertex.append(k)
            errordata=v
            errordata['error']='公司/指标节点没有找到code，可能是忘记填写或忘记换行，请检查'
            data['other'].append({k:errordata})
    for k,v in data['edge'].items():
        
        if (v['sourcename'],v['targetname']) in checkedge or (v['targetname'],v['sourcename']) in checkedge:
            error_edge.append(k)
            errordata=v
            errordata['error']='发现有重复连线，请检查'
            data['other'].append({k:errordata})
        checkedge.append((v['sourcename'],v['targetname']))
        pass
    for v in error_vertex:
        try:
            data['vertex'].pop(v)
        except:
            pass
    for v in error_edge:
        try:
            data['edge'].pop(v)
        except:
            pass
    return data
def split_data(data):
    '''将data中节点表拆成一般节点和指标表'''
    data['indicator']={}
    indi_keys=[]
    reflect_links=[]
    for k,v in data['vertex'].items():
        if v['category']=='Indicator':
            data['indicator'][k]=v
            indi_keys.append(k)
    for k in indi_keys:
        print('pop')
        data['vertex'].pop(k)
    for k,v in data['edge'].items():
        if v['name']=='反映':
            reflect_links.append(k)
            try:
                ind=v['source']
                data['indicator'][ind]['reflect_node_name']=v['targetname']
            except:
                pass
    for k in reflect_links:
        data['edge'].pop(k)

    return data
def xml2graph_worker(string,name):
    data=graph_recognizer(string)
    data=data_mapper(data)
    data=add_backbone(data,name)
    data=data_check(data)
    data=split_data(data)
    #json.dumps(data)
    print(data['other'])
    result=data2text(data)
    print(result)
    return result,data
