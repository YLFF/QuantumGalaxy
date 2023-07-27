from flask import Blueprint

scout = Blueprint("scout", __name__,static_folder='static',template_folder='templates',url_prefix='/scout')
from . import views
