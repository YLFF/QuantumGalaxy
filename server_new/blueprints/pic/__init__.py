from flask import Blueprint

pic = Blueprint("pic", __name__,static_folder='static',template_folder='templates',url_prefix='/pic')
from . import views
