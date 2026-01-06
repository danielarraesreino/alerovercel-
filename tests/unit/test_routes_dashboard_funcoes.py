import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock, PropertyMock
import json
import pandas as pd

from app.routes.dashboard.views import (
    calcular_metricas_principais,
    obter_dados_diarios,
    obter_top_pratos,
    obter_distribuicao_categorias,
    obter_tendencia_lucratividade,
    obter_indicadores_desperdicio
)
from app.models.modelo_prato import Prato
from app.models.modelo_produto import Produto
from app.models.modelo_cardapio import Cardapio, CardapioItem, CardapioSecao
from app.models.modelo_previsao import HistoricoVendas
from app.models.modelo_desperdicio import RegistroDesperdicio
from app.models.modelo_custo import CustoIndireto

@pytest.fixture
def mock_vendas():
    """Mock para o histórico de vendas"""
    venda1 = MagicMock(spec=HistoricoVendas)
    venda1.id = 1
    venda1.data = date(2023, 5, 15)
    venda1.cardapio_item_id = 1
    venda1.prato_id = None
    venda1.quantidade = 2
    venda1.valor_total = Decimal('59.80')
    
    venda2 = MagicMock(spec=HistoricoVendas)
    venda2.id = 2
    venda2.data = date(2023, 5, 16)
    venda2.cardapio_item_id = None
    venda2.prato_id = 1
    venda2.quantidade = 3
    venda2.valor_total = Decimal('89.70')
    
    return [venda1, venda2]

@pytest.fixture
def mock_cardapio_item():
    """Mock para item de cardápio"""
    item = MagicMock(spec=CardapioItem)
    item.id = 1
    item.prato_id = 2
    item.preco_venda = Decimal('29.90')
    item.preco_custo = Decimal('10.50')
    item.prato = MagicMock(
        nome="Prato do Cardápio",
        categoria="Principal",
        custo_total=Decimal('10.50')
    )
    return item

@pytest.fixture
def mock_prato():
    """Mock para prato"""
    prato = MagicMock(spec=Prato)
    prato.id = 1
    prato.nome = "Prato Teste"
    prato.categoria = "Entrada"
    prato.preco_venda = Decimal('29.90')
    prato.custo_total = Decimal('12.00')
    return prato

@pytest.fixture
def mock_custos_indiretos():
    """Mock para custos indiretos"""
    custo1 = MagicMock(spec=CustoIndireto)
    custo1.id = 1
    custo1.descricao = "Aluguel"
    custo1.valor = Decimal('1000.00')
    custo1.data_referencia = date(2023, 5, 15)
    
    custo2 = MagicMock(spec=CustoIndireto)
    custo2.id = 2
    custo2.descricao = "Energia"
    custo2.valor = Decimal('500.00')
    custo2.data_referencia = date(2023, 5, 16)
    
    return [custo1, custo2]

@pytest.fixture
def mock_registros_desperdicio():
    """Mock para registros de desperdício"""
    reg1 = MagicMock(spec=RegistroDesperdicio)
    reg1.id = 1
    reg1.data = date(2023, 5, 15)
    reg1.quantidade = 2.5
    reg1.valor = Decimal('25.00')
    reg1.categoria = MagicMock(nome="Sobras")
    
    reg2 = MagicMock(spec=RegistroDesperdicio)
    reg2.id = 2
    reg2.data = date(2023, 5, 16)
    reg2.quantidade = 1.8
    reg2.valor = Decimal('18.00')
    reg2.categoria = MagicMock(nome="Vencidos")
    
    return [reg1, reg2]

def test_calcular_metricas_principais(mock_vendas, mock_cardapio_item, mock_prato, mock_custos_indiretos):
    """Testa a função de cálculo de métricas principais"""
    with patch('app.routes.dashboard.views.HistoricoVendas.query') as mock_vendas_query, \
         patch('app.routes.dashboard.views.CardapioItem.query') as mock_item_query, \
         patch('app.routes.dashboard.views.Prato.query') as mock_prato_query, \
         patch('app.routes.dashboard.views.CustoIndireto.query') as mock_custo_query:
        
        # Configurar mocks para as consultas
        mock_vendas_filter = MagicMock()
        mock_vendas_filter.all.return_value = mock_vendas
        mock_vendas_query.filter.return_value = mock_vendas_filter
        
        mock_item_query.get.return_value = mock_cardapio_item
        mock_prato_query.get.return_value = mock_prato
        
        mock_custos_filter = MagicMock()
        mock_custos_filter.all.return_value = mock_custos_indiretos
        mock_custo_query.filter.return_value = mock_custos_filter
        
        # Chamar a função
        data_inicio = date(2023, 5, 1)
        data_fim = date(2023, 5, 31)
        resultado = calcular_metricas_principais(data_inicio, data_fim)
        
        # Verificar resultados
        assert "receita_total" in resultado
        assert "custo_total" in resultado
        assert "lucro" in resultado
        assert "margem" in resultado
        
        # Verificar cálculos específicos
        # Receita total: 59.80 + 89.70 = 149.50
        assert resultado["receita_total"] == 149.50
        
        # Custo total: (10.50 * 2) + (12.00 * 3) + 1000.00 + 500.00 = 1557.00
        assert resultado["custo_total"] == 1557.00
        
        # Lucro: 149.50 - 1557.00 = -1407.50
        assert resultado["lucro"] == -1407.50
        
        # Margem: -1407.50 / 149.50 = -9.41 (ou -941%)
        assert resultado["margem"] < 0

def test_obter_dados_diarios(mock_vendas, mock_custos_indiretos):
    """Testa a função de obtenção de dados diários"""
    with patch('app.routes.dashboard.views.HistoricoVendas.query') as mock_vendas_query, \
         patch('app.routes.dashboard.views.CustoIndireto.query') as mock_custo_query, \
         patch('app.routes.dashboard.views.db.session') as mock_session:
        
        # Configurar mocks para as consultas SQL
        mock_group_by_result = [
            (date(2023, 5, 15), 59.80, None),
            (date(2023, 5, 16), 89.70, None)
        ]
        mock_session.query.return_value.filter.return_value.group_by.return_value.all.return_value = mock_group_by_result
        
        # Configurar mocks para custos indiretos
        mock_custos_filter = MagicMock()
        mock_custos_filter.all.return_value = mock_custos_indiretos
        mock_custo_query.filter.return_value = mock_custos_filter
        
        # Chamar a função
        data_inicio = date(2023, 5, 1)
        data_fim = date(2023, 5, 31)
        resultado = obter_dados_diarios(data_inicio, data_fim)
        
        # Verificar resultado
        assert "datas" in resultado
        assert "receitas" in resultado
        assert "custos" in resultado
        assert "lucros" in resultado
        
        # Verificar que as datas foram processadas
        assert len(resultado["datas"]) == 2
        assert "15/05/2023" in resultado["datas"]
        assert "16/05/2023" in resultado["datas"]

def test_obter_top_pratos(mock_vendas, mock_prato):
    """Testa a função de obtenção dos pratos mais lucrativos"""
    with patch('app.routes.dashboard.views.db.session') as mock_session:
        # Configurar mock para a consulta SQL
        mock_query_result = [
            (1, "Prato 1", 10, 250.00, 100.00, 150.00),
            (2, "Prato 2", 5, 150.00, 75.00, 75.00),
            (3, "Prato 3", 8, 200.00, 120.00, 80.00)
        ]
        mock_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.\
            order_by.return_value.limit.return_value.all.return_value = mock_query_result
        
        # Chamar a função
        data_inicio = date(2023, 5, 1)
        data_fim = date(2023, 5, 31)
        resultado = obter_top_pratos(data_inicio, data_fim, limite=3)
        
        # Verificar resultado
        assert len(resultado) == 3
        assert resultado[0]["nome"] == "Prato 1"
        assert resultado[0]["lucro"] == 150.00
        assert resultado[1]["nome"] == "Prato 3"
        assert resultado[1]["lucro"] == 80.00
        assert resultado[2]["nome"] == "Prato 2"
        assert resultado[2]["lucro"] == 75.00

def test_obter_distribuicao_categorias():
    """Testa a função de obtenção da distribuição por categorias"""
    with patch('app.routes.dashboard.views.db.session') as mock_session:
        # Configurar mock para a consulta SQL
        mock_query_result = [
            ("Entrada", 150.00, 60.00, 90.00),
            ("Principal", 350.00, 175.00, 175.00),
            ("Sobremesa", 100.00, 40.00, 60.00)
        ]
        mock_session.query.return_value.outerjoin.return_value.filter.return_value.group_by.return_value.\
            all.return_value = mock_query_result
        
        # Chamar a função
        data_inicio = date(2023, 5, 1)
        data_fim = date(2023, 5, 31)
        resultado = obter_distribuicao_categorias(data_inicio, data_fim)
        
        # Verificar resultado
        assert len(resultado) == 3
        assert resultado[0]["categoria"] == "Entrada"
        assert resultado[0]["receita"] == 150.00
        assert resultado[0]["custo"] == 60.00
        assert resultado[0]["lucro"] == 90.00

def test_obter_tendencia_lucratividade():
    """Testa a função de obtenção da tendência de lucratividade"""
    with patch('app.routes.dashboard.views.datetime') as mock_datetime, \
         patch('app.routes.dashboard.views.calcular_metricas_principais') as mock_calcular:
        
        # Configurar mock para datetime.now()
        mock_today = datetime(2023, 6, 15)
        mock_datetime.now.return_value = mock_today
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        # Configurar mock para calcular_metricas_principais
        mock_calcular.side_effect = [
            {"receita_total": 2000.00, "custo_total": 1500.00, "lucro": 500.00, "margem": 25.0},
            {"receita_total": 2200.00, "custo_total": 1600.00, "lucro": 600.00, "margem": 27.3},
            {"receita_total": 2100.00, "custo_total": 1550.00, "lucro": 550.00, "margem": 26.2},
            {"receita_total": 2300.00, "custo_total": 1650.00, "lucro": 650.00, "margem": 28.3},
            {"receita_total": 2500.00, "custo_total": 1750.00, "lucro": 750.00, "margem": 30.0},
            {"receita_total": 2400.00, "custo_total": 1700.00, "lucro": 700.00, "margem": 29.2}
        ]
        
        # Chamar a função
        resultado = obter_tendencia_lucratividade(meses=6)
        
        # Verificar resultado
        assert "meses" in resultado
        assert "receitas" in resultado
        assert "custos" in resultado
        assert "lucros" in resultado
        assert "margens" in resultado
        
        assert len(resultado["meses"]) == 6
        assert len(resultado["receitas"]) == 6
        assert len(resultado["custos"]) == 6
        assert len(resultado["lucros"]) == 6
        assert len(resultado["margens"]) == 6

def test_obter_indicadores_desperdicio(mock_registros_desperdicio):
    """Testa a função de obtenção dos indicadores de desperdício"""
    with patch('app.routes.dashboard.views.RegistroDesperdicio.query') as mock_reg_query, \
         patch('app.routes.dashboard.views.db.session') as mock_session:
        
        # Configurar mock para a consulta de registros
        mock_registros_filter = MagicMock()
        mock_registros_filter.all.return_value = mock_registros_desperdicio
        mock_reg_query.filter.return_value = mock_registros_filter
        
        # Configurar mock para a consulta SQL de categorias
        mock_query_result = [
            ("Sobras", 25.00),
            ("Vencidos", 18.00)
        ]
        mock_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.\
            order_by.return_value.all.return_value = mock_query_result
        
        # Chamar a função
        data_inicio = date(2023, 5, 1)
        data_fim = date(2023, 5, 31)
        resultado = obter_indicadores_desperdicio(data_inicio, data_fim)
        
        # Verificar resultado
        assert "total_desperdicio" in resultado
        assert "categorias" in resultado
        assert "valores" in resultado
        assert "porcentagens" in resultado
        
        # Verificar valores calculados
        assert resultado["total_desperdicio"] == 43.00  # 25.00 + 18.00
        assert len(resultado["categorias"]) == 2
        assert "Sobras" in resultado["categorias"]
        assert "Vencidos" in resultado["categorias"]
