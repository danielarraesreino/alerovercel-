import pytest
from flask import url_for
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.models.modelo_produto import Produto
from app.models.modelo_fornecedor import Fornecedor
from app.models.modelo_estoque import EstoqueMovimentacao

@pytest.fixture
def mock_produto():
    """Mock para um produto de teste"""
    produto = MagicMock()
    produto.id = 1
    produto.nome = "Produto Teste"
    produto.codigo = "PT001"
    produto.descricao = "Descrição do produto teste"
    produto.categoria = "Alimentos"
    produto.unidade_medida = "kg"
    produto.estoque_minimo = 10.0
    produto.estoque_atual = 15.0
    produto.preco_unitario = Decimal('25.90')
    produto.fornecedor_id = 1
    produto.fornecedor = MagicMock(razao_social="Fornecedor Teste")
    return produto

@pytest.fixture
def mock_fornecedores():
    """Mock para lista de fornecedores"""
    return [
        MagicMock(id=1, razao_social="Fornecedor A"),
        MagicMock(id=2, razao_social="Fornecedor B")
    ]

def test_index_route(client):
    """Testa a rota de listagem de produtos"""
    with patch('app.routes.produtos.views.Produto') as mock_model, \
         patch('app.routes.produtos.views.Fornecedor') as mock_fornecedor, \
         patch('app.routes.produtos.views.db.session') as mock_session:
        
        # Configurar mock de paginação
        mock_pagination = MagicMock()
        mock_pagination.items = [MagicMock(id=1, nome="Produto Teste", categoria="Alimentos")]
        mock_pagination.pages = 1
        mock_pagination.page = 1
        
        # Configurar mock da consulta
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_model.query = mock_query
        
        # Mock para lista de categorias
        mock_distinct = MagicMock()
        mock_distinct.all.return_value = [("Alimentos",), ("Bebidas",)]
        mock_session.query().distinct.return_value = mock_distinct
        
        # Mock para lista de fornecedores
        mock_fornecedor_query = MagicMock()
        mock_fornecedor_query.order_by.return_value = mock_fornecedor_query
        mock_fornecedor_query.all.return_value = [MagicMock(id=1, razao_social="Fornecedor Teste")]
        mock_fornecedor.query = mock_fornecedor_query
        
        response = client.get(url_for('produtos.index'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Produtos" in response.data
        assert b"Produto Teste" in response.data
        assert b"Alimentos" in response.data

def test_criar_get_route(client, mock_fornecedores):
    """Testa a rota GET para criar um produto"""
    with patch('app.routes.produtos.views.Fornecedor') as mock_fornecedor:
        # Configurar mock para lista de fornecedores
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_fornecedores
        mock_fornecedor.query = mock_query
        
        response = client.get(url_for('produtos.criar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Cadastrar Novo Produto" in response.data
        assert b"Fornecedor A" in response.data
        assert b"Fornecedor B" in response.data

def test_criar_post_route(client, mock_fornecedores):
    """Testa a rota POST para criar um produto"""
    with patch('app.routes.produtos.views.Produto') as mock_model, \
         patch('app.routes.produtos.views.Fornecedor') as mock_fornecedor, \
         patch('app.routes.produtos.views.db.session') as mock_session:
        
        # Configurar mock para lista de fornecedores
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_fornecedores
        mock_fornecedor.query = mock_query
        
        # Mock para criação do produto
        mock_model.return_value = MagicMock(id=1)
        
        # Dados do formulário
        form_data = {
            'nome': 'Novo Produto',
            'codigo': 'NP001',
            'descricao': 'Descrição do novo produto',
            'categoria': 'Alimentos',
            'unidade_medida': 'kg',
            'estoque_minimo': '10.0',
            'estoque_atual': '15.0',
            'preco_unitario': '25.90',
            'fornecedor_id': '1'
        }
        
        response = client.post(url_for('produtos.criar'), data=form_data, follow_redirects=True)
        
        # Verificar se o modelo foi chamado corretamente
        mock_model.assert_called_once()
        
        # Verificar se os dados foram salvos
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"cadastrado" in response.data.lower()

def test_editar_get_route(client, mock_produto, mock_fornecedores):
    """Testa a rota GET para editar um produto"""
    with patch('app.routes.produtos.views.Produto.query') as mock_query, \
         patch('app.routes.produtos.views.Fornecedor') as mock_fornecedor:
        
        # Configurar mock para retornar o produto
        mock_query.get_or_404.return_value = mock_produto
        
        # Configurar mock para lista de fornecedores
        mock_fornecedor_query = MagicMock()
        mock_fornecedor_query.order_by.return_value = mock_fornecedor_query
        mock_fornecedor_query.all.return_value = mock_fornecedores
        mock_fornecedor.query = mock_fornecedor_query
        
        response = client.get(url_for('produtos.editar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Editar Produto" in response.data
        assert bytes(mock_produto.nome, 'utf-8') in response.data
        assert b"Fornecedor A" in response.data

def test_editar_post_route(client, mock_produto, mock_fornecedores):
    """Testa a rota POST para editar um produto"""
    with patch('app.routes.produtos.views.Produto.query') as mock_query, \
         patch('app.routes.produtos.views.Fornecedor') as mock_fornecedor, \
         patch('app.routes.produtos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o produto
        mock_query.get_or_404.return_value = mock_produto
        
        # Configurar mock para lista de fornecedores
        mock_fornecedor_query = MagicMock()
        mock_fornecedor_query.order_by.return_value = mock_fornecedor_query
        mock_fornecedor_query.all.return_value = mock_fornecedores
        mock_fornecedor.query = mock_fornecedor_query
        
        # Dados do formulário
        form_data = {
            'nome': 'Produto Atualizado',
            'codigo': 'PA001',
            'descricao': 'Descrição atualizada',
            'categoria': 'Bebidas',
            'unidade_medida': 'l',
            'estoque_minimo': '5.0',
            'preco_unitario': '29.90',
            'fornecedor_id': '2'
        }
        
        response = client.post(url_for('produtos.editar', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert mock_produto.nome == 'Produto Atualizado'
        assert mock_produto.codigo == 'PA001'
        assert mock_produto.categoria == 'Bebidas'
        
        # Verificar se as alterações foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_visualizar_route(client, mock_produto):
    """Testa a rota para visualizar detalhes de um produto"""
    with patch('app.routes.produtos.views.Produto.query') as mock_query:
        # Configurar mock para retornar o produto
        mock_query.get_or_404.return_value = mock_produto
        
        response = client.get(url_for('produtos.visualizar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert bytes(mock_produto.nome, 'utf-8') in response.data
        assert bytes(mock_produto.codigo, 'utf-8') in response.data
        assert bytes(str(mock_produto.estoque_atual), 'utf-8') in response.data

def test_ajustar_estoque_get_route(client, mock_produto):
    """Testa a rota GET para ajustar estoque de um produto"""
    with patch('app.routes.produtos.views.Produto.query') as mock_query:
        # Configurar mock para retornar o produto
        mock_query.get_or_404.return_value = mock_produto
        
        response = client.get(url_for('produtos.ajustar_estoque', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Ajustar Estoque" in response.data
        assert bytes(mock_produto.nome, 'utf-8') in response.data

def test_ajustar_estoque_post_route(client, mock_produto):
    """Testa a rota POST para ajustar estoque de um produto"""
    with patch('app.routes.produtos.views.Produto.query') as mock_query, \
         patch('app.routes.produtos.views.EstoqueMovimentacao') as mock_movimentacao, \
         patch('app.routes.produtos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o produto
        mock_query.get_or_404.return_value = mock_produto
        
        # Mock para movimentação de estoque
        mock_movimentacao.return_value = MagicMock(id=1)
        
        # Dados do formulário - adição de estoque
        form_data = {
            'quantidade': '5.0',
            'tipo': 'entrada',
            'observacao': 'Ajuste manual para teste'
        }
        
        response = client.post(url_for('produtos.ajustar_estoque', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se o estoque foi atualizado
        # O valor inicial era 15.0, mais 5.0 = 20.0
        assert mock_produto.estoque_atual == 20.0
        
        # Verificar se a movimentação foi registrada
        assert mock_movimentacao.called
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"ajustado" in response.data.lower()

def test_em_falta_route(client):
    """Testa a rota para listar produtos em falta"""
    with patch('app.routes.produtos.views.EstoqueMovimentacao.get_produtos_em_falta') as mock_em_falta:
        # Configurar mock para retornar produtos em falta
        mock_em_falta.return_value = [
            MagicMock(id=1, nome="Produto em Falta 1", estoque_atual=2.0, estoque_minimo=5.0),
            MagicMock(id=2, nome="Produto em Falta 2", estoque_atual=0.0, estoque_minimo=10.0)
        ]
        
        response = client.get(url_for('produtos.em_falta'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Produtos em Falta" in response.data
        assert b"Produto em Falta 1" in response.data
        assert b"Produto em Falta 2" in response.data

def test_api_listar_route(client, mock_produto):
    """Testa a API de listagem de produtos"""
    with patch('app.routes.produtos.views.Produto') as mock_model:
        # Configurar mock para retornar produtos
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_produto]
        mock_model.query = mock_query
        
        response = client.get(url_for('produtos.api_listar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_produto.id
        assert response.json[0]["nome"] == mock_produto.nome
        assert response.json[0]["codigo"] == mock_produto.codigo

def test_api_buscar_route(client, mock_produto):
    """Testa a API de busca de produtos"""
    with patch('app.routes.produtos.views.Produto') as mock_model:
        # Configurar mock para retornar produtos
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_produto]
        mock_model.query = mock_query
        
        response = client.get(url_for('produtos.api_buscar', termo='teste'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_produto.id
        assert response.json[0]["nome"] == mock_produto.nome
