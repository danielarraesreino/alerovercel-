from app.models import Categoria, Produto, db
from datetime import datetime
import random

def criar_categorias():
    """Cria categorias de produtos para o AleroVeg"""
    categorias = [
        'Cogumelos', 'Legumes', 'Verduras', 'Temperos',
        'Grãos e Cereais', 'Farinhas', 'Óleos e Gorduras', 'Laticínios Vegetais',
        'Ovos e Substitutos', 'Adoçantes Naturais', 'Castanhas e Sementes',
        'Frutas', 'Pães e Massas', 'Bebidas', 'Molhos e Caldos', 'Produtos Prontos'
    ]
    
    categorias_criadas = []
    for nome in categorias:
        categoria = Categoria(nome=nome, descricao=f"Categoria de {nome}")
        db.session.add(categoria)
        categorias_criadas.append(categoria)
    
    db.session.commit()
    return categorias_criadas

def criar_produtos(fornecedores):
    """Cria produtos para o AleroVeg"""
    # Mapeamento de categorias para facilitar a busca
    categorias = {c.nome: c for c in Categoria.query.all()}
    
    # Mapeamento de fornecedores para facilitar a busca
    fornecedores_dict = {f.nome: f for f in fornecedores}
    
    # Dados dos produtos
    produtos_data = [
        # Cogumelos
        {'nome': 'Cogumelo Paris Fresco', 'unidade': 'kg', 'preco': 45.90, 'categoria': 'Cogumelos', 'estoque_min': 5, 'fornecedor': 'Cogumelos do Vale'},
        {'nome': 'Shitake Fresco', 'unidade': 'kg', 'preco': 89.90, 'categoria': 'Cogumelos', 'estoque_min': 3, 'fornecedor': 'Cogumelos do Vale'},
        {'nome': 'Shimeji Branco', 'unidade': 'kg', 'preco': 52.50, 'categoria': 'Cogumelos', 'estoque_min': 3, 'fornecedor': 'Cogumelos do Vale'},
        
        # Legumes
        {'nome': 'Abóbora Cabotiá', 'unidade': 'kg', 'preco': 5.90, 'categoria': 'Legumes', 'estoque_min': 10, 'fornecedor': 'Fazenda Orgânica Sol Nascente'},
        {'nome': 'Berinjela', 'unidade': 'kg', 'preco': 6.90, 'categoria': 'Legumes', 'estoque_min': 8, 'fornecedor': 'Fazenda Orgânica Sol Nascente'},
        {'nome': 'Abobrinha Italiana', 'unidade': 'kg', 'preco': 4.90, 'categoria': 'Legumes', 'estoque_min': 12, 'fornecedor': 'Fazenda Orgânica Sol Nascente'},
        
        # Grãos e Cereais
        {'nome': 'Arroz Integral', 'unidade': 'kg', 'preco': 8.90, 'categoria': 'Grãos e Cereais', 'estoque_min': 20, 'fornecedor': 'Grãos Nobres'},
        {'nome': 'Feijão Preto', 'unidade': 'kg', 'preco': 9.90, 'categoria': 'Grãos e Cereais', 'estoque_min': 15, 'fornecedor': 'Grãos Nobres'},
        {'nome': 'Quinoa em Grãos', 'unidade': 'kg', 'preco': 24.90, 'categoria': 'Grãos e Cereais', 'estoque_min': 5, 'fornecedor': 'Grãos Nobres'},
        
        # Temperos
        {'nome': 'Cúrcuma em Pó', 'unidade': 'g', 'preco': 0.50, 'categoria': 'Temperos', 'estoque_min': 100, 'fornecedor': 'Temperos da Terra'},
        {'nome': 'Páprica Defumada', 'unidade': 'g', 'preco': 0.65, 'categoria': 'Temperos', 'estoque_min': 80, 'fornecedor': 'Temperos da Terra'},
        {'nome': 'Cominho em Pó', 'unidade': 'g', 'preco': 0.45, 'categoria': 'Temperos', 'estoque_min': 120, 'fornecedor': 'Temperos da Terra'}
    ]
    
    produtos_criados = []
    for dados in produtos_data:
        # Encontrar fornecedor
        fornecedor = fornecedores_dict.get(dados['fornecedor'])
        
        # Encontrar categoria
        categoria = categorias.get(dados['categoria'])
        
        if not fornecedor or not categoria:
            continue
            
        produto = Produto(
            nome=dados['nome'],
            unidade=dados['unidade'],
            preco_unitario=dados['preco'],
            estoque_minimo=dados['estoque_min'],
            estoque_atual=random.randint(dados['estoque_min'], dados['estoque_min'] * 3),  # Estoque entre o mínimo e 3x o mínimo
            categoria=dados['categoria'],
            fornecedor_id=fornecedor.id,
            ativo=True,
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now()
        )
        
        db.session.add(produto)
        produtos_criados.append(produto)
    
    db.session.commit()
    return produtos_criados
