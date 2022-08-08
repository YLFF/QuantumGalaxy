
from jira import JIRA
import pandas as pd
import sys
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.jiraapi import Jira
from QGI.neoapi import Neo4j
#jira = JIRA('https://research.quantumgalaxy.cn/', basic_auth=('wangzhilin', "wangzhilin"))
import time
import numpy as np

uri = "neo4j+ssc://08ef0a79.databases.neo4j.io"
user = "QG_Editor"
password = "editor"


neo=Neo4j(uri,user,password)

def get_fields(issue,fields):
    val=[]
    for field in fields:
        val.append(issue.fields.__dict__[field])
    return val

jira=Jira()




jql = 'project = SCENARIO AND status in (评估中, 生效中)'
issues = jira.jql_search(jql)


for issue in issues:
    link = issue.permalink()

    code, current_scenario_date, current_profit_sequence, current_scenario_value = get_fields(
        issue, [
            'customfield_10201', 'customfield_10920', 'customfield_11430',
            'customfield_10917'
        ])
    summary, future_scenario_date, future_profit_sequence, future_scenario_value = get_fields(
        issue, [
            'summary', 'customfield_10622', 'customfield_11432',
            'customfield_10921'
        ])
    cypher = 'merge (n:Scenario {link:"%s"}) set n.code="%s",n.current_scenario_date="%s",n.current_profit_sequence="%s",n.current_scenario_value="%s",n.name="%s",n.future_scenario_date="%s",n.future_profit_sequence="%s",n.future_scenario_value="%s" '%(link,code, current_scenario_date, current_profit_sequence, current_scenario_value,summary, future_scenario_date, future_profit_sequence, future_scenario_value)
    #print(cypher)
    neo.read_query(cypher)
    #time.sleep(0.5)
    #break
result=neo.simple_query(cypher='match (n:Scenario) with n,collect(n.code) as codes match(m:Company) where m.code in codes merge (m)-[r:imagine]->(n) return m.name')
print(result)
time.sleep(5)