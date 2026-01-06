from flask import Blueprint

bp = Blueprint('estoque', __name__)

from app.routes.estoque import views
