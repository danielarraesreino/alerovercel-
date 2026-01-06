import pytest
from flask import url_for
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock

from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem
from app.extensions import db

@pytest.fixture
def mock_cardapio():
    cardapio = Cardapio(
        nome="Cardápio de Teste",
        descricao="Descrição do cardápio de teste",
        tipo="Almoço",
        temporada="Verão",
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=30),
        ativo=True
    )
    cardapio.id = 1
    return cardapio

@pytest.fixture
def mock_secao(mock_cardapio):
    secao = CardapioSecao(
        nome="Seção de Teste",
        descricao="Descrição da seção de teste",
        ordem=1,
        cardapio_id=mock_cardapio.id
    )
    secao.id = 1
    return secao

@pytest.fixture
def mock_item(mock_secao):
    item = CardapioItem(
        nome="Item de Teste",
        descricao="Descrição do item de teste",
        preco_venda=25.90,
        secao_id=mock_secao.id,
        ordem=1
    )
    item.id = 1
    return item

def test_index(client, mock_cardapio):
    """Testa a rota de listagem de cardápios"""
    with patch('app.routes.cardapios.views.Cardapio') as mock_model:
        # Configurar mock de paginação
        mock_pagination = MagicMock()
        mock_pagination.items = [mock_cardapio]
        mock_pagination.pages = 1
        mock_pagination.page = 1
        
        # Configurar mock da consulta
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_model.query = mock_query
        
        # Configurar mock de tipos e temporadas
        mock_session = MagicMock()
        mock_distinct_tipos = MagicMock()
        mock_distinct_tipos.all.return_value = [("Almoço",), ("Jantar",)]
        
        mock_distinct_temporadas = MagicMock()
        mock_distinct_temporadas.all.return_value = [("Verão",), ("Inverno",)]
        
        mock_session.query().distinct.side_effect = [mock_distinct_tipos, mock_distinct_temporadas]
        
        with patch('app.routes.cardapios.views.db.session', mock_session):
            response = client.get(url_for('cardapios.index'))
            
            assert response.status_code == 200
            assert b"Card\xc3\xa1pios" in response.data

def test_criar_get(client):
    """Testa a rota de criação de cardápio (GET)"""
    response = client.get(url_for('cardapios.criar'))
    
    assert response.status_code == 200
    assert b"Criar Novo Card\xc3\xa1pio" in response.data

def test_criar_post(client):
    """Testa a rota de criação de cardápio (POST)"""
    with patch('app.routes.cardapios.views.Cardapio') as mock_model, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        # Mock para a criação do modelo
        mock_model.return_value = MagicMock(id=1)
        
        # Dados do formulário
        form_data = {
            'nome': 'Novo Cardápio',
            'descricao': 'Descrição do novo cardápio',
            'tipo': 'Almoço',
            'temporada': 'Verão',
            'data_inicio': date.today().strftime('%Y-%m-%d'),
            'data_fim': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'ativo': 'true'
        }
        
        response = client.post(url_for('cardapios.criar'), data=form_data, follow_redirects=True)
        
        # Verificar chamadas aos mocks
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"criado" in response.data.lower()

def test_visualizar(client, mock_cardapio, mock_secao, mock_item):
    """Testa a rota de visualização de cardápio"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        # Configurar mock para retornar cardápio com seções e itens
        mock_cardapio.secoes = [mock_secao]
        mock_secao.itens = [mock_item]
        
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.visualizar', id=1))
        
        assert response.status_code == 200
        assert bytes(mock_cardapio.nome, 'utf-8') in response.data
        assert bytes(mock_secao.nome, 'utf-8') in response.data
        assert bytes(mock_item.nome, 'utf-8') in response.data

def test_adicionar_secao_get(client, mock_cardapio):
    """Testa a rota de adição de seção ao cardápio (GET)"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.adicionar_secao', id=1))
        
        assert response.status_code == 200
        assert b"Adicionar Se\xc3\xa7\xc3\xa3o" in response.data
        assert bytes(mock_cardapio.nome, 'utf-8') in response.data

def test_adicionar_secao_post(client, mock_cardapio):
    """Testa a rota de adição de seção ao cardápio (POST)"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query, \
         patch('app.routes.cardapios.views.CardapioSecao') as mock_secao_model, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        # Configurar mocks
        mock_query.get_or_404.return_value = mock_cardapio
        mock_secao_model.return_value = MagicMock(id=1)
        
        # Dados do formulário
        form_data = {
            'nome': 'Nova Seção',
            'descricao': 'Descrição da nova seção',
            'ordem': '1'
        }
        
        response = client.post(url_for('cardapios.adicionar_secao', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar chamadas aos mocks
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"adicionada" in response.data.lower()

def test_adicionar_item_get(client, mock_secao):
    """Testa a rota de adição de item à seção (GET)"""
    with patch('app.routes.cardapios.views.CardapioSecao.query') as mock_query, \
         patch('app.routes.cardapios.views.Prato.query') as mock_prato_query:
        
        # Configurar mocks
        mock_secao.cardapio = MagicMock(nome="Cardápio de Teste")
        mock_query.get_or_404.return_value = mock_secao
        
        # Mock para lista de pratos disponíveis
        mock_prato = MagicMock(id=1, nome="Prato de Teste")
        mock_prato_query.all.return_value = [mock_prato]
        
        response = client.get(url_for('cardapios.adicionar_item', secao_id=1))
        
        assert response.status_code == 200
        assert b"Adicionar Item" in response.data
        assert bytes(mock_secao.nome, 'utf-8') in response.data

def test_adicionar_item_post(client, mock_secao):
    """Testa a rota de adição de item à seção (POST)"""
    with patch('app.routes.cardapios.views.CardapioSecao.query') as mock_query, \
         patch('app.routes.cardapios.views.CardapioItem') as mock_item_model, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        # Configurar mocks
        mock_secao.cardapio = MagicMock(id=1)
        mock_query.get_or_404.return_value = mock_secao
        mock_item_model.return_value = MagicMock(id=1)
        
        # Dados do formulário
        form_data = {
            'nome': 'Novo Item',
            'descricao': 'Descrição do novo item',
            'preco_venda': '29.90',
            'ordem': '1',
            'tipo': 'manual'  # Item manual, não vinculado a um prato
        }
        
        response = client.post(url_for('cardapios.adicionar_item', secao_id=1), 
                             data=form_data, follow_redirects=True)
        
        # Verificar chamadas aos mocks
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"adicionado" in response.data.lower()

def test_exportar(client, mock_cardapio, mock_secao, mock_item):
    """Testa a rota de exportação de cardápio"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        # Configurar mock para retornar cardápio com seções e itens
        mock_cardapio.secoes = [mock_secao]
        mock_secao.itens = [mock_item]
        
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.exportar', id=1))
        
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert response.headers["Content-Disposition"].startswith("attachment; filename=")

def test_api_listar(client, mock_cardapio):
    """Testa a API de listagem de cardápios"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        # Configurar mock
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_cardapio]
        
        response = client.get(url_for('cardapios.api_listar'))
        
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_cardapio.id
        assert response.json[0]["nome"] == mock_cardapio.nome

def test_api_cardapio(client, mock_cardapio, mock_secao, mock_item):
    """Testa a API de detalhes de cardápio"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        # Configurar mock para retornar cardápio e seus relacionamentos
        mock_cardapio.secoes = [mock_secao]
        mock_secao.cardapio = mock_cardapio
        mock_secao.itens = [mock_item]
        mock_item.secao = mock_secao
        mock_item.prato = MagicMock(nome='Prato de Teste')
        
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.api_cardapio', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['nome'] == 'Cardápio de Teste'
        assert len(response.json['secoes']) == 1
        assert response.json['secoes'][0]['nome'] == 'Seção de Teste'
        assert len(response.json['secoes'][0]['itens']) == 1

def test_editar_get(client, mock_cardapio):
    """Testa a rota de edição de cardápio (GET)"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.editar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Editar Card\xc3\xa1pio' in response.data
        assert bytes(mock_cardapio.nome, 'utf-8') in response.data
        assert bytes(mock_cardapio.tipo, 'utf-8') in response.data

def test_editar_post(client, mock_cardapio):
    """Testa a rota de edição de cardápio (POST)"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        mock_query.get_or_404.return_value = mock_cardapio
        
        # Dados do formulário
        form_data = {
            'nome': 'Cardápio Atualizado',
            'descricao': 'Descrição atualizada',
            'tipo': 'Jantar',
            'temporada': 'Inverno',
            'data_inicio': date.today().strftime('%Y-%m-%d'),
            'data_fim': (date.today() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'ativo': 'true'
        }
        
        response = client.post(url_for('cardapios.editar', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert mock_cardapio.nome == 'Cardápio Atualizado'
        assert mock_cardapio.descricao == 'Descrição atualizada'
        assert mock_cardapio.tipo == 'Jantar'
        assert mock_cardapio.temporada == 'Inverno'
        
        # Verificar se as alterações foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower() or b'atualizado' in response.data.lower()

def test_editar_secao_get(client, mock_secao):
    """Testa a rota de edição de seção (GET)"""
    with patch('app.routes.cardapios.views.CardapioSecao.query') as mock_query:
        mock_query.get_or_404.return_value = mock_secao
        
        response = client.get(url_for('cardapios.editar_secao', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Editar Se\xc3\xa7\xc3\xa3o' in response.data
        assert bytes(mock_secao.nome, 'utf-8') in response.data

def test_editar_secao_post(client, mock_secao):
    """Testa a rota de edição de seção (POST)"""
    with patch('app.routes.cardapios.views.CardapioSecao.query') as mock_query, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        mock_query.get_or_404.return_value = mock_secao
        
        # Dados do formulário
        form_data = {
            'nome': 'Seção Atualizada',
            'descricao': 'Descrição atualizada da seção',
            'ordem': '2'
        }
        
        response = client.post(url_for('cardapios.editar_secao', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert mock_secao.nome == 'Seção Atualizada'
        assert mock_secao.descricao == 'Descrição atualizada da seção'
        assert mock_secao.ordem == 2
        
        # Verificar se as alterações foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower() or b'atualizada' in response.data.lower()

def test_remover_secao(client, mock_secao):
    """Testa a rota de remoção de seção"""
    with patch('app.routes.cardapios.views.CardapioSecao.query') as mock_query, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        mock_query.get_or_404.return_value = mock_secao
        
        response = client.post(url_for('cardapios.remover_secao', id=1), follow_redirects=True)
        
        # Verificar se a seção foi removida
        assert mock_session.delete.called
        assert mock_session.delete.call_args[0][0] == mock_secao
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower() or b'removida' in response.data.lower()

def test_editar_item_get(client, mock_item):
    """Testa a rota de edição de item (GET)"""
    with patch('app.routes.cardapios.views.CardapioItem.query') as mock_query:
        mock_query.get_or_404.return_value = mock_item
        
        response = client.get(url_for('cardapios.editar_item', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Editar Item' in response.data

def test_editar_item_post(client, mock_item):
    """Testa a rota de edição de item (POST)"""
    with patch('app.routes.cardapios.views.CardapioItem.query') as mock_query, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        mock_query.get_or_404.return_value = mock_item
        
        # Dados do formulário
        form_data = {
            'preco_venda': '29.90',
            'destaque': 'true',
            'disponivel': 'true',
            'ordem': '2',
            'observacao': 'Observação atualizada'
        }
        
        response = client.post(url_for('cardapios.editar_item', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert float(mock_item.preco_venda) == 29.90
        assert mock_item.destaque is True
        assert mock_item.disponivel is True
        assert mock_item.ordem == 2
        assert mock_item.observacao == 'Observação atualizada'
        
        # Verificar se as alterações foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower() or b'atualizado' in response.data.lower()

def test_remover_item(client, mock_item):
    """Testa a rota de remoção de item"""
    with patch('app.routes.cardapios.views.CardapioItem.query') as mock_query, \
         patch('app.routes.cardapios.views.db.session') as mock_session:
        
        mock_query.get_or_404.return_value = mock_item
        
        response = client.post(url_for('cardapios.remover_item', id=1), follow_redirects=True)
        
        # Verificar se o item foi removido
        assert mock_session.delete.called
        assert mock_session.delete.call_args[0][0] == mock_item
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'sucesso' in response.data.lower() or b'removido' in response.data.lower()

def test_imprimir(client, mock_cardapio, mock_secao, mock_item):
    """Testa a rota de impressão de cardápio"""
    with patch('app.routes.cardapios.views.Cardapio.query') as mock_query:
        # Configurar mock para retornar cardápio e seus relacionamentos
        mock_cardapio.secoes = [mock_secao]
        mock_secao.cardapio = mock_cardapio
        mock_secao.itens = [mock_item]
        mock_item.secao = mock_secao
        mock_item.prato = MagicMock(nome='Prato de Teste', descricao='Descrição do prato')
        
        mock_query.get_or_404.return_value = mock_cardapio
        
        response = client.get(url_for('cardapios.imprimir', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Imprimir Card\xc3\xa1pio' in response.data
        assert bytes(mock_cardapio.nome, 'utf-8') in response.data
        assert bytes(mock_secao.nome, 'utf-8') in response.data
        assert b'Prato de Teste' in response.data

def test_sugestao(client):
    """Testa a rota de sugestão de cardápio"""
    with patch('app.routes.cardapios.views.Prato') as mock_prato_model:
        # Configurar mock para retornar pratos sugeridos
        mock_prato1 = MagicMock(id=1, nome='Prato Sugerido 1', categoria='entrada')
        type(mock_prato1).margem_lucro = PropertyMock(return_value=70.0)
        type(mock_prato1).preco_venda = PropertyMock(return_value=25.90)
        
        mock_prato2 = MagicMock(id=2, nome='Prato Sugerido 2', categoria='principal')
        type(mock_prato2).margem_lucro = PropertyMock(return_value=65.0)
        type(mock_prato2).preco_venda = PropertyMock(return_value=45.90)
        
        # Configurar o retorno do query
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = [mock_prato1, mock_prato2]
        mock_prato_model.query = mock_query
        
        response = client.get(url_for('cardapios.sugestao'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Sugest\xc3\xa3o de Card\xc3\xa1pio' in response.data
        assert b'Prato Sugerido 1' in response.data
        assert b'Prato Sugerido 2' in response.data
        assert response.json["secoes"][0]["itens"][0]["nome"] == mock_item.nome
