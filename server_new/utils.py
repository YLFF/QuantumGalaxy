import re
from jira import JIRA
import logging
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    #fh = logging.FileHandler(
    #    "E:/wangzhilin/QuantumGalaxy/logs/flask_server.log",
    #    'a',
    #    encoding='utf-8')
    #fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    ch.setFormatter(formatter)
    #fh.setFormatter(formatter)
    logger.addHandler(ch)
    #logger.addHandler(fh)
    return logger

