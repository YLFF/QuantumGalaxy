import pandas as pd
import sys
from jira import JIRA
jira=JIRA('https://research.quantumgalaxy.cn/', basic_auth=('bot2', "jira_bot2"))
import sys
import logging
sys.path.append('E:\wangzhilin\QuantumGalaxy')
from QGI.logger import get_logger
from QGI.mysql import get_mysql
import threading
import queue
import time

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Time taken by {func.__name__}: {end_time - start_time} seconds")
        return result
    return wrapper

@timeit
def worker(jql, maxResults, startAt, endAt, out_queue):
    while startAt < endAt:
        print(startAt)
        actual_maxResults = min(maxResults, endAt - startAt)
        result1 = jira.search_issues(jql, maxResults=actual_maxResults, startAt=startAt)
        #result1 = jira.search_issues(jql, maxResults=maxResults, startAt=startAt)
        for issue in result1:
            out_queue.put(issue)
        startAt += len(result1)
        print(startAt)

def threading_jira_search_2(jql, maxResults=500, startAt=0, num_threads=4):
    result_queue = queue.Queue()
    total = jira.search_issues(jql, maxResults=1, startAt=0).total
    print(total)
    threads = []
    for i in range(num_threads):
        worker_startAt = startAt + i * (total // num_threads)
        worker_endAt = startAt + (i + 1) * (total // num_threads) if i != num_threads - 1 else total
        thread = threading.Thread(target=worker, args=(jql, maxResults, worker_startAt, worker_endAt, result_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    result = []
    while not result_queue.empty():
        result.append(result_queue.get())

    print('total issue:', len(result))
    return result
if __name__=='__main__':
    print('?')
    logger=get_logger(name='jira_issue_update',fh=True)
    mysql=get_mysql()
    jql='project = COMPSTUDY AND issuetype = 公司研究'
    #jql="project = COMPSTUDY AND updated >=   startOfDay('-1d')"
    logger.info(f'start jira query:{jql}')
    issues=threading_jira_search_2(jql)
    logger.info(f'end query and get {len(issues)} issues')
    #print(issues)
    
    issue_codes=[issue.fields.customfield_10201 for issue in issues]
    stock=mysql.read_query('select code,name from ticker_info where region="CN"')
    mysql.close()
    new_issues=[]
    new_names=[]
    for code,name in stock:
        if '+' in code:continue
        if code not in issue_codes:
            #print(code,name)
            new_issues.append((code,name))
            #pass
        else:
            issue=issues[issue_codes.index(code)]
            if issue.fields.summary !=name:
                #print(issue.fields.summary,name)
                new_names.append((code,name,issue))
    logger.info(f'get {len(new_issues)} issues to create')
    logger.info(f'get {len(new_names)} issues to update')
    for code,name in new_issues:
        try:
            issue=jira.create_issue(project='10000',issuetype='公司研究',summary=name,customfield_10201=code)
        except Exception as e:
            print(e)
            print(code,name)
    for code,name,issue in new_names:
        try:
            issue.update(summary=name)
        except Exception as e:
            print(e)
            print(code,name)

                