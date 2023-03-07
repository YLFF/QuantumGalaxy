from . import bitapp_auth
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
'''多维表格：
    多维表格apptoken
            app元数据
    数据表tabletoken
            列出数据表 /open-apis/bitable/v1/apps/:app_token/tables
    视图view
             /open-apis/bitable/v1/apps/:app_token/tables/:table_id/views
    记录reocrd
             /open-apis/bitable/v1/apps/:app_token/tables/:table_id/records
             https://open.feishu.cn/open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id
            
            '''
def fetch_metadata(app_token):
    headers=build_headers()
    url='https://open.feishu.cn/open-apis/bitable/v1/apps/%s'%(app_token)
    
    r=base_fetch_func(url,headers=headers,method='get')
    
    return r
def fetch_table_records(app_token,table_id,**kwargs):
    '''reference:https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/list
    路径参数，kwargs:
    filter 示例值："AND(CurrentValue.[身高]>180, CurrentValue.[体重]>150)"
    field_names 字段名称，用于指定本次查询返回记录中包含的字段 示例值："["字段1","字段2"]"
    page_token 分页标记，第一次请求不填，表示从头开始遍历；分页查询结果还有更多项时会同时返回新的 page_token，下次遍历可采用该 page_token 获取查询结果 示例值："recn0hoyXL"         
    page_size  默认值：20 数据校验规则：最大值：500
    
    '''
    
    headers=build_headers()
    url='https://open.feishu.cn/open-apis/bitable/v1/apps/%s/tables/%s/records'%(app_token,table_id)
    
    r=base_fetch_func(url,headers=headers,params=kwargs,method='get')
    
    return r
def fetch_app_tables(app_token):
    headers=build_headers()
    url='https://open.feishu.cn/open-apis/bitable/v1/apps/%s/tables'%app_token
    r=base_fetch_func(url,headers,method='get')
    return r
def build_headers():
    
    token=fetch_tenant_token(bitapp_auth)
    #token='u-3atGsodiN9391_BlvmfeZh1kkwt5hlQxo0G0hgew2Ijc'
    headers = {
        'Authorization':
        'Bearer ' + token,  # your access token
        #'Content-Type': 'application/json; charset=utf-8'
    }
    return headers
