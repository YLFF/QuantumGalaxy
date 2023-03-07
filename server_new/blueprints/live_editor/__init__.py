from flask import Blueprint

live_editor = Blueprint("live_editor", __name__,static_folder='static',template_folder='templates',url_prefix='/qgapp')
from . import views
