from flask import Blueprint

bp = Blueprint('produtos', __name__)

from app.routes.produtos import views
