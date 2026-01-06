import pytest
from flask import url_for
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import json
from decimal import Decimal

from app.models.modelo_estoque import EstoqueMovimentacao
from app.models.modelo_produto import Produto

@pytest.fixture
def mock_movimentacoes():
    """Mock para uma lista de movimentau00e7u00f5es de estoque"""
    # Movimentau00e7u00e3o de entrada
    entrada = MagicMock(spec=EstoqueMovimentacao)
    entrada.id = 1
    entrada.produto_id = 1
    entrada.produto = MagicMock(nome="Produto 1", unidade_medida="kg")
    entrada.quantidade = 5.0
    entrada.tipo = "entrada"
    entrada.data_movimentacao = datetime.now() - timedelta(days=1)
    entrada.referencia = "NF 12345"
    entrada.valor_unitario = Decimal('20.00')
    entrada.observacao = "Entrada de teste"
    entrada.valor_total = Decimal('100.00')
    
    # Movimentau00e7u00e3o de sau00edda
    saida = MagicMock(spec=EstoqueMovimentacao)
    saida.id = 2
    saida.produto_id = 1
    saida.produto = MagicMock(nome="Produto 1", unidade_medida="kg")
    saida.quantidade = 2.0
    saida.tipo = "sau00edda"
    saida.data_movimentacao = datetime.now()
    saida.referencia = "Pedido 789"
    saida.valor_unitario = Decimal('20.00')
    saida.observacao = "Sau00edda de teste"
    saida.valor_total = Decimal('40.00')
    
    return [entrada, saida]

@pytest.fixture
def mock_produtos():
    """Mock para uma lista de produtos"""
    produto1 = MagicMock(spec=Produto)
    produto1.id = 1
    produto1.nome = "Produto 1"
    produto1.unidade_medida = "kg"
    produto1.estoque_atual = 8.0
    produto1.estoque_minimo = 5.0
    produto1.preco_unitario = Decimal('20.00')
    
    produto2 = MagicMock(spec=Produto)
    produto2.id = 2
    produto2.nome = "Produto 2"
    produto2.unidade_medida = "litro"
    produto2.estoque_atual = 3.0
    produto2.estoque_minimo = 5.0
    produto2.preco_unitario = Decimal('15.00')
    
    return [produto1, produto2]

def test_index_route(client, mock_movimentacoes, mock_produtos):
    """Testa a rota de listagem de movimentau00e7u00f5es de estoque"""
    with patch('app.routes.estoque.views.EstoqueMovimentacao') as mock_model, \
         patch('app.routes.estoque.views.Produto') as mock_produto_model:
        
        # Configurar mock para a paginau00e7u00e3o
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = MagicMock(
            items=mock_movimentacoes,
            page=1,
            per_page=20,
            total=2,
            pages=1
        )
        mock_model.query = mock_query
        
        # Mock para a lista de produtos do filtro
        mock_produto_query = MagicMock()
        mock_produto_query.order_by.return_value = mock_produto_query
        mock_produto_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_produto_query
        
        # Testar rota sem filtros
        response = client.get(url_for('estoque.index'))
        assert response.status_code == 200
        assert b"Movimenta\xc3\xa7\xc3\xb5es de Estoque" in response.data
        assert b"Produto 1" in response.data
        assert b"entrada" in response.data.lower()
        assert b"sa\xc3\xadda" in response.data.lower()
        
        # Testar com filtro de produto
        response = client.get(url_for('estoque.index', produto_id=1))
        assert response.status_code == 200
        assert b"Produto 1" in response.data
        
        # Testar com filtro de tipo
        response = client.get(url_for('estoque.index', tipo='entrada'))
        assert response.status_code == 200
        
        # Testar com filtro de datas
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        response = client.get(url_for('estoque.index', data_inicio=data_hoje, data_fim=data_hoje))
        assert response.status_code == 200

def test_entrada_get_route(client, mock_produtos):
    """Testa a rota GET para registrar entrada de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model:
        # Configurar mock para a lista de produtos
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_query
        
        response = client.get(url_for('estoque.entrada'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Registrar Entrada de Estoque" in response.data
        assert b"Produto 1" in response.data
        assert b"Produto 2" in response.data
        assert b"Quantidade" in response.data
        assert b"Valor Unit\xc3\xa1rio" in response.data

def test_entrada_post_route(client, mock_produtos):
    """Testa a rota POST para registrar entrada de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model, \
         patch('app.routes.estoque.views.EstoqueMovimentacao') as mock_movimentacao_model:
        
        # Configurar mock para o produto
        mock_produto_query = MagicMock()
        mock_produto_query.get.return_value = mock_produtos[0]
        mock_produto_model.query = mock_produto_query
        
        # Mock para o mu00e9todo de classe registrar_entrada
        mock_movimentacao_model.registrar_entrada.return_value = MagicMock(id=1)
        
        # Dados do formulu00e1rio
        form_data = {
            'produto_id': '1',
            'quantidade': '5.0',
            'valor_unitario': '20.00',
            'referencia': 'NF 12345',
            'observacao': 'Entrada de teste'
        }
        
        response = client.post(url_for('estoque.entrada'), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se o mu00e9todo foi chamado corretamente
        mock_movimentacao_model.registrar_entrada.assert_called_once_with(
            produto_id=1,
            quantidade=5.0,
            valor_unitario=Decimal('20.00'),
            referencia='NF 12345',
            observacao='Entrada de teste'
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"registrada" in response.data.lower()

def test_saida_get_route(client, mock_produtos):
    """Testa a rota GET para registrar sau00edda de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model:
        # Configurar mock para a lista de produtos
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_query
        
        response = client.get(url_for('estoque.saida'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Registrar Sa\xc3\xadda de Estoque" in response.data
        assert b"Produto 1" in response.data
        assert b"Produto 2" in response.data
        assert b"Quantidade" in response.data

def test_saida_post_route(client, mock_produtos):
    """Testa a rota POST para registrar sau00edda de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model, \
         patch('app.routes.estoque.views.EstoqueMovimentacao') as mock_movimentacao_model:
        
        # Configurar mock para o produto
        mock_produto_query = MagicMock()
        mock_produto_query.get.return_value = mock_produtos[0]
        mock_produto_model.query = mock_produto_query
        
        # Mock para o mu00e9todo de classe registrar_saida
        mock_movimentacao_model.registrar_saida.return_value = MagicMock(id=2)
        
        # Dados do formulu00e1rio
        form_data = {
            'produto_id': '1',
            'quantidade': '2.0',
            'referencia': 'Pedido 789',
            'observacao': 'Sau00edda de teste'
        }
        
        response = client.post(url_for('estoque.saida'), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se o mu00e9todo foi chamado corretamente
        mock_movimentacao_model.registrar_saida.assert_called_once_with(
            produto_id=1,
            quantidade=2.0,
            referencia='Pedido 789',
            observacao='Sau00edda de teste'
        )
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"registrada" in response.data.lower()

def test_saida_post_erro_estoque_insuficiente(client, mock_produtos):
    """Testa a rota POST para sau00edda com estoque insuficiente"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model, \
         patch('app.routes.estoque.views.EstoqueMovimentacao') as mock_movimentacao_model:
        
        # Configurar mock para o produto
        mock_produto_query = MagicMock()
        mock_produto_query.get.return_value = mock_produtos[0]
        mock_produto_model.query = mock_produto_query
        
        # Mock para simular erro de estoque insuficiente
        mock_movimentacao_model.registrar_saida.side_effect = ValueError('Estoque insuficiente')
        
        # Dados do formulu00e1rio
        form_data = {
            'produto_id': '1',
            'quantidade': '20.0',  # Quantidade maior que o estoque
            'referencia': 'Pedido 789',
            'observacao': 'Sau00edda de teste'
        }
        
        response = client.post(url_for('estoque.saida'), 
                              data=form_data, follow_redirects=True)
        
        # Verificar resposta de erro
        assert response.status_code == 200
        assert b"erro" in response.data.lower() or b"insuficiente" in response.data.lower()

def test_detalhe_produto_route(client, mock_produtos, mock_movimentacoes):
    """Testa a rota para detalhes de estoque de um produto"""
    with patch('app.routes.estoque.views.Produto.query') as mock_produto_query, \
         patch('app.routes.estoque.views.EstoqueMovimentacao.query') as mock_movimentacao_query:
        
        # Configurar mock para o produto
        mock_produto_query.get_or_404.return_value = mock_produtos[0]
        
        # Configurar mock para as movimentau00e7u00f5es
        mock_filter = MagicMock()
        mock_filter.order_by.return_value = mock_filter
        mock_filter.limit.return_value = mock_movimentacoes
        mock_movimentacao_query.filter_by.return_value = mock_filter
        
        response = client.get(url_for('estoque.detalhe_produto', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Detalhes do Estoque" in response.data
        assert bytes(mock_produtos[0].nome, 'utf-8') in response.data
        assert b"Estoque Atual" in response.data
        assert b"\xc3\x9altimas Movimenta\xc3\xa7\xc3\xb5es" in response.data

def test_relatorio_route(client, mock_produtos):
    """Testa a rota para relatu00f3rio de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model:
        # Configurar mock para filtragem e ordenau00e7u00e3o
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_query
        
        # Testar sem filtros
        response = client.get(url_for('estoque.relatorio'))
        assert response.status_code == 200
        assert b"Relat\xc3\xb3rio de Estoque" in response.data
        assert b"Produto 1" in response.data
        assert b"Produto 2" in response.data
        
        # Testar com filtro de categoria
        response = client.get(url_for('estoque.relatorio', categoria='Alimentos'))
        assert response.status_code == 200
        
        # Testar com filtro de em_falta=true
        response = client.get(url_for('estoque.relatorio', em_falta='true'))
        assert response.status_code == 200

def test_exportar_relatorio_route(client, mock_produtos):
    """Testa a rota para exportar relatu00f3rio de estoque"""
    with patch('app.routes.estoque.views.Produto') as mock_produto_model, \
         patch('app.routes.estoque.views.pd.DataFrame') as mock_dataframe:
        
        # Configurar mock para filtragem e ordenau00e7u00e3o
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_query
        
        # Mock para o DataFrame e to_csv
        mock_df_instance = MagicMock()
        mock_df_instance.to_csv.return_value = "produto,estoque_atual,estoque_minimo\nProduto 1,8.0,5.0\nProduto 2,3.0,5.0"
        mock_dataframe.return_value = mock_df_instance
        
        response = client.get(url_for('estoque.exportar_relatorio'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert response.headers["Content-Disposition"].startswith("attachment; filename=")

def test_api_movimentacoes_route(client, mock_movimentacoes):
    """Testa a API para obter movimentau00e7u00f5es de um produto"""
    with patch('app.routes.estoque.views.EstoqueMovimentacao.query') as mock_query:
        # Configurar mock para as movimentau00e7u00f5es
        mock_filter = MagicMock()
        mock_filter.order_by.return_value = mock_filter
        mock_filter.limit.return_value = mock_movimentacoes
        mock_query.filter_by.return_value = mock_filter
        
        response = client.get(url_for('estoque.api_movimentacoes', produto_id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json
        assert len(data) == 2
        assert data[0]["tipo"] == "entrada"
        assert data[1]["tipo"] == "sau00edda"

def test_api_em_falta_route(client, mock_produtos):
    """Testa a API para listar produtos com estoque abaixo do mu00ednimo"""
    with patch('app.routes.estoque.views.EstoqueMovimentacao') as mock_model:
        # Configurar mock para produtos em falta
        mock_model.get_produtos_em_falta.return_value = [mock_produtos[1]]  # Produto 2 está abaixo do mínimo
        
        response = client.get(url_for('estoque.api_em_falta'))
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json
        assert len(data) == 1
        assert data[0]["id"] == 2
        assert data[0]["nome"] == "Produto 2"
        assert data[0]["estoque_atual"] == 3.0
        assert data[0]["estoque_minimo"] == 5.0
