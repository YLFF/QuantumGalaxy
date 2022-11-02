from datetime import datetime,timedelta
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')

import pandas as pd
import numpy as np
from QGI.neoapi import Neo4j
from QGI.feishu import *
from QGI.mysql import MYSQL
import numpy as np
import pandas as pd
import json
import scipy,math
from jira import JIRA
from server_new.utils import get_logger
logger=get_logger(__name__)
def get_neo():
    uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
    user = "QG_Editor"
    password = "editor"
    neo=Neo4j(uri,user,password)
    return neo
def get_backbone_index():
    neo=get_neo()
    backbones=neo.read_query("match (n)  where not  n.backbone contains ',' return distinct n.backbone ")
    return [backbone.values()[0] for backbone in backbones]