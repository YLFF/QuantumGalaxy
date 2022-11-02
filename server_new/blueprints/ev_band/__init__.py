from flask import Blueprint

ev_band = Blueprint("ev_band", __name__,static_folder='static',template_folder='templates',url_prefix='/ev_band')
from . import views
