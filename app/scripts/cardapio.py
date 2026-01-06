from app.models import Prato, PratoInsumo, Cardapio, CardapioSecao, CardapioItem, db
from datetime import datetime
import random

def criar_pratos(produtos):
    """Cria pratos para o cardápio do AleroVeg"""
    # Mapear produtos por categoria para facilitar a busca
    produtos_por_categoria = {}
    for produto in produtos:
        if produto.categoria not in produtos_por_categoria:
            produtos_por_categoria[produto.categoria] = []
        produtos_por_categoria[produto.categoria].append(produto)
    
    # Dados dos pratos
    pratos_data = [
        {
            'nome': 'Hambúrguer de Grão de Bico',
            'descricao': 'Hambúrguer caseiro de grão de bico com temperos especiais, acompanha pão integral, alface, tomate e molho de iogurte de castanhas.',
            'categoria': 'Prato Principal',
            'rendimento': 1,
            'unidade_rendimento': 'porção',
            'tempo_preparo': 25,
            'preco_venda': 28.90,
            'margem': 45.0,
            'ingredientes': [
                {'nome': 'Grão de Bico', 'quantidade': 0.2, 'unidade': 'kg'},
                {'nome': 'Pão Integral', 'quantidade': 1, 'unidade': 'un'},
                {'nome': 'Temperos', 'quantidade': 5, 'unidade': 'g'}
            ]
        },
        {
            'nome': 'Escondidinho de Batata Doce com Shimeji',
            'descricao': 'Delicioso escondidinho de batata doce com shimeji refogado e queijo vegano gratinado.',
            'categoria': 'Prato Principal',
            'rendimento': 1,
            'unidade_rendimento': 'porção',
            'tempo_preparo': 35,
            'preco_venda': 32.90,
            'margem': 50.0,
            'ingredientes': [
                {'nome': 'Batata Doce', 'quantidade': 0.3, 'unidade': 'kg'},
                {'nome': 'Shimeji Branco', 'quantidade': 0.1, 'unidade': 'kg'},
                {'nome': 'Queijo Vegano', 'quantidade': 0.05, 'unidade': 'kg'},
                {'nome': 'Temperos', 'quantidade': 5, 'unidade': 'g'}
            ]
        },
        {
            'nome': 'Suco Detox Verde',
            'descricao': 'Suco detox com couve, maçã, limão e gengibre.',
            'categoria': 'Bebida',
            'rendimento': 1,
            'unidade_rendimento': 'copo 300ml',
            'tempo_preparo': 5,
            'preco_venda': 12.90,
            'margem': 40.0,
            'ingredientes': [
                {'nome': 'Maçã', 'quantidade': 1, 'unidade': 'un'},
                {'nome': 'Limão', 'quantidade': 0.5, 'unidade': 'un'},
                {'nome': 'Gengibre', 'quantidade': 0.01, 'unidade': 'kg'}
            ]
        }
    ]
    
    pratos_criados = []
    for dados in pratos_data:
        prato = Prato(
            nome=dados['nome'],
            descricao=dados['descricao'],
            categoria=dados['categoria'],
            rendimento=dados['rendimento'],
            unidade_rendimento=dados['unidade_rendimento'],
            tempo_preparo=dados['tempo_preparo'],
            preco_venda=dados['preco_venda'],
            margem=dados['margem'],
            ativo=True,
            data_cadastro=datetime.now(),
            data_atualizacao=datetime.now()
        )
        
        # Adicionar ingredientes ao prato
        for ingrediente_data in dados['ingredientes']:
            # Encontrar o produto correspondente
            produto_encontrado = None
            for produto in produtos:
                if ingrediente_data['nome'].lower() in produto.nome.lower():
                    produto_encontrado = produto
                    break
            
            if produto_encontrado:
                prato_insumo = PratoInsumo(
                    prato=prato,
                    produto=produto_encontrado,
                    quantidade=ingrediente_data['quantidade'],
                    unidade=ingrediente_data['unidade'],
                    obrigatorio=True
                )
                db.session.add(prato_insumo)
        
        db.session.add(prato)
        pratos_criados.append(prato)
    
    db.session.commit()
    return pratos_criados

def criar_cardapios(pratos):
    """Cria cardápios para o AleroVeg"""
    # Filtra pratos por categoria
    pratos_principais = [p for p in pratos if p.categoria == 'Prato Principal']
    bebidas = [p for p in pratos if p.categoria == 'Bebida']
    
    # Cria cardápio principal
    cardapio = Cardapio(
        nome='Cardápio Principal',
        descricao='Cardápio completo do AleroVeg',
        data_inicio=datetime.now().date(),
        ativo=True,
        tipo='Principal',
        data_criacao=datetime.now(),
        data_atualizacao=datetime.now()
    )
    
    # Adiciona seção de pratos principais
    secao_principal = CardapioSecao(
        cardapio=cardapio,
        nome='Pratos Principais',
        descricao='Pratos principais do cardápio',
        ordem=1
    )
    
    # Adiciona itens à seção de pratos principais
    for i, prato in enumerate(pratos_principais, 1):
        item = CardapioItem(
            secao=secao_principal,
            prato=prato,
            ordem=i,
            preco_venda=prato.preco_venda,
            destaque=True,
            disponivel=True
        )
        db.session.add(item)
    
    # Adiciona seção de bebidas
    secao_bebidas = CardapioSecao(
        cardapio=cardapio,
        nome='Bebidas',
        descricao='Bebidas naturais e sucos',
        ordem=2
    )
    
    # Adiciona itens à seção de bebidas
    for i, bebida in enumerate(bebidas, 1):
        item = CardapioItem(
            secao=secao_bebidas,
            prato=bebida,
            ordem=i,
            preco_venda=bebida.preco_venda,
            destaque=False,
            disponivel=True
        )
        db.session.add(item)
    
    db.session.add(cardapio)
    db.session.commit()
    
    return [cardapio]
