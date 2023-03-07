from flask import Blueprint

robot = Blueprint("robot", __name__,static_folder='static',template_folder='templates',url_prefix='/robot')

robot_auth={'app_id':'cli_a114f87decf9d00b','app_secret':'Y4X6TRs3FNZyhFok2HdGvQkYoW28KDSk'}
from . import views
