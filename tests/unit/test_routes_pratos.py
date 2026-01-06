import pytest
from flask import url_for
from decimal import Decimal
from unittest.mock import patch, MagicMock, PropertyMock
import json

from app.models.modelo_prato import Prato, PratoInsumo
from app.models.modelo_produto import Produto

@pytest.fixture
def mock_prato():
    """Mock para um prato de teste"""
    prato = MagicMock(spec=Prato)
    prato.id = 1
    prato.nome = "Prato Teste"
    prato.descricao = "Descriu00e7u00e3o do prato teste"
    prato.categoria = "Principal"
    prato.tempo_preparo = 30
    prato.rendimento = 4
    prato.unidade_medida = "poru00e7u00e3o"
    prato.modo_preparo = "Instruu00e7u00f5es de preparo para teste"
    prato.observacoes = "Observau00e7u00f5es para teste"
    prato.preco_venda = Decimal('45.90')
    
    # Propriedades calculadas como PropertyMock
    type(prato).custo_total = PropertyMock(return_value=Decimal('30.00'))
    type(prato).custo_total_por_porcao = PropertyMock(return_value=Decimal('7.50'))
    type(prato).margem_lucro = PropertyMock(return_value=Decimal('53.0'))
    type(prato).preco_sugerido = PropertyMock(return_value=Decimal('48.75'))
    
    # Relacionamentos
    insumo1 = MagicMock(spec=PratoInsumo)
    insumo1.id = 1
    insumo1.produto_id = 1
    insumo1.produto = MagicMock(nome="Insumo 1", preco_unitario=Decimal('10.00'), unidade_medida="kg")
    insumo1.quantidade = 1.5
    insumo1.obrigatorio = True
    insumo1.observacao = "Observau00e7u00e3o insumo 1"
    
    insumo2 = MagicMock(spec=PratoInsumo)
    insumo2.id = 2
    insumo2.produto_id = 2
    insumo2.produto = MagicMock(nome="Insumo 2", preco_unitario=Decimal('15.00'), unidade_medida="kg")
    insumo2.quantidade = 1.0
    insumo2.obrigatorio = True
    insumo2.observacao = "Observau00e7u00e3o insumo 2"
    
    prato.insumos = [insumo1, insumo2]
    
    return prato

@pytest.fixture
def mock_produtos():
    """Mock para lista de produtos que podem ser insumos"""
    return [
        MagicMock(id=1, nome="Produto 1", preco_unitario=Decimal('10.00'), unidade_medida="kg"),
        MagicMock(id=2, nome="Produto 2", preco_unitario=Decimal('15.00'), unidade_medida="kg"),
        MagicMock(id=3, nome="Produto 3", preco_unitario=Decimal('8.50'), unidade_medida="kg")
    ]

def test_index_route(client):
    """Testa a rota de listagem de pratos"""
    with patch('app.routes.pratos.views.Prato') as mock_model:
        # Configurar mock para retornar pratos
        mock_prato1 = MagicMock(id=1, nome="Prato 1", categoria="Principal")
        type(mock_prato1).custo_total_por_porcao = PropertyMock(return_value=Decimal('7.50'))
        
        mock_prato2 = MagicMock(id=2, nome="Prato 2", categoria="Entrada")
        type(mock_prato2).custo_total_por_porcao = PropertyMock(return_value=Decimal('5.25'))
        
        # Mock para ordenar por nome
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = MagicMock(
            items=[mock_prato1, mock_prato2],
            page=1,
            per_page=20,
            total=2,
            pages=1
        )
        mock_model.query = mock_query
        
        # Mock para ordenar por custo
        mock_model.all.return_value = [mock_prato1, mock_prato2]
        
        # Testar ordenau00e7u00e3o por nome (padru00e3o)
        response = client.get(url_for('pratos.index'))
        assert response.status_code == 200
        assert b"Pratos" in response.data
        assert b"Prato 1" in response.data
        assert b"Prato 2" in response.data
        
        # Testar ordenau00e7u00e3o por custo
        response = client.get(url_for('pratos.index', ordenar_por='custo'))
        assert response.status_code == 200
        assert b"Pratos" in response.data
        assert b"Prato 1" in response.data
        assert b"Prato 2" in response.data
        
        # Testar filtro por categoria
        response = client.get(url_for('pratos.index', categoria='Principal'))
        assert response.status_code == 200
        assert b"Pratos" in response.data
        assert b"Principal" in response.data

def test_criar_get_route(client, mock_produtos):
    """Testa a rota GET para criar um prato"""
    with patch('app.routes.pratos.views.Produto') as mock_produto_model:
        # Configurar mock para lista de produtos
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_produtos
        mock_produto_model.query = mock_query
        
        response = client.get(url_for('pratos.criar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Cadastrar Novo Prato" in response.data
        assert b"Nome" in response.data
        assert b"Categoria" in response.data
        assert b"Tempo de Preparo" in response.data

def test_criar_post_route(client):
    """Testa a rota POST para criar um prato"""
    with patch('app.routes.pratos.views.Prato') as mock_model, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Mock para criau00e7u00e3o do prato
        mock_model.return_value = MagicMock(id=1)
        
        # Dados do formulu00e1rio
        form_data = {
            'nome': 'Novo Prato',
            'descricao': 'Descriu00e7u00e3o do novo prato',
            'categoria': 'Principal',
            'tempo_preparo': '30',
            'rendimento': '4',
            'unidade_medida': 'poru00e7u00e3o',
            'modo_preparo': 'Instruu00e7u00f5es de preparo',
            'observacoes': 'Observau00e7u00f5es gerais'
        }
        
        response = client.post(url_for('pratos.criar'), data=form_data, follow_redirects=True)
        
        # Verificar se o modelo foi chamado corretamente
        mock_model.assert_called_once()
        
        # Verificar se os dados foram salvos
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"cadastrado" in response.data.lower()

def test_editar_get_route(client, mock_prato):
    """Testa a rota GET para editar um prato"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query:
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.get(url_for('pratos.editar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Editar Prato" in response.data
        assert bytes(mock_prato.nome, 'utf-8') in response.data
        assert bytes(mock_prato.categoria, 'utf-8') in response.data

def test_editar_post_route(client, mock_prato):
    """Testa a rota POST para editar um prato"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        # Dados do formulu00e1rio
        form_data = {
            'nome': 'Prato Atualizado',
            'descricao': 'Descriu00e7u00e3o atualizada',
            'categoria': 'Sobremesa',
            'tempo_preparo': '25',
            'rendimento': '6',
            'unidade_medida': 'poru00e7u00e3o',
            'modo_preparo': 'Instruu00e7u00f5es atualizadas',
            'observacoes': 'Observau00e7u00f5es atualizadas'
        }
        
        response = client.post(url_for('pratos.editar', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert mock_prato.nome == 'Prato Atualizado'
        assert mock_prato.descricao == 'Descriu00e7u00e3o atualizada'
        assert mock_prato.categoria == 'Sobremesa'
        
        # Verificar se as alterau00e7u00f5es foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_visualizar_route(client, mock_prato):
    """Testa a rota para visualizar detalhes de um prato"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query:
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.get(url_for('pratos.visualizar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert bytes(mock_prato.nome, 'utf-8') in response.data
        assert bytes(mock_prato.categoria, 'utf-8') in response.data
        assert bytes(str(mock_prato.rendimento), 'utf-8') in response.data

def test_adicionar_insumo_get_route(client, mock_prato, mock_produtos):
    """Testa a rota GET para adicionar insumo a um prato"""
    with patch('app.routes.pratos.views.Prato.query') as mock_prato_query, \
         patch('app.routes.pratos.views.Produto.query') as mock_produto_query:
        
        # Configurar mocks
        mock_prato_query.get_or_404.return_value = mock_prato
        
        mock_produto_query_obj = MagicMock()
        mock_produto_query_obj.order_by.return_value = mock_produto_query_obj
        mock_produto_query_obj.all.return_value = mock_produtos
        mock_produto_query.return_value = mock_produto_query_obj
        
        response = client.get(url_for('pratos.adicionar_insumo', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Adicionar Insumo" in response.data
        assert bytes(mock_prato.nome, 'utf-8') in response.data
        assert b"Produto 1" in response.data
        assert b"Produto 2" in response.data

def test_adicionar_insumo_post_route(client, mock_prato, mock_produtos):
    """Testa a rota POST para adicionar insumo a um prato"""
    with patch('app.routes.pratos.views.Prato.query') as mock_prato_query, \
         patch('app.routes.pratos.views.Produto.query') as mock_produto_query, \
         patch('app.routes.pratos.views.PratoInsumo') as mock_insumo_model, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mocks
        mock_prato_query.get_or_404.return_value = mock_prato
        
        mock_produto_query_obj = MagicMock()
        mock_produto_query_obj.get.return_value = mock_produtos[2]  # Produto 3
        mock_produto_query.return_value = mock_produto_query_obj
        
        # Mock para criau00e7u00e3o do insumo
        mock_insumo_model.return_value = MagicMock(id=3)
        
        # Dados do formulu00e1rio
        form_data = {
            'produto_id': '3',
            'quantidade': '2.5',
            'obrigatorio': 'true',
            'observacao': 'Observau00e7u00e3o do novo insumo'
        }
        
        response = client.post(url_for('pratos.adicionar_insumo', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se o modelo foi chamado corretamente
        mock_insumo_model.assert_called_once()
        
        # Verificar se os dados foram salvos
        assert mock_session.add.called
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"adicionado" in response.data.lower()

def test_editar_insumo_get_route(client, mock_prato):
    """Testa a rota GET para editar um insumo"""
    insumo = mock_prato.insumos[0]
    
    with patch('app.routes.pratos.views.PratoInsumo.query') as mock_query:
        # Configurar mock para retornar o insumo
        mock_query.get_or_404.return_value = insumo
        
        response = client.get(url_for('pratos.editar_insumo', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Editar Insumo" in response.data
        assert bytes(insumo.produto.nome, 'utf-8') in response.data

def test_editar_insumo_post_route(client, mock_prato):
    """Testa a rota POST para editar um insumo"""
    insumo = mock_prato.insumos[0]
    
    with patch('app.routes.pratos.views.PratoInsumo.query') as mock_query, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o insumo
        mock_query.get_or_404.return_value = insumo
        
        # Dados do formulu00e1rio
        form_data = {
            'quantidade': '2.0',
            'obrigatorio': 'true',
            'observacao': 'Observau00e7u00e3o atualizada'
        }
        
        response = client.post(url_for('pratos.editar_insumo', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se os atributos foram atualizados
        assert insumo.quantidade == 2.0
        assert insumo.observacao == 'Observau00e7u00e3o atualizada'
        
        # Verificar se as alterau00e7u00f5es foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_remover_insumo_route(client, mock_prato):
    """Testa a rota para remover um insumo"""
    insumo = mock_prato.insumos[0]
    
    with patch('app.routes.pratos.views.PratoInsumo.query') as mock_query, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o insumo
        mock_query.get_or_404.return_value = insumo
        
        response = client.post(url_for('pratos.remover_insumo', id=1), follow_redirects=True)
        
        # Verificar se o insumo foi removido
        assert mock_session.delete.called
        assert mock_session.delete.call_args[0][0] == insumo
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"removido" in response.data.lower()

def test_atualizar_preco_route(client, mock_prato):
    """Testa a rota para atualizar o preu00e7o de venda com base no preu00e7o sugerido"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.post(url_for('pratos.atualizar_preco', id=1), follow_redirects=True)
        
        # Verificar se o preu00e7o foi atualizado para o preu00e7o sugerido
        assert mock_prato.preco_venda == mock_prato.preco_sugerido
        
        # Verificar se as alterau00e7u00f5es foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_definir_preco_route(client, mock_prato):
    """Testa a rota para definir manualmente o preu00e7o de venda"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query, \
         patch('app.routes.pratos.views.db.session') as mock_session:
        
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        # Dados do formulu00e1rio
        form_data = {
            'preco_venda': '50.00'
        }
        
        response = client.post(url_for('pratos.definir_preco', id=1), 
                              data=form_data, follow_redirects=True)
        
        # Verificar se o preu00e7o foi atualizado
        assert mock_prato.preco_venda == Decimal('50.00')
        
        # Verificar se as alterau00e7u00f5es foram salvas
        assert mock_session.commit.called
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"atualizado" in response.data.lower()

def test_ficha_tecnica_route(client, mock_prato):
    """Testa a rota para visualizar a ficha tu00e9cnica"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query:
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.get(url_for('pratos.ficha_tecnica', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Ficha T\xc3\xa9cnica" in response.data
        assert bytes(mock_prato.nome, 'utf-8') in response.data
        assert b"Insumo 1" in response.data
        assert b"Insumo 2" in response.data

def test_exportar_ficha_route(client, mock_prato):
    """Testa a rota para exportar a ficha tu00e9cnica para CSV"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query:
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.get(url_for('pratos.exportar_ficha', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert response.headers["Content-Disposition"].startswith("attachment; filename=")

def test_relatorio_custos_route(client):
    """Testa a rota para o relatu00f3rio de custos"""
    with patch('app.routes.pratos.views.Prato') as mock_model, \
         patch('app.routes.pratos.views.CustoIndireto') as mock_custo:
        
        # Mock para lista de pratos
        mock_prato1 = MagicMock(id=1, nome="Prato 1", categoria="Principal")
        type(mock_prato1).custo_total_por_porcao = PropertyMock(return_value=Decimal('7.50'))
        type(mock_prato1).preco_venda = PropertyMock(return_value=Decimal('30.00'))
        type(mock_prato1).margem_lucro = PropertyMock(return_value=Decimal('75.0'))
        
        mock_prato2 = MagicMock(id=2, nome="Prato 2", categoria="Entrada")
        type(mock_prato2).custo_total_por_porcao = PropertyMock(return_value=Decimal('5.25'))
        type(mock_prato2).preco_venda = PropertyMock(return_value=Decimal('20.00'))
        type(mock_prato2).margem_lucro = PropertyMock(return_value=Decimal('73.75'))
        
        # Configurar mock para retornar pratos
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_prato1, mock_prato2]
        mock_model.query = mock_query
        
        # Mock para custos indiretos
        mock_custo_query = MagicMock()
        mock_custo_query.filter.return_value = mock_custo_query
        mock_custo_query.all.return_value = [
            MagicMock(valor=Decimal('1000.00'), categoria="Aluguel"),
            MagicMock(valor=Decimal('500.00'), categoria="Energia")
        ]
        mock_custo.query = mock_custo_query
        
        response = client.get(url_for('pratos.relatorio_custos'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Relat\xc3\xb3rio de Custos" in response.data
        assert b"Prato 1" in response.data
        assert b"Prato 2" in response.data
        assert b"Custos Indiretos" in response.data

def test_api_listar_route(client, mock_prato):
    """Testa a API de listagem de pratos"""
    with patch('app.routes.pratos.views.Prato') as mock_model:
        # Configurar mock para retornar pratos
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_prato]
        mock_model.query = mock_query
        
        response = client.get(url_for('pratos.api_listar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json[0]["id"] == mock_prato.id
        assert response.json[0]["nome"] == mock_prato.nome
        assert response.json[0]["categoria"] == mock_prato.categoria

def test_api_ficha_tecnica_route(client, mock_prato):
    """Testa a API de ficha tu00e9cnica"""
    with patch('app.routes.pratos.views.Prato.query') as mock_query:
        # Configurar mock para retornar o prato
        mock_query.get_or_404.return_value = mock_prato
        
        response = client.get(url_for('pratos.api_ficha_tecnica', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert response.json["id"] == mock_prato.id
        assert response.json["nome"] == mock_prato.nome
        assert "insumos" in response.json
        assert len(response.json["insumos"]) == 2
        assert response.json["insumos"][0]["nome"] == "Insumo 1"
        assert response.json["insumos"][1]["nome"] == "Insumo 2"
