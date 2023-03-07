
import sys     
sys.path.append(r'E:\wangzhilin\QuantumGalaxy')
import logging
from QGI.mysql import MYSQL
from base64 import b64decode,b64encode


def get_logger(name,chlevel=logging.ERROR):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    #fh = logging.FileHandler(
    #    "E:/wangzhilin/QuantumGalaxy/logs/flask_server.log",
    #    'a',
    #    encoding='utf-8')
    #fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(chlevel)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    logger.addHandler(ch)
    #logger.addHandler(fh)
    return logger

def get_mysql(database='web_server'):

    host='localhost'
    user='Local_Editor'
    password='QuantumGalaxy'
    #database='qgdbs'
    mysql=MYSQL(host,user,password,database)
    return mysql


def main():
    name=input('user name:')
    num=input('user number:')
    mail=input('user email:')
    name_en=name.encode('utf-8')

    name_en=b64encode(name_en).decode('utf-8')

    num_en=b64encode(num.encode('utf-8')).decode('utf-8')
    mail_en=b64encode(mail.encode('utf-8')).decode('utf-8')
    print(name_en,num_en,mail_en)
    mysql=get_mysql()
    sql='insert into user_info (user_name,user_number,user_mail) values ("%s","%s","%s")'%(name_en,num_en,mail_en)
    mysql.write_query(sql)

if __name__=='__main__':
    main()