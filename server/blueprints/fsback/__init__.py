from flask import Blueprint

fsback = Blueprint("fsback", __name__,static_folder='static',template_folder='templates',url_prefix='/fs')
from . import views
from . import global_var
global_var._init()
