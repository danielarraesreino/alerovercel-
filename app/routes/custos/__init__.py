from flask import Blueprint

bp = Blueprint('custos', __name__)

from app.routes.custos import views
