from flask import Blueprint

bp = Blueprint('pratos', __name__)

from app.routes.pratos import views
