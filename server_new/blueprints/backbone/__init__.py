from flask import Blueprint

backbone = Blueprint("backbone", __name__,static_folder='static',template_folder='templates',url_prefix='/backbone')
from . import views
