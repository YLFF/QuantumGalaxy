from flask import Blueprint

graph2xml = Blueprint("graph2xml", __name__,static_folder='static',template_folder='templates',url_prefix='/xml')
from . import views
