from app import create_app
from app.extensions import db
from app.models import *

def setup_database(drop_all=False):
    """Cria todas as tabelas no banco de dados
    
    Args:
        drop_all: Se True, apaga todas as tabelas antes de criar novamente
    """
    app = create_app('development')
    with app.app_context():
        if drop_all:
            print("Apagando tabelas existentes...")
            db.drop_all()
        
        print("Criando tabelas...")
        db.create_all()
        print("Banco de dados configurado com sucesso!")

if __name__ == '__main__':
    import sys
    
    # Verificar se o parâmetro --drop foi passado
    drop_all = '--drop' in sys.argv
    
    setup_database(drop_all)
