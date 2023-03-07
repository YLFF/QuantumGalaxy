from utils import get_mysql
from base64 import b64decode,b64encode

def my_auth(sec):
    '''只匹配手机号'''
    mysql=get_mysql('web_server')
    r=mysql.read_query('select * from user_info where  user_number="%s" '%(sec))
    #r=mysql.read_query('select * from user_info where user_name="%s" or user_number="%s" or user_mail="%s"'%(sec,sec,sec))
    mysql.close()
    if r:
        name=b64decode(r[0][1]).decode('utf-8')
        #print(name)
        return name
    else:
        return False
