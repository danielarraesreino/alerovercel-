import pytest
from flask import url_for
from unittest.mock import patch, MagicMock
from datetime import datetime
import json
import io
from decimal import Decimal

from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_fornecedor import Fornecedor
from app.models.modelo_produto import Produto

@pytest.fixture
def mock_fornecedor():
    """Mock para um fornecedor"""
    fornecedor = MagicMock(spec=Fornecedor)
    fornecedor.id = 1
    fornecedor.razao_social = "Fornecedor Teste"
    fornecedor.cnpj = "12345678901234"
    fornecedor.inscricao_estadual = "123456789"
    fornecedor.cidade = "São Paulo"
    fornecedor.estado = "SP"
    return fornecedor

@pytest.fixture
def mock_produto():
    """Mock para um produto"""
    produto = MagicMock(spec=Produto)
    produto.id = 1
    produto.nome = "Produto Teste"
    produto.unidade_medida = "kg"
    produto.estoque_atual = 10.0
    produto.preco_unitario = Decimal('15.00')
    return produto

@pytest.fixture
def mock_nf_notas(mock_fornecedor):
    """Mock para uma lista de notas fiscais"""
    # Nota 1
    nota1 = MagicMock(spec=NFNota)
    nota1.id = 1
    nota1.chave_acesso = "12345678901234567890123456789012345678901234"
    nota1.numero = "12345"
    nota1.serie = "1"
    nota1.data_emissao = datetime(2023, 5, 15)
    nota1.data_importacao = datetime(2023, 5, 16)
    nota1.valor_total = Decimal('1000.00')
    nota1.valor_produtos = Decimal('900.00')
    nota1.valor_frete = Decimal('50.00')
    nota1.valor_seguro = Decimal('10.00')
    nota1.valor_desconto = Decimal('20.00')
    nota1.valor_impostos = Decimal('80.00')
    nota1.fornecedor_id = mock_fornecedor.id
    nota1.fornecedor = mock_fornecedor
    nota1.xml_data = "<xml>Teste</xml>"
    nota1.get_data_formatada.return_value = "15/05/2023"
    nota1.valor_liquido = 980.0
    nota1.itens = []
    
    # Nota 2
    nota2 = MagicMock(spec=NFNota)
    nota2.id = 2
    nota2.chave_acesso = "98765432109876543210987654321098765432109876"
    nota2.numero = "54321"
    nota2.serie = "2"
    nota2.data_emissao = datetime(2023, 6, 20)
    nota2.data_importacao = datetime(2023, 6, 21)
    nota2.valor_total = Decimal('500.00')
    nota2.valor_produtos = Decimal('450.00')
    nota2.valor_frete = Decimal('30.00')
    nota2.valor_seguro = Decimal('5.00')
    nota2.valor_desconto = Decimal('10.00')
    nota2.valor_impostos = Decimal('40.00')
    nota2.fornecedor_id = mock_fornecedor.id
    nota2.fornecedor = mock_fornecedor
    nota2.xml_data = "<xml>Teste2</xml>"
    nota2.get_data_formatada.return_value = "20/06/2023"
    nota2.valor_liquido = 490.0
    nota2.itens = []
    
    return [nota1, nota2]

@pytest.fixture
def mock_nf_itens(mock_nf_notas, mock_produto):
    """Mock para uma lista de itens de nota fiscal"""
    # Item 1
    item1 = MagicMock(spec=NFItem)
    item1.id = 1
    item1.nf_nota_id = mock_nf_notas[0].id
    item1.produto_id = mock_produto.id
    item1.num_item = 1
    item1.quantidade = 2.5
    item1.valor_unitario = Decimal('100.00')
    item1.valor_total = Decimal('250.00')
    item1.unidade_medida = "kg"
    item1.cfop = "5102"
    item1.ncm = "12345678"
    item1.percentual_icms = Decimal('18.00')
    item1.valor_icms = Decimal('45.00')
    item1.percentual_ipi = Decimal('5.00')
    item1.valor_ipi = Decimal('12.50')
    item1.nota = mock_nf_notas[0]
    item1.produto = mock_produto
    item1.valor_com_impostos = 262.5
    
    # Item 2
    item2 = MagicMock(spec=NFItem)
    item2.id = 2
    item2.nf_nota_id = mock_nf_notas[0].id
    item2.produto_id = mock_produto.id
    item2.num_item = 2
    item2.quantidade = 5.0
    item2.valor_unitario = Decimal('130.00')
    item2.valor_total = Decimal('650.00')
    item2.unidade_medida = "kg"
    item2.cfop = "5102"
    item2.ncm = "12345678"
    item2.percentual_icms = Decimal('18.00')
    item2.valor_icms = Decimal('117.00')
    item2.percentual_ipi = Decimal('5.00')
    item2.valor_ipi = Decimal('32.50')
    item2.nota = mock_nf_notas[0]
    item2.produto = mock_produto
    item2.valor_com_impostos = 682.5
    
    # Adicionar itens à nota
    mock_nf_notas[0].itens = [item1, item2]
    
    return [item1, item2]

def test_index_route(client, mock_nf_notas):
    """Testa a rota de listagem de notas fiscais"""
    with patch('app.routes.nfe.views.NFNota') as mock_model:
        # Configurar mock para paginação
        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = MagicMock(
            items=mock_nf_notas,
            page=1,
            per_page=20,
            total=2,
            pages=1
        )
        mock_model.query = mock_query
        
        response = client.get(url_for('nfe.index'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Notas Fiscais" in response.data
        assert b"12345" in response.data
        assert b"54321" in response.data
        assert b"Fornecedor Teste" in response.data

def test_importar_get_route(client, mock_fornecedor):
    """Testa a rota GET para importar nota fiscal"""
    with patch('app.routes.nfe.views.Fornecedor') as mock_model:
        # Configurar mock para a lista de fornecedores
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_fornecedor]
        mock_model.query = mock_query
        
        response = client.get(url_for('nfe.importar'))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Importar Nota Fiscal" in response.data
        assert b"Fornecedor Teste" in response.data
        assert b"XML da NFe" in response.data

def test_importar_post_route(client, mock_fornecedor):
    """Testa a rota POST para importar nota fiscal"""
    with patch('app.routes.nfe.views.Fornecedor') as mock_fornecedor_model, \
         patch('app.routes.nfe.views.processar_xml_nfe') as mock_processar, \
         patch('app.routes.nfe.views.importar_nfe') as mock_importar:
        
        # Configurar mocks
        mock_fornecedor_query = MagicMock()
        mock_fornecedor_query.all.return_value = [mock_fornecedor]
        mock_fornecedor_model.query = mock_fornecedor_query
        
        # Mock para processamento de XML
        mock_nfe_data = {
            'chave_acesso': '12345678901234567890123456789012345678901234',
            'numero': '12345',
            'serie': '1',
            'data_emissao': datetime(2023, 5, 15),
            'valor_produtos': 900.0,
            'valor_total': 1000.0,
            'valor_frete': 50.0,
            'valor_seguro': 10.0,
            'valor_desconto': 20.0,
            'valor_impostos': 80.0,
            'fornecedor': {
                'cnpj': '12345678901234',
                'razao_social': 'Fornecedor Teste',
                'inscricao_estadual': '123456789'
            },
            'itens': [
                {
                    'num_item': 1,
                    'codigo': 'PROD001',
                    'descricao': 'Produto Teste',
                    'ncm': '12345678',
                    'cfop': '5102',
                    'unidade': 'kg',
                    'quantidade': 2.5,
                    'valor_unitario': 100.0,
                    'valor_total': 250.0,
                    'icms_aliquota': 18.0,
                    'icms_valor': 45.0,
                    'ipi_aliquota': 5.0,
                    'ipi_valor': 12.5
                }
            ]
        }
        mock_processar.return_value = mock_nfe_data
        
        # Mock para importação de NF
        mock_importar.return_value = MagicMock(id=1)
        
        # Dados do formulário
        xml_content = b"<nfeProc xmlns='http://www.portalfiscal.inf.br/nfe' versao='4.00'><NFe>...</NFe></nfeProc>"
        data = {
            'fornecedor_id': '1',
            'xml_file': (io.BytesIO(xml_content), 'nfe.xml')
        }
        
        response = client.post(url_for('nfe.importar'),
                              data=data,
                              content_type='multipart/form-data',
                              follow_redirects=True)
        
        # Verificar se os métodos foram chamados corretamente
        mock_processar.assert_called_once()
        mock_importar.assert_called_once()
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"sucesso" in response.data.lower() or b"importada" in response.data.lower()

def test_visualizar_route(client, mock_nf_notas, mock_nf_itens):
    """Testa a rota para visualizar detalhes de uma nota fiscal"""
    with patch('app.routes.nfe.views.NFNota.query') as mock_query:
        # Configurar mock para retornar a nota
        mock_query.get_or_404.return_value = mock_nf_notas[0]
        
        response = client.get(url_for('nfe.visualizar', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Detalhes da Nota Fiscal" in response.data
        assert b"12345" in response.data
        assert b"Fornecedor Teste" in response.data
        assert b"Produto Teste" in response.data

def test_visualizar_item_route(client, mock_nf_itens):
    """Testa a rota para visualizar detalhes de um item de nota fiscal"""
    with patch('app.routes.nfe.views.NFItem.query') as mock_query:
        # Configurar mock para retornar o item
        mock_query.get_or_404.return_value = mock_nf_itens[0]
        
        response = client.get(url_for('nfe.visualizar_item', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        assert b"Detalhes do Item" in response.data
        assert b"Produto Teste" in response.data
        assert b"kg" in response.data
        assert b"2.5" in response.data

def test_api_listar_notas_route(client, mock_nf_notas):
    """Testa a API para listar notas fiscais"""
    with patch('app.routes.nfe.views.NFNota') as mock_model:
        # Configurar mock para retornar notas
        mock_query = MagicMock()
        mock_query.all.return_value = mock_nf_notas
        mock_model.query = mock_query
        
        response = client.get(url_for('nfe.api_listar_notas'))
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json
        assert len(data) == 2
        assert data[0]["numero"] == "12345"
        assert data[1]["numero"] == "54321"

def test_api_detalhes_nota_route(client, mock_nf_notas, mock_nf_itens):
    """Testa a API para obter detalhes de uma nota fiscal"""
    with patch('app.routes.nfe.views.NFNota.query') as mock_query:
        # Configurar mock para retornar a nota
        mock_query.get_or_404.return_value = mock_nf_notas[0]
        
        response = client.get(url_for('nfe.api_detalhes_nota', id=1))
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json
        assert data["nota"]["numero"] == "12345"
        assert data["nota"]["serie"] == "1"
        assert data["nota"]["fornecedor"] == "Fornecedor Teste"
        assert len(data["itens"]) == 2
        assert data["itens"][0]["num_item"] == 1
        assert data["itens"][1]["num_item"] == 2
