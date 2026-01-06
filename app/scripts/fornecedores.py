from app.models import Fornecedor
from faker import Faker

fake = Faker('pt_BR')

def criar_fornecedores():
    """Cria fornecedores para o AleroVeg"""
    fornecedores_data = [
        {
            'nome': 'Fazenda Orgânica Sol Nascente',
            'tipo': 'Hortifruti',
            'responsavel': 'Maria Silva',
            'email': 'contato@solnascente.com.br',
            'telefone': '(19) 99876-5432',
            'endereco': 'Rodovia SP-101, Km 12,5, Campinas/SP',
            'produtos_fornecidos': 'Hortaliças, legumes e frutas orgânicas'
        },
        {
            'nome': 'Cogumelos do Vale',
            'tipo': 'Cogumelos',
            'responsavel': 'Carlos Mendes',
            'email': 'vendas@cogumelosdovale.com.br',
            'telefone': '(19) 98765-4321',
            'endereco': 'Estrada dos Cogumelos, 123, Valinhos/SP',
            'produtos_fornecidos': 'Cogumelos frescos e desidratados'
        },
        {
            'nome': 'Grãos Nobres',
            'tipo': 'Grãos e Cereais',
            'responsavel': 'Ana Paula Oliveira',
            'email': 'vendas@graosnobres.com.br',
            'telefone': '(19) 98765-1234',
            'endereco': 'Av. das Especiarias, 456, Campinas/SP',
            'produtos_fornecidos': 'Grãos, cereais e farinhas integrais'
        },
        {
            'nome': 'Temperos da Terra',
            'tipo': 'Temperos e Especiarias',
            'responsavel': 'Roberto Santos',
            'email': 'contato@temperosdaterra.com.br',
            'telefone': '(19) 99876-1234',
            'endereco': 'Rua dos Aromas, 789, Campinas/SP',
            'produtos_fornecidos': 'Temperos, ervas e especiarias diversas'
        },
        {
            'nome': 'Sementes do Bem',
            'tipo': 'Sementes e Castanhas',
            'responsavel': 'Juliana Costa',
            'email': 'contato@sementesdobem.com.br',
            'telefone': '(19) 99876-5678',
            'endereco': 'Av. das Sementes, 321, Campinas/SP',
            'produtos_fornecidos': 'Sementes, castanhas e frutas secas'
        },
        {
            'nome': 'Pães da Terra',
            'tipo': 'Panificação',
            'responsavel': 'Ricardo Mendonça',
            'email': 'vendas@paesdaterra.com.br',
            'telefone': '(19) 98765-8765',
            'endereco': 'Rua dos Pães, 654, Campinas/SP',
            'produtos_fornecidos': 'Pães artesanais e produtos de panificação veganos'
        },
        {
            'nome': 'Doces da Vó',
            'tipo': 'Confeitaria',
            'responsavel': 'Fernanda Lima',
            'email': 'contato@docesdavo.com.br',
            'telefone': '(19) 99876-2345',
            'endereco': 'Rua dos Doces, 987, Campinas/SP',
            'produtos_fornecidos': 'Doces e sobremesas veganas'
        },
        {
            'nome': 'Bebidas Naturais',
            'tipo': 'Bebidas',
            'responsavel': 'Marcos Oliveira',
            'email': 'vendas@bebidasnaturais.com.br',
            'telefone': '(19) 98765-3456',
            'endereco': 'Av. das Bebidas, 159, Campinas/SP',
            'produtos_fornecidos': 'Sucos, chás e bebidas naturais'
        }
    ]
    
    fornecedores = []
    for dados in fornecedores_data:
        fornecedor = Fornecedor(
            nome=dados['nome'],
            tipo=dados['tipo'],
            responsavel=dados['responsavel'],
            email=dados['email'],
            telefone=dados['telefone'],
            endereco=dados['endereco'],
            produtos_fornecidos=dados['produtos_fornecidos'],
            ativo=True
        )
        db.session.add(fornecedor)
        fornecedores.append(fornecedor)
    
    db.session.commit()
    return fornecedores
