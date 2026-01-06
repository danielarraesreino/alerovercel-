from flask import Blueprint

bp = Blueprint('previsao', __name__)

from app.routes.previsao import views
