from flask import Blueprint

cmpr = Blueprint("cmpr", __name__,static_folder='static',template_folder='templates',url_prefix='/cmpr')
from . import views


