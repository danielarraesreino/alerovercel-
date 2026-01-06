from app import create_app
from app.extensions import db
from app.models import *
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker('pt_BR')

def seed_aleroveg():
    """Popula o banco de dados com dados iniciais para o AleroVeg"""
    app = create_app('development')
    with app.app_context():
        print("Iniciando a criação dos dados do AleroVeg...")
        
        # Limpar dados existentes (cuidado em produção!)
        print("Limpando dados existentes...")
        db.drop_all()
        db.create_all()
        
        # 1. Criar Fornecedores
        print("Criando fornecedores...")
        fornecedores = criar_fornecedores()
        
        # 2. Criar Categorias de Produtos
        print("Criando categorias de produtos...")
        categorias = criar_categorias()
        
        # 3. Criar Produtos
        print("Criando produtos...")
        produtos = criar_produtos(fornecedores, categorias)
        
        # 4. Criar Pratos
        print("Criando pratos...")
        pratos = criar_pratos(produtos)
        
        # 5. Criar Cardápios
        print("Criando cardápios...")
        cardapios = criar_cardapios(pratos)
        
        # 6. Criar Categorias de Desperdício
        print("Criando categorias de desperdício...")
        categorias_desperdicio = criar_categorias_desperdicio()
        
        # 7. Criar Registros de Desperdício
        print("Criando registros de desperdício...")
        criar_registros_desperdicio(pratos, produtos, categorias_desperdicio)
        
        # 8. Criar Metas de Desperdício
        print("Criando metas de redução de desperdício...")
        criar_metas_desperdicio(pratos, produtos, categorias_desperdicio)
        
        # 9. Criar Histórico de Vendas
        print("Criando histórico de vendas...")
        criar_historico_vendas(pratos)
        
        print("\nDados do AleroVeg criados com sucesso!")
        print("="*50)
        print("RESUMO DA IMPORTAÇÃO")
        print("="*50)
        print(f"Fornecedores: {len(fornecedores)}")
        print(f"Categorias de Produtos: {len(categorias)}")
        print(f"Produtos: {len(produtos)}")
        print(f"Pratos: {len(pratos)}")
        print(f"Cardápios: {len(cardapios)}")
        print(f"Categorias de Desperdício: {len(categorias_desperdicio)}")
        print("="*50)
        print("\nAcesse o sistema e faça login com as credenciais padrão:")
        print("Email: admin@aleroveg.com.br")
        print("Senha: admin123")
        
        return True
