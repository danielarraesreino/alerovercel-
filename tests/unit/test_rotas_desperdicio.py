import pytest
import json
from datetime import datetime, timedelta
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio

def test_index_desperdicio(client):
    """Testa se a pu00e1gina inicial do mu00f3dulo de desperdu00edcio carrega corretamente"""
    response = client.get('/desperdicio/')
    assert response.status_code == 200
    assert b'Dashboard de Desperdu00edcio' in response.data

def test_listar_categorias(client, session):
    """Testa a rota de listagem de categorias de desperdu00edcio"""
    # Criar algumas categorias
    categorias = [
        CategoriaDesperdicio(nome="Categoria 1", descricao="Descriu00e7u00e3o 1", cor="#FF0000"),
        CategoriaDesperdicio(nome="Categoria 2", descricao="Descriu00e7u00e3o 2", cor="#00FF00"),
        CategoriaDesperdicio(nome="Categoria 3", descricao="Descriu00e7u00e3o 3", cor="#0000FF"),
    ]
    for categoria in categorias:
        session.add(categoria)
    session.commit()
    
    response = client.get('/desperdicio/categorias')
    assert response.status_code == 200
    assert b'Categorias de Desperdu00edcio' in response.data
    # Verificar se as categorias estu00e3o sendo exibidas
    assert b'Categoria 1' in response.data
    assert b'Categoria 2' in response.data
    assert b'Categoria 3' in response.data

def test_criar_categoria(client):
    """Testa o formulu00e1rio de criau00e7u00e3o de categoria de desperdu00edcio"""
    # Testar carregamento do formulu00e1rio
    response = client.get('/desperdicio/criar-categoria')
    assert response.status_code == 200
    assert b'Criar Categoria de Desperdu00edcio' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'nome': 'Nova Categoria',
        'descricao': 'Descriu00e7u00e3o da nova categoria',
        'cor': '#FFAA00'
    }
    response = client.post('/desperdicio/criar-categoria', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Categoria criada com sucesso' in response.data or b'Categorias de Desperdu00edcio' in response.data

def test_editar_categoria(client, session):
    """Testa a ediu00e7u00e3o de uma categoria existente"""
    # Criar uma categoria
    categoria = CategoriaDesperdicio(
        nome="Categoria Teste",
        descricao="Descriu00e7u00e3o de teste",
        cor="#FF00FF"
    )
    session.add(categoria)
    session.commit()
    
    # Testar carregamento do formulu00e1rio de ediu00e7u00e3o
    response = client.get(f'/desperdicio/editar-categoria/{categoria.id}')
    assert response.status_code == 200
    assert b'Editar Categoria de Desperdu00edcio' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'nome': 'Categoria Atualizada',
        'descricao': 'Descriu00e7u00e3o atualizada',
        'cor': '#00FFAA'
    }
    response = client.post(f'/desperdicio/editar-categoria/{categoria.id}', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Categoria atualizada com sucesso' in response.data or b'Categorias de Desperdu00edcio' in response.data

def test_registros_desperdicio(client, session):
    """Testa a rota de listagem de registros de desperdu00edcio"""
    # Criar uma categoria
    categoria = CategoriaDesperdicio(
        nome="Categoria para Registros",
        descricao="Categoria para testes de registros",
        cor="#AABBCC"
    )
    session.add(categoria)
    session.commit()
    
    # Criar alguns registros
    registros = [
        RegistroDesperdicio(
            categoria_id=categoria.id,
            produto_id=1,
            quantidade=5.0,
            unidade="kg",
            valor=50.0,
            data_registro=datetime.now().date(),
            observacao="Observau00e7u00e3o 1"
        ),
        RegistroDesperdicio(
            categoria_id=categoria.id,
            produto_id=2,
            quantidade=3.0,
            unidade="l",
            valor=30.0,
            data_registro=datetime.now().date() - timedelta(days=1),
            observacao="Observau00e7u00e3o 2"
        ),
    ]
    for registro in registros:
        session.add(registro)
    session.commit()
    
    response = client.get('/desperdicio/registros')
    assert response.status_code == 200
    assert b'Registros de Desperdu00edcio' in response.data

def test_registrar_desperdicio(client, session):
    """Testa o formulu00e1rio de registro de desperdu00edcio"""
    # Criar uma categoria
    categoria = CategoriaDesperdicio(
        nome="Categoria para Registro",
        descricao="Categoria para teste de registro",
        cor="#123456"
    )
    session.add(categoria)
    session.commit()
    
    # Testar carregamento do formulu00e1rio
    response = client.get('/desperdicio/registrar')
    assert response.status_code == 200
    assert b'Registrar Desperdu00edcio' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'categoria_id': categoria.id,
        'produto_id': 1,
        'quantidade': 4.5,
        'unidade': 'kg',
        'valor': 45.0,
        'data_registro': datetime.now().strftime('%Y-%m-%d'),
        'observacao': 'Teste de registro de desperdu00edcio'
    }
    response = client.post('/desperdicio/registrar', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Desperdu00edcio registrado com sucesso' in response.data or b'Registros de Desperdu00edcio' in response.data

def test_metas_desperdicio(client, session):
    """Testa a rota de listagem de metas de desperdu00edcio"""
    # Criar algumas metas
    metas = [
        MetaDesperdicio(
            categoria_id=None,
            valor_inicial=1000.0,
            valor_meta=800.0,
            percentual_reducao=20.0,
            data_inicio=datetime.now().date(),
            data_fim=datetime.now().date() + timedelta(days=30),
            descricao="Meta geral"
        ),
        MetaDesperdicio(
            categoria_id=1,
            valor_inicial=500.0,
            valor_meta=400.0,
            percentual_reducao=20.0,
            data_inicio=datetime.now().date(),
            data_fim=datetime.now().date() + timedelta(days=30),
            descricao="Meta para categoria especu00edfica"
        ),
    ]
    for meta in metas:
        session.add(meta)
    session.commit()
    
    response = client.get('/desperdicio/metas')
    assert response.status_code == 200
    assert b'Metas de Reduu00e7u00e3o de Desperdu00edcio' in response.data

def test_criar_meta(client, session):
    """Testa o formulu00e1rio de criau00e7u00e3o de meta de desperdu00edcio"""
    # Criar uma categoria
    categoria = CategoriaDesperdicio(
        nome="Categoria para Meta",
        descricao="Categoria para teste de meta",
        cor="#654321"
    )
    session.add(categoria)
    session.commit()
    
    # Testar carregamento do formulu00e1rio
    response = client.get('/desperdicio/criar-meta')
    assert response.status_code == 200
    assert b'Criar Meta de Reduu00e7u00e3o' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'categoria_id': categoria.id,
        'valor_inicial': 1000.0,
        'percentual_reducao': 20.0,
        'data_inicio': datetime.now().strftime('%Y-%m-%d'),
        'data_fim': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'descricao': 'Meta de teste'
    }
    response = client.post('/desperdicio/criar-meta', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Meta criada com sucesso' in response.data or b'Metas de Reduu00e7u00e3o de Desperdu00edcio' in response.data

def test_relatorios_desperdicio(client):
    """Testa a rota de relatu00f3rios de desperdu00edcio"""
    response = client.get('/desperdicio/relatorios')
    assert response.status_code == 200
    assert b'Relatu00f3rios de Desperdu00edcio' in response.data
