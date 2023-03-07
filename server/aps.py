from flask import Flask
 
from flask_apscheduler import APScheduler
 
import datetime

from flask import session
from flask_apscheduler.auth import HTTPBasicAuth
from blueprints.fsback import global_var
from blueprints.fsback.views import refresh
from blueprints.research_robot.models import routine_pointview_list
# interval examples
scheduler = APScheduler()
from log import get_logger
apslogger=get_logger('scheduler_log')
@scheduler.task('interval', id='do_job_1', seconds=6800)
def refresh_token():
 
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    r=refresh()
    apslogger.debug(now)
    apslogger.info('refresh token')

#@scheduler.task('cron',id='robot_investmentview_list',hour=18,minute=0,second=0,day_of_week='0-6')
def send_list():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    apslogger.info(now)
    r=routine_pointview_list()
    apslogger.info('sended')

#@scheduler.task('cron',id='test',hour=8,minute=55,second=0,day_of_week='0-6')
def send_list():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    apslogger.info('\n\n')
    apslogger.info(now)
    


 
if __name__ == '__main__':
 
    app = Flask(__name__)
    app.config.from_object

 
    scheduler.init_app(app)
 
    scheduler.start()
