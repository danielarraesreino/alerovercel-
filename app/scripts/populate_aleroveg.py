from app import create_app, db
from app.scripts.fornecedores import criar_fornecedores
from app.scripts.produtos import criar_categorias, criar_produtos
from app.scripts.cardapio import criar_pratos, criar_cardapios
from app.scripts.vendas import criar_historico_vendas, criar_fatores_sazonais
from app.models.usuario import Usuario
from datetime import datetime
import sys
from werkzeug.security import generate_password_hash

def main():
    """Função principal para popular o banco de dados do AleroVeg"""
    print("Iniciando a população do banco de dados do AleroVeg...")
    
    # Criar aplicação
    app = create_app('development')
    
    with app.app_context():
        # Limpar o banco de dados existente (cuidado em produção!)
        print("Limpando o banco de dados existente...")
        db.drop_all()
        db.create_all()
        
        # 1. Criar fornecedores
        print("\n1. Criando fornecedores...")
        fornecedores = criar_fornecedores()
        print(f"   ✓ {len(fornecedores)} fornecedores criados")
        
        # 2. Criar categorias
        print("\n2. Criando categorias de produtos...")
        categorias = criar_categorias()
        print(f"   ✓ {len(categorias)} categorias criadas")
        
        # 3. Criar produtos
        print("\n3. Criando produtos...")
        produtos = criar_produtos(fornecedores)
        print(f"   ✓ {len(produtos)} produtos criados")
        
        # 4. Criar pratos
        print("\n4. Criando pratos...")
        pratos = criar_pratos(produtos)
        print(f"   ✓ {len(pratos)} pratos criados")
        
        # 5. Criar cardápios
        print("\n5. Criando cardápios...")
        cardapios = criar_cardapios(pratos)
        print(f"   ✓ {len(cardapios)} cardápios criados")
        
        # 6. Criar histórico de vendas
        print("\n6. Criando histórico de vendas...")
        criar_historico_vendas(pratos)
        print("   ✓ Histórico de vendas criado")
        
        # 7. Criar fatores sazonais
        print("\n7. Criando fatores sazonais...")
        criar_fatores_sazonais()
        print("   ✓ Fatores sazonais criados")
        
        # 8. Criar usuário administrador
        print("\n8. Criando usuário administrador...")
        criar_usuario_admin()
        print("   ✓ Usuário administrador criado")
        
        print("\nBanco de dados do AleroVeg populado com sucesso!")
        print("="*50)
        print("DADOS DE ACESSO")
        print("="*50)
        print("Email: admin@aleroveg.com.br")
        print("Senha: admin123")
        db.session.commit()
    return True

def criar_usuario_admin():
    """Cria um usuário administrador padrão"""
    # Verifica se já existe um usuário administrador
    admin_existente = Usuario.query.filter_by(email='admin@aleroveg.com.br').first()
    
    if admin_existente:
        return admin_existente
    
    # Cria o usuário administrador
    admin = Usuario(
        nome='Administrador AleroVeg',
        email='admin@aleroveg.com.br',
        senha=generate_password_hash('admin123'),
        tipo='admin',
        ativo=True,
        data_cadastro=datetime.now(),
        data_atualizacao=datetime.now()
    )
    
    db.session.add(admin)
    db.session.commit()
    return admin

if __name__ == "__main__":
    main()
