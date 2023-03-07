from flask import Blueprint

qgapp = Blueprint("qgapp", __name__,static_folder='static',template_folder='templates',url_prefix='/qgapp')
from . import views
