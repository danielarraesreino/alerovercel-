from flask import Blueprint

bp = Blueprint('nfe', __name__)

from app.routes.nfe import views
