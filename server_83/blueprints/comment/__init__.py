from flask import Blueprint

comment = Blueprint("comment", __name__,static_folder='static',template_folder='templates',url_prefix='/comment')
from . import views
