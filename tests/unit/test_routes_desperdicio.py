import pytest
from flask import url_for
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto

@pytest.fixture
def mock_categorias():
    """Mock para categorias de desperdu00edcio"""
    cat1 = MagicMock(spec=CategoriaDesperdicio)
    cat1.id = 1
    cat1.nome = "Sobras"
    cat1.descricao = "Sobras de produu00e7u00e3o"
    cat1.cor = "#FF5733"
    cat1.ativa = True
    
    cat2 = MagicMock(spec=CategoriaDesperdicio)
    cat2.id = 2
    cat2.nome = "Vencidos"
    cat2.descricao = "Produtos vencidos"
    cat2.cor = "#C70039"
    cat2.ativa = True
    
    return [cat1, cat2]

@pytest.fixture
def mock_produtos():
    """Mock para produtos"""
    prod1 = MagicMock(spec=Produto)
    prod1.id = 1
    prod1.nome = "Produto Teste 1"
    prod1.codigo = "PT001"
    prod1.unidade_medida = "kg"
    prod1.preco_unitario = Decimal('25.90')
    
    prod2 = MagicMock(spec=Produto)
    prod2.id = 2
    prod2.nome = "Produto Teste 2"
    prod2.codigo = "PT002"
    prod2.unidade_medida = "un"
    prod2.preco_unitario = Decimal('15.50')
    
    return [prod1, prod2]

@pytest.fixture
def mock_registros(mock_categorias, mock_produtos):
    """Mock para registros de desperdu00edcio"""
    reg1 = MagicMock(spec=RegistroDesperdicio)
    reg1.id = 1
    reg1.categoria_id = mock_categorias[0].id
    reg1.categoria = mock_categorias[0]
    reg1.produto_id = mock_produtos[0].id
    reg1.produto = mock_produtos[0]
    reg1.quantidade = 2.5
    reg1.unidade_medida = "kg"
    reg1.valor_estimado = Decimal('64.75')  # 25.90 * 2.5
    reg1.data_registro = date.today() - timedelta(days=5)
    reg1.motivo = "Sobra de produu00e7u00e3o"
    reg1.responsavel = "Jou00e3o"
    
    reg2 = MagicMock(spec=RegistroDesperdicio)
    reg2.id = 2
    reg2.categoria_id = mock_categorias[1].id
    reg2.categoria = mock_categorias[1]
    reg2.produto_id = mock_produtos[1].id
    reg2.produto = mock_produtos[1]
    reg2.quantidade = 3
    reg2.unidade_medida = "un"
    reg2.valor_estimado = Decimal('46.50')  # 15.50 * 3
    reg2.data_registro = date.today() - timedelta(days=2)
    reg2.motivo = "Produto vencido"
    reg2.responsavel = "Maria"
    
    return [reg1, reg2]

@pytest.fixture
def mock_metas(mock_categorias):
    """Mock para metas de desperdu00edcio"""
    meta1 = MagicMock(spec=MetaDesperdicio)
    meta1.id = 1
    meta1.categoria_id = mock_categorias[0].id
    meta1.categoria = mock_categorias[0]
    meta1.valor_inicial = Decimal('1000.00')
    meta1.meta_reducao_percentual = 20.0
    meta1.data_inicio = date.today() - timedelta(days=30)
    meta1.data_fim = date.today() + timedelta(days=30)
    meta1.descricao = "Reduzir desperdu00edcio de sobras em 20%"
    meta1.responsavel = "Gerente"
    
    meta2 = MagicMock(spec=MetaDesperdicio)
    meta2.id = 2
    meta2.categoria_id = None  # Meta geral para todas as categorias
    meta2.categoria = None
    meta2.valor_inicial = Decimal('2500.00')
    meta2.meta_reducao_percentual = 15.0
    meta2.data_inicio = date.today() - timedelta(days=15)
    meta2.data_fim = date.today() + timedelta(days=45)
    meta2.descricao = "Reduzir desperdu00edcio geral em 15%"
    meta2.responsavel = "Diretor"
    
    return [meta1, meta2]

def test_index_route(client):
    """Testa a rota principal do dashboard de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_reg, \
         patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_cat, \
         patch('app.routes.desperdicio.views.MetaDesperdicio') as mock_meta, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Configurar mocks
        mock_reg.query.filter.return_value.all.return_value = [
            MagicMock(valor_estimado=Decimal('50.00'), data_registro=date.today()),
            MagicMock(valor_estimado=Decimal('75.00'), data_registro=date.today() - timedelta(days=1))
        ]
        
        mock_cat.query.all.return_value = [
            MagicMock(id=1, nome="Sobras", cor="#FF5733")
        ]
        
        mock_meta.query.filter.return_value.all.return_value = [
            MagicMock(
                valor_inicial=Decimal('1000.00'),
                meta_reducao_percentual=20,
                data_inicio=date.today() - timedelta(days=30),
                data_fim=date.today() + timedelta(days=30)
            )
        ]
        
        # Fazer request
        response = client.get(url_for('desperdicio.index'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Dashboard de Desperd\xc3\xadcio' in response.data

def test_categorias_route(client, mock_categorias):
    """Testa a rota de listagem de categorias de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_model:
        # Configurar mock
        mock_model.query.all.return_value = mock_categorias
        
        # Fazer request
        response = client.get(url_for('desperdicio.categorias'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categorias de Desperd\xc3\xadcio' in response.data
        assert b'Sobras' in response.data
        assert b'Vencidos' in response.data

def test_criar_categoria_get_route(client):
    """Testa a rota GET para criar categoria de desperdu00edcio"""
    # Fazer request
    response = client.get(url_for('desperdicio.criar_categoria'))
    
    # Verificar resposta
    assert response.status_code == 200
    assert b'Nova Categoria de Desperd\xc3\xadcio' in response.data
    assert b'<form' in response.data
    assert b'method="post"' in response.data

def test_criar_categoria_post_route(client):
    """Testa a rota POST para criar categoria de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_model, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Preparar dados do formulu00e1rio
        form_data = {
            'nome': 'Nova Categoria',
            'descricao': 'Descriu00e7u00e3o da nova categoria',
            'cor': '#3366FF'
        }
        
        # Fazer request
        response = client.post(
            url_for('desperdicio.criar_categoria'),
            data=form_data,
            follow_redirects=True
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categoria criada com sucesso' in response.data

def test_editar_categoria_get_route(client, mock_categorias):
    """Testa a rota GET para editar categoria de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_model:
        # Configurar mock
        mock_model.query.get.return_value = mock_categorias[0]
        
        # Fazer request
        response = client.get(url_for('desperdicio.editar_categoria', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Editar Categoria de Desperd\xc3\xadcio' in response.data
        assert b'Sobras' in response.data
        assert b'#FF5733' in response.data

def test_editar_categoria_post_route(client, mock_categorias):
    """Testa a rota POST para editar categoria de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_model, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Configurar mock
        mock_model.query.get.return_value = mock_categorias[0]
        
        # Preparar dados do formulu00e1rio
        form_data = {
            'nome': 'Sobras Atualizadas',
            'descricao': 'Descriu00e7u00e3o atualizada',
            'cor': '#FF9900'
        }
        
        # Fazer request
        response = client.post(
            url_for('desperdicio.editar_categoria', id=1),
            data=form_data,
            follow_redirects=True
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categoria atualizada com sucesso' in response.data

def test_registros_route(client, mock_registros):
    """Testa a rota de listagem de registros de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_model, \
         patch('app.routes.desperdicio.views.request') as mock_request:
        
        # Configurar mocks
        mock_model.query.filter.return_value.order_by.return_value.all.return_value = mock_registros
        mock_request.args = {}
        
        # Fazer request
        response = client.get(url_for('desperdicio.registros'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registros de Desperd\xc3\xadcio' in response.data
        assert b'Sobra de produ\xc3\xa7\xc3\xa3o' in response.data
        assert b'Produto vencido' in response.data

def test_registrar_desperdicio_get_route(client, mock_categorias, mock_produtos):
    """Testa a rota GET para registrar desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_cat, \
         patch('app.routes.desperdicio.views.Produto') as mock_prod:
        
        # Configurar mocks
        mock_cat.query.filter_by.return_value.all.return_value = mock_categorias
        mock_prod.query.filter_by.return_value.all.return_value = mock_produtos
        
        # Fazer request
        response = client.get(url_for('desperdicio.registrar_desperdicio'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registrar Desperd\xc3\xadcio' in response.data
        assert b'<form' in response.data
        assert b'method="post"' in response.data

def test_registrar_desperdicio_post_route(client, mock_categorias, mock_produtos):
    """Testa a rota POST para registrar desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_cat, \
         patch('app.routes.desperdicio.views.Produto') as mock_prod, \
         patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_reg, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Configurar mocks
        mock_cat.query.get.return_value = mock_categorias[0]
        mock_prod.query.get.return_value = mock_produtos[0]
        
        # Preparar dados do formulu00e1rio
        form_data = {
            'categoria_id': 1,
            'produto_id': 1,
            'quantidade': 2.5,
            'unidade_medida': 'kg',
            'valor_estimado': 64.75,
            'data_registro': date.today().strftime('%Y-%m-%d'),
            'motivo': 'Sobra de produu00e7u00e3o',
            'responsavel': 'Jou00e3o',
            'local': 'Cozinha',
            'descricao': 'Sobra do almou00e7o'
        }
        
        # Fazer request
        response = client.post(
            url_for('desperdicio.registrar_desperdicio'),
            data=form_data,
            follow_redirects=True
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Desperd\xc3\xadcio registrado com sucesso' in response.data

def test_visualizar_registro_route(client, mock_registros):
    """Testa a rota para visualizar um registro de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_model:
        # Configurar mock
        mock_model.query.get.return_value = mock_registros[0]
        
        # Fazer request
        response = client.get(url_for('desperdicio.visualizar_registro', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Detalhes do Registro de Desperd\xc3\xadcio' in response.data
        assert b'Sobra de produ\xc3\xa7\xc3\xa3o' in response.data
        assert b'Jo\xc3\xa3o' in response.data

def test_metas_route(client, mock_metas):
    """Testa a rota de listagem de metas de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.MetaDesperdicio') as mock_model:
        # Configurar mock
        mock_model.query.order_by.return_value.all.return_value = mock_metas
        
        # Fazer request
        response = client.get(url_for('desperdicio.metas'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Metas de Redu\xc3\xa7\xc3\xa3o de Desperd\xc3\xadcio' in response.data
        assert b'Reduzir desperd\xc3\xadcio de sobras em 20%' in response.data
        assert b'Reduzir desperd\xc3\xadcio geral em 15%' in response.data

def test_criar_meta_get_route(client, mock_categorias):
    """Testa a rota GET para criar meta de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_cat:
        # Configurar mock
        mock_cat.query.filter_by.return_value.all.return_value = mock_categorias
        
        # Fazer request
        response = client.get(url_for('desperdicio.criar_meta'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Nova Meta de Redu\xc3\xa7\xc3\xa3o de Desperd\xc3\xadcio' in response.data
        assert b'<form' in response.data
        assert b'method="post"' in response.data

def test_criar_meta_post_route(client, mock_categorias):
    """Testa a rota POST para criar meta de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.CategoriaDesperdicio') as mock_cat, \
         patch('app.routes.desperdicio.views.MetaDesperdicio') as mock_meta, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Configurar mock
        mock_cat.query.get.return_value = mock_categorias[0]
        
        # Preparar dados do formulu00e1rio
        form_data = {
            'categoria_id': 1,
            'valor_inicial': 1000.00,
            'meta_reducao_percentual': 20.0,
            'data_inicio': date.today().strftime('%Y-%m-%d'),
            'data_fim': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'descricao': 'Meta de teste',
            'responsavel': 'Gerente de Teste',
            'acoes_propostas': 'Au00e7u00f5es para reduzir desperdu00edcio'
        }
        
        # Fazer request
        response = client.post(
            url_for('desperdicio.criar_meta'),
            data=form_data,
            follow_redirects=True
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Meta criada com sucesso' in response.data

def test_visualizar_meta_route(client, mock_metas):
    """Testa a rota para visualizar uma meta de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.MetaDesperdicio') as mock_model, \
         patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_reg, \
         patch('app.routes.desperdicio.views.db.session'):
        
        # Configurar mocks
        mock_model.query.get.return_value = mock_metas[0]
        
        # Mock para dados de progresso
        mock_reg_query = MagicMock()
        mock_reg_query.filter.return_value.all.return_value = [
            MagicMock(valor_estimado=Decimal('50.00')),
            MagicMock(valor_estimado=Decimal('75.00'))
        ]
        mock_reg.query = mock_reg_query
        
        # Fazer request
        response = client.get(url_for('desperdicio.visualizar_meta', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Detalhes da Meta de Redu\xc3\xa7\xc3\xa3o' in response.data
        assert b'Reduzir desperd\xc3\xadcio de sobras em 20%' in response.data
        assert b'Progresso da Meta' in response.data

def test_relatorios_route(client):
    """Testa a rota de relatu00f3rios de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.db.session'):
        # Fazer request
        response = client.get(url_for('desperdicio.relatorios'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Relat\xc3\xb3rios de Desperd\xc3\xadcio' in response.data
        assert b'Per\xc3\xadodo de An\xc3\xa1lise' in response.data

def test_api_estatisticas_route(client, mock_registros):
    """Testa a API de estatu00edsticas de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.RegistroDesperdicio') as mock_model, \
         patch('app.routes.desperdicio.views.db.session') as mock_session:
        
        # Configurar mocks
        mock_model.query.filter.return_value.all.return_value = mock_registros
        
        # Configurar mock para consulta SQL
        mock_query_result = [
            ("Sobras", 64.75),
            ("Vencidos", 46.50)
        ]
        mock_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.\
            order_by.return_value.all.return_value = mock_query_result
        
        # Fazer request
        response = client.get(
            url_for('desperdicio.api_estatisticas'),
            query_string={
                'inicio': (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'fim': date.today().strftime('%Y-%m-%d')
            }
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "categorias" in data
        assert "valores" in data
        assert "total" in data
        assert data["total"] == 111.25  # 64.75 + 46.50

def test_api_tendencia_route(client):
    """Testa a API de tendu00eancia de desperdu00edcio"""
    with patch('app.routes.desperdicio.views.db.session') as mock_session:
        # Configurar mock para consulta SQL
        hoje = date.today()
        mock_query_result = [
            (hoje - timedelta(days=6), 50.00),
            (hoje - timedelta(days=5), 45.00),
            (hoje - timedelta(days=4), 60.00),
            (hoje - timedelta(days=3), 55.00),
            (hoje - timedelta(days=2), 40.00),
            (hoje - timedelta(days=1), 35.00),
            (hoje, 30.00)
        ]
        mock_session.query.return_value.filter.return_value.group_by.return_value.\
            order_by.return_value.all.return_value = mock_query_result
        
        # Fazer request
        response = client.get(
            url_for('desperdicio.api_tendencia'),
            query_string={'dias': 7}
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "datas" in data
        assert "valores" in data
        assert len(data["datas"]) == 7
        assert len(data["valores"]) == 7
