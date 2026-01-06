from flask import Blueprint

bp = Blueprint('cardapios', __name__)

from app.routes.cardapios import views
