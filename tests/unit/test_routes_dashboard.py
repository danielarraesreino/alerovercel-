import pytest
from flask import url_for
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, PropertyMock
import json

from app.routes.dashboard.views import (
    calcular_metricas_principais,
    obter_dados_diarios,
    obter_top_pratos,
    obter_distribuicao_categorias,
    obter_tendencia_lucratividade,
    obter_indicadores_desperdicio
)

@pytest.fixture
def mock_db_query():
    with patch('app.routes.dashboard.views.db.session.query') as mock_query:
        # Configurar mock para retornar resultados para diferentes consultas
        mock_query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.first.return_value = None
        yield mock_query

@pytest.fixture
def mock_historico_vendas():
    with patch('app.routes.dashboard.views.HistoricoVendas') as mock_model:
        # Configurar mock para query de vendas
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(data=date.today(), valor_total=Decimal('100.00'), quantidade=1, cardapio_item_id=1, prato_id=None),
            MagicMock(data=date.today(), valor_total=Decimal('150.00'), quantidade=2, cardapio_item_id=None, prato_id=1)
        ]
        mock_model.query = mock_query
        yield mock_model

@pytest.fixture
def mock_registro_desperdicio():
    with patch('app.routes.dashboard.views.RegistroDesperdicio') as mock_model:
        # Configurar mock para query de registros de desperdu00edcio
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(data_registro=date.today(), valor_estimado=Decimal('25.00'), quantidade=2.5),
            MagicMock(data_registro=date.today(), valor_estimado=Decimal('15.00'), quantidade=1.5)
        ]
        mock_model.query = mock_query
        yield mock_model

@pytest.fixture
def mock_cardapio_item():
    with patch('app.routes.dashboard.views.CardapioItem') as mock_model:
        # Configurar mock para query de itens de cardu00e1pio
        mock_item = MagicMock(preco_custo=Decimal('40.00'), preco_venda=Decimal('80.00'))
        mock_model.query.get.return_value = mock_item
        yield mock_model

@pytest.fixture
def mock_prato():
    with patch('app.routes.dashboard.views.Prato') as mock_model:
        # Configurar mock para query de pratos
        mock_prato = MagicMock(
            id=1, 
            nome="Prato Teste", 
            custo_total=Decimal('30.00'), 
            preco_venda=Decimal('60.00'),
            categoria="Principal"
        )
        type(mock_prato).margem_lucro = PropertyMock(return_value=50.0)
        mock_model.query.get.return_value = mock_prato
        
        # Mock para consultas com filter
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_prato]
        mock_model.query = mock_query
        
        yield mock_model

@pytest.fixture
def mock_custo_indireto():
    with patch('app.routes.dashboard.views.CustoIndireto') as mock_model:
        # Configurar mock para query de custos indiretos
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [
            MagicMock(data_referencia=date.today(), valor=Decimal('100.00'), categoria="Aluguel"),
            MagicMock(data_referencia=date.today(), valor=Decimal('50.00'), categoria="Energia")
        ]
        mock_model.query = mock_query
        yield mock_model

def test_calcular_metricas_principais(mock_historico_vendas, mock_cardapio_item, mock_prato, mock_custo_indireto):
    """Testa o cu00e1lculo das mu00e9tricas principais de lucratividade"""
    # Peru00edodo de teste
    data_inicio = date.today() - timedelta(days=30)
    data_fim = date.today()
    
    # Executar a funu00e7u00e3o
    metricas = calcular_metricas_principais(data_inicio, data_fim)
    
    # Verificar se todas as mu00e9tricas esperadas estu00e3o presentes
    assert 'receita_total' in metricas
    assert 'custo_total' in metricas
    assert 'lucro' in metricas
    assert 'margem' in metricas
    
    # Verificar se a receita total estu00e1 correta (baseado nos mocks)
    assert metricas['receita_total'] == 250.0  # 100.00 + 150.00
    
    # Verificar se o custo total inclui custos de produtos e custos indiretos
    assert metricas['custo_total'] > 0
    
    # Verificar se o lucro u00e9 calculado corretamente (receita - custos)
    assert metricas['lucro'] == metricas['receita_total'] - metricas['custo_total']
    
    # Verificar se a margem estu00e1 entre 0 e 100%
    assert 0 <= metricas['margem'] <= 100

def test_obter_dados_diarios(mock_historico_vendas, mock_custo_indireto):
    """Testa a obtenu00e7u00e3o de dados diu00e1rios para gru00e1ficos"""
    # Peru00edodo de teste
    data_inicio = date.today() - timedelta(days=7)
    data_fim = date.today()
    
    # Executar a funu00e7u00e3o
    dados = obter_dados_diarios(data_inicio, data_fim)
    
    # Verificar se todas as chaves esperadas estu00e3o presentes
    assert 'labels' in dados
    assert 'receitas' in dados
    assert 'custos' in dados
    assert 'lucros' in dados
    
    # Verificar se temos dados para todos os dias do peru00edodo
    dias_periodo = (data_fim - data_inicio).days + 1
    assert len(dados['labels']) == dias_periodo
    assert len(dados['receitas']) == dias_periodo
    assert len(dados['custos']) == dias_periodo
    assert len(dados['lucros']) == dias_periodo

def test_obter_top_pratos(mock_historico_vendas, mock_prato):
    """Testa a obtenu00e7u00e3o dos pratos mais lucrativos"""
    # Peru00edodo de teste
    data_inicio = date.today() - timedelta(days=30)
    data_fim = date.today()
    
    # Executar a funu00e7u00e3o
    top_pratos = obter_top_pratos(data_inicio, data_fim, limite=5)
    
    # Verificar se retornou uma lista
    assert isinstance(top_pratos, list)
    
    # Se o mock retornou dados, verificar estrutura
    if top_pratos:
        primeiro_prato = top_pratos[0]
        assert 'id' in primeiro_prato
        assert 'nome' in primeiro_prato
        assert 'quantidade_vendida' in primeiro_prato
        assert 'receita' in primeiro_prato
        assert 'custo' in primeiro_prato
        assert 'lucro' in primeiro_prato
        assert 'margem' in primeiro_prato

def test_obter_distribuicao_categorias(mock_historico_vendas, mock_prato):
    """Testa a obtenu00e7u00e3o da distribuiu00e7u00e3o de vendas por categoria"""
    # Peru00edodo de teste
    data_inicio = date.today() - timedelta(days=30)
    data_fim = date.today()
    
    # Executar a funu00e7u00e3o
    distribuicao = obter_distribuicao_categorias(data_inicio, data_fim)
    
    # Verificar se retornou um dicionu00e1rio
    assert isinstance(distribuicao, dict)
    
    # Verificar se as chaves esperadas estu00e3o presentes
    assert 'labels' in distribuicao
    assert 'valores' in distribuicao
    
    # Verificar se os tamanhos das listas su00e3o iguais
    assert len(distribuicao['labels']) == len(distribuicao['valores'])

def test_obter_tendencia_lucratividade(mock_db_query):
    """Testa a obtenu00e7u00e3o da tendu00eancia de lucratividade"""
    # Configurar mock para retornar dados para cada mu00eas
    mock_db_query.all.return_value = [
        (1, date(2023, 1, 1), 1000.0, 600.0, 400.0),
        (2, date(2023, 2, 1), 1200.0, 650.0, 550.0),
        (3, date(2023, 3, 1), 1100.0, 500.0, 600.0)
    ]
    
    # Executar a funu00e7u00e3o
    tendencia = obter_tendencia_lucratividade(meses=3)
    
    # Verificar se retornou um dicionu00e1rio
    assert isinstance(tendencia, dict)
    
    # Verificar se as chaves esperadas estu00e3o presentes
    assert 'meses' in tendencia
    assert 'receitas' in tendencia
    assert 'custos' in tendencia
    assert 'lucros' in tendencia
    
    # Verificar se temos dados para o nu00famero de meses solicitado
    assert len(tendencia['meses']) == 3
    assert len(tendencia['receitas']) == 3
    assert len(tendencia['custos']) == 3
    assert len(tendencia['lucros']) == 3

def test_obter_indicadores_desperdicio(mock_registro_desperdicio):
    """Testa a obtenu00e7u00e3o dos indicadores de desperdu00edcio"""
    # Peru00edodo de teste
    data_inicio = date.today() - timedelta(days=30)
    data_fim = date.today()
    
    # Executar a funu00e7u00e3o
    indicadores = obter_indicadores_desperdicio(data_inicio, data_fim)
    
    # Verificar se retornou um dicionu00e1rio
    assert isinstance(indicadores, dict)
    
    # Verificar se as chaves esperadas estu00e3o presentes
    assert 'valor_total' in indicadores
    assert 'quantidade_total' in indicadores
    assert 'categorias' in indicadores
    
    # Verificar se os valores estu00e3o corretos (baseado nos mocks)
    assert indicadores['valor_total'] == 40.0  # 25.00 + 15.00
    assert indicadores['quantidade_total'] == 4.0  # 2.5 + 1.5

def test_index_route(client, mock_historico_vendas, mock_prato, mock_custo_indireto, mock_registro_desperdicio):
    """Testa a rota principal do dashboard"""
    # Configurar mocks para as funu00e7u00f5es auxiliares
    with patch('app.routes.dashboard.views.calcular_metricas_principais') as mock_metricas, \
         patch('app.routes.dashboard.views.obter_dados_diarios') as mock_dados_diarios, \
         patch('app.routes.dashboard.views.obter_top_pratos') as mock_top_pratos, \
         patch('app.routes.dashboard.views.obter_distribuicao_categorias') as mock_distribuicao, \
         patch('app.routes.dashboard.views.obter_tendencia_lucratividade') as mock_tendencia, \
         patch('app.routes.dashboard.views.obter_indicadores_desperdicio') as mock_indicadores:
        
        # Configurar retornos dos mocks
        mock_metricas.return_value = {
            'receita_total': 1000.0,
            'custo_total': 600.0,
            'lucro': 400.0,
            'margem': 40.0
        }
        
        mock_dados_diarios.return_value = {
            'labels': ['01/05', '02/05', '03/05'],
            'receitas': [300, 350, 350],
            'custos': [180, 200, 220],
            'lucros': [120, 150, 130]
        }
        
        mock_top_pratos.return_value = [
            {'id': 1, 'nome': 'Prato 1', 'quantidade_vendida': 10, 'receita': 500, 'custo': 250, 'lucro': 250, 'margem': 50.0},
            {'id': 2, 'nome': 'Prato 2', 'quantidade_vendida': 8, 'receita': 400, 'custo': 240, 'lucro': 160, 'margem': 40.0}
        ]
        
        mock_distribuicao.return_value = {
            'labels': ['Principal', 'Entrada', 'Sobremesa'],
            'valores': [60, 25, 15]
        }
        
        mock_tendencia.return_value = {
            'meses': ['Jan', 'Fev', 'Mar'],
            'receitas': [900, 950, 1000],
            'custos': [540, 570, 600],
            'lucros': [360, 380, 400]
        }
        
        mock_indicadores.return_value = {
            'valor_total': 120.0,
            'quantidade_total': 10.5,
            'categorias': [
                {'nome': 'Sobras', 'valor': 80.0, 'quantidade': 7.0, 'percentual': 66.7},
                {'nome': 'Vencidos', 'valor': 40.0, 'quantidade': 3.5, 'percentual': 33.3}
            ]
        }
        
        # Fazer a requisiu00e7u00e3o
        response = client.get(url_for('dashboard.index'))
        
        # Verificar resposta
        assert response.status_code == 200
        
        # Verificar se todas as funu00e7u00f5es auxiliares foram chamadas
        mock_metricas.assert_called_once()
        mock_dados_diarios.assert_called_once()
        mock_top_pratos.assert_called_once()
        mock_distribuicao.assert_called_once()
        mock_tendencia.assert_called_once()
        mock_indicadores.assert_called_once()

def test_relatorio_pratos_route(client, mock_prato, mock_historico_vendas):
    """Testa a rota de relatu00f3rio de lucratividade por prato"""
    # Configurar mock para retornar dados de pratos
    with patch('app.routes.dashboard.views.obter_top_pratos') as mock_top_pratos:
        mock_top_pratos.return_value = [
            {'id': 1, 'nome': 'Prato 1', 'quantidade_vendida': 10, 'receita': 500, 'custo': 250, 'lucro': 250, 'margem': 50.0},
            {'id': 2, 'nome': 'Prato 2', 'quantidade_vendida': 8, 'receita': 400, 'custo': 240, 'lucro': 160, 'margem': 40.0}
        ]
        
        # Fazer a requisiu00e7u00e3o
        response = client.get(url_for('dashboard.relatorio_pratos'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Relat\xc3\xb3rio de Lucratividade por Prato' in response.data
        
        # Verificar se a funu00e7u00e3o auxiliar foi chamada
        mock_top_pratos.assert_called_once()

def test_relatorio_categorias_route(client):
    """Testa a rota de relatu00f3rio de lucratividade por categoria"""
    # Configurar mock para retornar dados de categorias
    with patch('app.routes.dashboard.views.obter_distribuicao_categorias') as mock_distribuicao, \
         patch('app.routes.dashboard.views.db.session.query') as mock_query:
         
        mock_distribuicao.return_value = {
            'labels': ['Principal', 'Entrada', 'Sobremesa'],
            'valores': [60, 25, 15]
        }
        
        # Mock para a query que retorna detalhes das categorias
        mock_results = [
            ("Principal", 10, 500.0, 250.0, 250.0),
            ("Entrada", 5, 200.0, 120.0, 80.0),
            ("Sobremesa", 3, 150.0, 90.0, 60.0)
        ]
        mock_query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_results
        
        # Fazer a requisiu00e7u00e3o
        response = client.get(url_for('dashboard.relatorio_categorias'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Relat\xc3\xb3rio de Lucratividade por Categoria' in response.data
        
        # Verificar se a funu00e7u00e3o auxiliar foi chamada
        mock_distribuicao.assert_called_once()
