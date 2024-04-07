from flask import Blueprint

localapi = Blueprint("localapi", __name__,static_folder='static',template_folder='templates',url_prefix='/localapi')
from . import views
