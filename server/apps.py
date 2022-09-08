# %%
import re
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.feishu import FeishuAPI
feishu=FeishuAPI()
def assistant(content,sender):
    '''解析文字内容，验证是不是有效代码，有效代码则添加到表里，生成回复'''
    try:
        code=re.findall(r"([a-zA-Z0-9]+\.+[a-zA-Z0-9]+)",content)[0]
        feishu.append_table(table_id='shtcnLWuQvuf7Bd2PoajBwYgaQh',data_list=[code,sender],sheet_id='72bcb0',table_range='A2:B2')
        msg='解析到万得代码："%s"，如代码无误请耐心等待，每个整点系统将发送ppt到本会话中，谢谢使用。查看当前待处理任务清单请点击：%s'%(code,'https://quantumgalaxy.feishu.cn/sheets/shtcnLWuQvuf7Bd2PoajBwYgaQh?sheet=72bcb0')
    except:
        msg='无法从消息中解析到有效代码，请检查'
    return msg

    



