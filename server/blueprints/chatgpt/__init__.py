from flask import Blueprint

chatgpt = Blueprint("chatgpt", __name__,static_folder='static',template_folder='templates',url_prefix='/chatgpt')
from . import views
