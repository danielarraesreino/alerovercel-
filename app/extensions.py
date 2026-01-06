from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Criando a instância do SQLAlchemy
db = SQLAlchemy()

# Criando a instância de Migrate
migrate = Migrate()

# Adicione aqui outras extensões conforme necessário
# Por exemplo: login_manager, admin, jwt, etc.
