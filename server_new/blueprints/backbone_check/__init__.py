from flask import Blueprint

backbone_check = Blueprint("backbone_check", __name__,static_folder='static',template_folder='templates',url_prefix='/backbone_check')
from . import views


