from flask import Blueprint

map = Blueprint("map", __name__,static_folder='static',template_folder='templates',url_prefix='/map')
from . import views
