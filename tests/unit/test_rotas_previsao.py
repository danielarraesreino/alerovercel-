import pytest
import json
from datetime import datetime, timedelta
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade

def test_index_previsao(client):
    """Testa se a pu00e1gina inicial do mu00f3dulo de previsu00e3o carrega corretamente"""
    response = client.get('/previsao/')
    assert response.status_code == 200
    assert b'Dashboard de Previsu00e3o' in response.data

def test_listar_historico(client, session):
    """Testa a rota de listagem do histu00f3rico de vendas"""
    # Criar alguns registros de histu00f3rico
    for i in range(3):
        venda = HistoricoVendas(
            data_venda=datetime.now().date() - timedelta(days=i),
            produto_id=i+1,
            quantidade=10 + i,
            valor=100.0 + i * 10
        )
        session.add(venda)
    session.commit()
    
    response = client.get('/previsao/historico')
    assert response.status_code == 200
    # Verificar se os dados estu00e3o sendo exibidos
    assert b'Histu00f3rico de Vendas' in response.data

def test_registrar_venda(client):
    """Testa o formulu00e1rio de registro de vendas"""
    # Testar carregamento do formulu00e1rio
    response = client.get('/previsao/registrar-venda')
    assert response.status_code == 200
    assert b'Registrar Venda' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'produto_id': 1,
        'data_venda': datetime.now().strftime('%Y-%m-%d'),
        'quantidade': 15,
        'valor': 150.0
    }
    response = client.post('/previsao/registrar-venda', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Venda registrada com sucesso' in response.data or b'Histu00f3rico de Vendas' in response.data

def test_gerar_previsao(client):
    """Testa o formulu00e1rio de gerau00e7u00e3o de previsu00e3o"""
    # Testar carregamento do formulu00e1rio
    response = client.get('/previsao/gerar-previsao')
    assert response.status_code == 200
    assert b'Gerar Previsu00e3o' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'produto_id': 1,
        'data_inicio': datetime.now().strftime('%Y-%m-%d'),
        'data_fim': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'metodo': 'mu00e9dia_mu00f3vel'
    }
    response = client.post('/previsao/gerar-previsao', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Previsu00e3o gerada com sucesso' in response.data or b'Previsu00f5es' in response.data

def test_listar_previsoes(client, session):
    """Testa a rota de listagem de previsu00f5es"""
    # Criar uma previsu00e3o
    previsao = PrevisaoDemanda(
        produto_id=1,
        data_inicio=datetime.now().date(),
        data_fim=datetime.now().date() + timedelta(days=7),
        metodo="mu00e9dia_mu00f3vel",
        valores_previstos="[12,12,12,12,12,12,12]",
        data_geracao=datetime.now()
    )
    session.add(previsao)
    session.commit()
    
    response = client.get('/previsao/previsoes')
    assert response.status_code == 200
    assert b'Previsu00f5es Geradas' in response.data

def test_visualizar_previsao(client, session):
    """Testa a rota de visualizau00e7u00e3o de uma previsu00e3o especu00edfica"""
    # Criar uma previsu00e3o
    previsao = PrevisaoDemanda(
        produto_id=1,
        data_inicio=datetime.now().date(),
        data_fim=datetime.now().date() + timedelta(days=7),
        metodo="mu00e9dia_mu00f3vel",
        valores_previstos="[12,12,12,12,12,12,12]",
        data_geracao=datetime.now()
    )
    session.add(previsao)
    session.commit()
    
    response = client.get(f'/previsao/previsao/{previsao.id}')
    assert response.status_code == 200
    assert b'Detalhes da Previsu00e3o' in response.data

def test_fatores_sazonalidade(client):
    """Testa a rota de listagem de fatores de sazonalidade"""
    response = client.get('/previsao/fatores-sazonalidade')
    assert response.status_code == 200
    assert b'Fatores de Sazonalidade' in response.data

def test_criar_fator_sazonalidade(client):
    """Testa o formulu00e1rio de criau00e7u00e3o de fator de sazonalidade"""
    # Testar carregamento do formulu00e1rio
    response = client.get('/previsao/criar-fator-sazonalidade')
    assert response.status_code == 200
    assert b'Criar Fator de Sazonalidade' in response.data
    
    # Testar envio do formulu00e1rio
    data = {
        'tipo': 'dia_semana',
        'valor': 1.2,
        'descricao': 'Segunda-feira'
    }
    response = client.post('/previsao/criar-fator-sazonalidade', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Fator de sazonalidade criado com sucesso' in response.data or b'Fatores de Sazonalidade' in response.data
