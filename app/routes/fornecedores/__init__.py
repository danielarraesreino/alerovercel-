from flask import Blueprint

bp = Blueprint('fornecedores', __name__)

from app.routes.fornecedores import views
