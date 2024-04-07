import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.neoapi import Neo4j

def get_backbone(backbone):

    uri = "neo4j+ssc://789bfae9.databases.neo4j.io"
    user = "QG_Editor"
    password = "qgeditor"
    neo=Neo4j(uri,user,password)
    cypher='match (n) where n.backbone contains "%s" \
    return distinct n.name,labels(n) as label ,n.backbone as backbone,n.code as code \
    union all \
    match (n1) where n1.backbone contains "%s" \
    with n1 \
    match (n:Indicator)-[]-(n1) \
    return  distinct n.name,labels(n) as label ,n.backbone as backbone,n.code as code order by labels(n)'%(backbone,backbone)
    nodes=neo.read_query(cypher)
    cypher='match p=(n1)-[r]->(n2) where n1.backbone contains "%s" and n2.backbone contains "%s" return startNode(r).name as start,endNode(r).name as end ,type(r) as relationship \
    union all \
    match p=(n:Indicator)-[r]-(n1) where n1.backbone contains "%s"\
    return  distinct startNode(r).name as start,endNode(r).name as end ,type(r) as relationship'%(backbone,backbone,backbone)
    edges=neo.read_query(cypher)
    return nodes,edges