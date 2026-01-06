from flask import Blueprint

bp = Blueprint('desperdicio', __name__)

from app.routes.desperdicio import views
