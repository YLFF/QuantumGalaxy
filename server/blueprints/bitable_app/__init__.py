from flask import Blueprint
'''专用多维表格读取接口'''
bitapp = Blueprint("bitapp", __name__,static_folder='static',template_folder='templates',url_prefix='/bitapp')

bitapp_auth={'app_id':'cli_a1fc0a192db8100c','app_secret':'nNk1fT8h2eVi8B2ymIFangHTpYrOAJTD'}
from . import views
