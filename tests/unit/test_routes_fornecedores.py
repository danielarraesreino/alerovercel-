import pytest
from flask import url_for
from unittest.mock import patch, MagicMock

from app.models.modelo_fornecedor import Fornecedor

@pytest.fixture
def mock_fornecedor():
    """Mock para um fornecedor de teste"""
    fornecedor = MagicMock()
    fornecedor.id = 1
    fornecedor.cnpj = "12345678000190"
    fornecedor.razao_social = "Fornecedor Teste LTDA"
    fornecedor.nome_fantasia = "Fornecedor Teste"
    fornecedor.endereco = "Rua Teste, 123"
    fornecedor.cidade = "Cidade Teste"
    fornecedor.estado = "SP"
    fornecedor.cep = "01234567"
    fornecedor.telefone = "(11) 1234-5678"
    fornecedor.email = "contato@fornecedorteste.com"
    fornecedor.inscricao_estadual = "123456789"
    return fornecedor

def test_index_route(client):
    """Testa a rota de listagem de fornecedores"""
    with patch('app.routes.fornecedores.views.Fornecedor') as mock_model:
        # Configurar mock de paginau00e7u00e3o
        mock_pagination = MagicMock()
        mock_pagination.items = [MagicMock(id=1, razao_social="Fornecedor Teste")]
        mock_pagination.pages = 1
        mock_pagination.page = 1
        
        # Configurar mock da consulta
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_model.query = mock_query
        
        response = client.get(url_for('fornecedores.index'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Fornecedores" in response.data
        assert b"Fornecedor Teste" in response.data

def test_criar_get_route(client):
    """Testa a rota GET para criar um fornecedor"""
    response = client.get(url_for('fornecedores.criar'))
    
    # Verificar resposta
    assert response.status_code == 200
    assert b"Cadastrar Novo Fornecedor" in response.data
    assert b"CNPJ" in response.data
    assert b"Raz\xc3\xa3o Social" in response.data

def test_criar_post_route_sucesso(client):
    """Testa a rota POST para criar um fornecedor com sucesso"""
    with patch('app.routes.fornecedores.views.Fornecedor') as mock_model, \
         patch('app.routes.fornecedores.views.db.session') as mock_session:
        
        # Configurar mock para verificar se CNPJ ju00e1 existe
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = None  # CNPJ nu00e3o existe
        mock_model.query = mock_query
        
        # Dados do formulu00e1rio
        form_data = {
            'cnpj': '12.345.678/0001-90',
            'razao_social': 'Fornecedor Teste LTDA',
            'nome_fantasia': 'Fornecedor Teste',
            'endereco': 'Rua Teste, 123',
            'cidade': 'Cidade Teste',
            'estado': 'SP',
            'cep': '01234-567',
            'telefone': '(11) 1234-5678',
            'email': 'contato@fornecedorteste.com',
            'inscricao_estadual': '123456789'
        }
        
        response = client.post(url_for('fornecedores.criar'), data=form_data, follow_redirects=True)
        
        # Verificar se o modelo foi chamado corretamente
        mock_model.assert_called_once()
        
        # Verificar se os dados foram salvos
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"cadastrado" in response.data.lower()

def test_criar_post_route_cnpj_existente(client):
    """Testa a rota POST para criar um fornecedor com CNPJ ju00e1 existente"""
    with patch('app.routes.fornecedores.views.Fornecedor') as mock_model:
        # Configurar mock para verificar se CNPJ ju00e1 existe
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = MagicMock()  # CNPJ ju00e1 existe
        mock_model.query = mock_query
        
        # Dados do formulu00e1rio
        form_data = {
            'cnpj': '12.345.678/0001-90',
            'razao_social': 'Fornecedor Teste LTDA'
        }
        
        response = client.post(url_for('fornecedores.criar'), data=form_data)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"CNPJ j\xc3\xa1 cadastrado" in response.data

def test_criar_post_route_dados_incompletos(client):
    """Testa a rota POST para criar um fornecedor com dados incompletos"""
    # Dados do formulu00e1rio incompletos
    form_data = {
        'cnpj': '',  # CNPJ vazio
        'razao_social': 'Fornecedor Teste LTDA'
    }
    
    response = client.post(url_for('fornecedores.criar'), data=form_data)
    
    # Verificar resposta
    assert response.status_code == 200
    assert b"obrigat\xc3\xb3rios" in response.data

def test_editar_get_route(client, mock_fornecedor):
    """Testa a rota GET para editar um fornecedor"""
    with patch('app.routes.fornecedores.views.Fornecedor.query') as mock_query:
        # Configurar mock para retornar o fornecedor
        mock_query.get_or_404.return_value = mock_fornecedor
        
        response = client.get(url_for('fornecedores.editar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Editar Fornecedor" in response.data
        assert bytes(mock_fornecedor.razao_social, 'utf-8') in response.data

def test_editar_post_route(client, mock_fornecedor):
    """Testa a rota POST para editar um fornecedor"""
    with patch('app.routes.fornecedores.views.Fornecedor.query') as mock_query, \
         patch('app.routes.fornecedores.views.db.session') as mock_session:
        
        # Configurar mock para retornar o fornecedor
        mock_query.get_or_404.return_value = mock_fornecedor
        
        # Dados do formulu00e1rio
        form_data = {
            'razao_social': 'Fornecedor Atualizado LTDA',
            'nome_fantasia': 'Fornecedor Atualizado',
            'endereco': 'Rua Nova, 456',
            'cidade': 'Nova Cidade',
            'estado': 'RJ',
            'cep': '98765-432',
            'telefone': '(21) 9876-5432',
            'email': 'novo@fornecedor.com',
            'inscricao_estadual': '987654321'
        }
        
        response = client.post(url_for('fornecedores.editar', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert mock_fornecedor.razao_social == 'Fornecedor Atualizado LTDA'
        assert mock_fornecedor.nome_fantasia == 'Fornecedor Atualizado'
        assert mock_fornecedor.endereco == 'Rua Nova, 456'
        
        # Verificar se as alterau00e7u00f5es foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_visualizar_route(client, mock_fornecedor):
    """Testa a rota para visualizar detalhes de um fornecedor"""
    with patch('app.routes.fornecedores.views.Fornecedor.query') as mock_query:
        # Configurar mock para retornar o fornecedor
        mock_query.get_or_404.return_value = mock_fornecedor
        
        response = client.get(url_for('fornecedores.visualizar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert bytes(mock_fornecedor.razao_social, 'utf-8') in response.data
        assert bytes(mock_fornecedor.cnpj, 'utf-8') in response.data
        assert bytes(mock_fornecedor.email, 'utf-8') in response.data

def test_deletar_route(client, mock_fornecedor):
    """Testa a rota para deletar um fornecedor"""
    with patch('app.routes.fornecedores.views.Fornecedor.query') as mock_query, \
         patch('app.routes.fornecedores.views.db.session') as mock_session:
        
        # Configurar mock para retornar o fornecedor
        mock_query.get_or_404.return_value = mock_fornecedor
        
        response = client.post(url_for('fornecedores.deletar', id=1), follow_redirects=True)
        
        # Verificar se o fornecedor foi deletado
        assert mock_session.delete.called
        assert mock_session.delete.call_args[0][0] == mock_fornecedor
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"removido" in response.data.lower()

def test_api_listar_route(client, mock_fornecedor):
    """Testa a API de listagem de fornecedores"""
    with patch('app.routes.fornecedores.views.Fornecedor') as mock_model:
        # Configurar mock para retornar fornecedores
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_fornecedor]
        mock_model.query = mock_query
        
        response = client.get(url_for('fornecedores.api_listar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_fornecedor.id
        assert response.json[0]["razao_social"] == mock_fornecedor.razao_social
        assert response.json[0]["cnpj"] == mock_fornecedor.cnpj

def test_api_buscar_route(client, mock_fornecedor):
    """Testa a API de busca de fornecedores"""
    with patch('app.routes.fornecedores.views.Fornecedor') as mock_model:
        # Configurar mock para retornar fornecedores
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_fornecedor]
        mock_model.query = mock_query
        
        response = client.get(url_for('fornecedores.api_buscar', termo='teste'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_fornecedor.id
        assert response.json[0]["razao_social"] == mock_fornecedor.razao_social
