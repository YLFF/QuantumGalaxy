from flask import Flask
 
from flask_apscheduler import APScheduler
 
import datetime

from flask import session
from flask_apscheduler.auth import HTTPBasicAuth
from blueprints.ev_band.ev_band_aps import ev_band_routine
from blueprints.backbone.backbone_aps import reset_mysql
 
# interval examples
scheduler = APScheduler()

#@scheduler.task('interval', id='do_job_1', seconds=30)
def job1():
 
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 
    print(now)


@scheduler.task('cron',id='ev_band_routine',hour=4,minute=4,second=0)
def job0():
    ev_band_routine()


@scheduler.task('cron',id='backbone_routine',hour=17,minute=17,second=0)
def job1():
    #reset_mysql()
    pass


 
if __name__ == '__main__':
 
    app = Flask(__name__)
    app.config.from_object

 
    scheduler.init_app(app)
 
    scheduler.start()
