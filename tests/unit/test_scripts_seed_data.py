import pytest
from unittest.mock import patch, MagicMock, call
import random

from app.scripts.seed_data import (
    seed_database,
    crear_fornecedores,
    crear_produtos,
    crear_notas_fiscais,
    crear_movimentacoes,
    crear_custos_indiretos,
    crear_pratos,
    crear_cardapios
)

@pytest.fixture
def mock_app():
    with patch('app.scripts.seed_data.create_app') as mock_create_app:
        mock_app = MagicMock()
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context
        mock_create_app.return_value = mock_app
        yield mock_app

@pytest.fixture
def mock_db_session():
    with patch('app.scripts.seed_data.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_random():
    with patch('app.scripts.seed_data.random') as mock_random:
        mock_random.choice.side_effect = lambda x: x[0] if x else None
        mock_random.randint.side_effect = lambda a, b: a
        mock_random.uniform.return_value = 10.0
        mock_random.sample.side_effect = lambda pop, k: pop[:k] if len(pop) >= k else pop
        yield mock_random

@pytest.fixture
def mock_faker():
    with patch('app.scripts.seed_data.fake') as mock_faker:
        mock_faker.company.return_value = "Empresa Teste"
        mock_faker.company_suffix.return_value = "Ltda"
        mock_faker.name.return_value = "Nome Teste"
        mock_faker.email.return_value = "teste@email.com"
        mock_faker.phone_number.return_value = "(11) 99999-9999"
        mock_faker.address.return_value = "Endereu00e7o Teste"
        mock_faker.city.return_value = "Cidade Teste"
        mock_faker.state.return_value = "Estado Teste"
        mock_faker.state_abbr.return_value = "ET"
        mock_faker.postcode.return_value = "00000-000"
        mock_faker.cnpj.return_value = "00.000.000/0001-00"
        mock_faker.sentence.return_value = "Descriu00e7u00e3o de teste."
        mock_faker.paragraph.return_value = "Paru00e1grafo de teste."
        mock_faker.date_between.return_value = datetime.now().date()
        yield mock_faker

@pytest.fixture
def mock_models():
    with patch('app.scripts.seed_data.Fornecedor') as mock_fornecedor, \
         patch('app.scripts.seed_data.Produto') as mock_produto, \
         patch('app.scripts.seed_data.NFe') as mock_nfe, \
         patch('app.scripts.seed_data.NFItem') as mock_nf_item, \
         patch('app.scripts.seed_data.EstoqueMovimentacao') as mock_estoque, \
         patch('app.scripts.seed_data.CustoCategoria') as mock_custo_categoria, \
         patch('app.scripts.seed_data.CustoOperacional') as mock_custo, \
         patch('app.scripts.seed_data.Prato') as mock_prato, \
         patch('app.scripts.seed_data.PratoInsumo') as mock_prato_insumo, \
         patch('app.scripts.seed_data.Cardapio') as mock_cardapio, \
         patch('app.scripts.seed_data.CardapioSecao') as mock_secao, \
         patch('app.scripts.seed_data.CardapioItem') as mock_item:
        
        # Configurar os mocks para retornar instu00e2ncias com IDs
        mock_fornecedor.return_value = MagicMock(id=1)
        mock_produto.return_value = MagicMock(id=1)
        mock_nfe.return_value = MagicMock(id=1)
        mock_nf_item.return_value = MagicMock(id=1)
        mock_estoque.return_value = MagicMock(id=1)
        mock_custo_categoria.return_value = MagicMock(id=1)
        mock_custo.return_value = MagicMock(id=1)
        mock_prato.return_value = MagicMock(id=1)
        mock_prato_insumo.return_value = MagicMock(id=1)
        mock_cardapio.return_value = MagicMock(id=1)
        mock_secao.return_value = MagicMock(id=1)
        mock_item.return_value = MagicMock(id=1)
        
        yield {
            'fornecedor': mock_fornecedor,
            'produto': mock_produto,
            'nfe': mock_nfe,
            'nf_item': mock_nf_item,
            'estoque': mock_estoque,
            'custo_categoria': mock_custo_categoria,
            'custo': mock_custo,
            'prato': mock_prato,
            'prato_insumo': mock_prato_insumo,
            'cardapio': mock_cardapio,
            'secao': mock_secao,
            'item': mock_item
        }

def test_seed_database(mock_app, mock_db_session, mock_models):
    """Testa a funu00e7u00e3o principal que popula todo o banco de dados"""
    # Patch para todas as funu00e7u00f5es de criau00e7u00e3o
    with patch('app.scripts.seed_data.crear_fornecedores') as mock_crear_fornecedores, \
         patch('app.scripts.seed_data.crear_produtos') as mock_crear_produtos, \
         patch('app.scripts.seed_data.crear_notas_fiscais') as mock_crear_notas, \
         patch('app.scripts.seed_data.crear_movimentacoes') as mock_crear_movimentacoes, \
         patch('app.scripts.seed_data.crear_custos_indiretos') as mock_crear_custos, \
         patch('app.scripts.seed_data.crear_pratos') as mock_crear_pratos, \
         patch('app.scripts.seed_data.crear_cardapios') as mock_crear_cardapios:
        
        # Configurar os mocks para retornar listas
        fornecedores = [MagicMock() for _ in range(5)]
        produtos = [MagicMock() for _ in range(20)]
        notas = [MagicMock() for _ in range(10)]
        movimentacoes = [MagicMock() for _ in range(30)]
        custos = [MagicMock() for _ in range(3)]
        pratos = [MagicMock() for _ in range(8)]
        cardapios = [MagicMock() for _ in range(2)]
        
        mock_crear_fornecedores.return_value = fornecedores
        mock_crear_produtos.return_value = produtos
        mock_crear_notas.return_value = notas
        mock_crear_movimentacoes.return_value = movimentacoes
        mock_crear_custos.return_value = custos
        mock_crear_pratos.return_value = pratos
        mock_crear_cardapios.return_value = cardapios
        
        # Executar a funu00e7u00e3o
        resultado = seed_database()
        
        # Verificar se todas as funu00e7u00f5es foram chamadas
        mock_crear_fornecedores.assert_called_once_with(5)
        mock_crear_produtos.assert_called_once_with(20, fornecedores)
        mock_crear_notas.assert_called_once_with(10, fornecedores, produtos)
        mock_crear_movimentacoes.assert_called_once_with(30, produtos)
        mock_crear_custos.assert_called_once_with(3)
        mock_crear_pratos.assert_called_once_with(8, produtos)
        mock_crear_cardapios.assert_called_once_with(2, pratos)
        
        # Verificar o resultado
        assert resultado["fornecedores"] == 5
        assert resultado["produtos"] == 20
        assert resultado["notas"] == 10
        assert resultado["movimentacoes"] == 30
        assert resultado["custos"] == 3
        assert resultado["pratos"] == 8
        assert resultado["cardapios"] == 2

def test_crear_fornecedores(mock_db_session, mock_models, mock_faker):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de fornecedores"""
    fornecedores = crear_fornecedores(3)
    
    # Verificar se foram criados 3 fornecedores
    assert len(fornecedores) == 3
    
    # Verificar se o modelo Fornecedor foi chamado 3 vezes
    assert mock_models["fornecedor"].call_count == 3
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count >= 3
    assert mock_db_session.commit.called

def test_crear_produtos(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de produtos"""
    # Criar mock de fornecedores
    fornecedores = [MagicMock(id=i) for i in range(1, 4)]
    
    produtos = crear_produtos(5, fornecedores)
    
    # Verificar se foram criados 5 produtos
    assert len(produtos) == 5
    
    # Verificar se o modelo Produto foi chamado 5 vezes
    assert mock_models["produto"].call_count == 5
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count >= 5
    assert mock_db_session.commit.called

def test_crear_notas_fiscais(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de notas fiscais"""
    # Criar mocks
    fornecedores = [MagicMock(id=i, razao_social=f"Fornecedor {i}") for i in range(1, 4)]
    produtos = [MagicMock(id=i, nome=f"Produto {i}") for i in range(1, 6)]
    
    notas = crear_notas_fiscais(2, fornecedores, produtos)
    
    # Verificar se foram criadas 2 notas
    assert len(notas) == 2
    
    # Verificar se o modelo NFe foi chamado 2 vezes
    assert mock_models["nfe"].call_count == 2
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count >= 2
    assert mock_db_session.commit.called
    
    # Verificar se foram criados itens para as notas
    assert mock_models["nf_item"].call_count > 0

def test_crear_movimentacoes(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de movimentau00e7u00f5es de estoque"""
    # Criar mocks
    produtos = [MagicMock(id=i, nome=f"Produto {i}") for i in range(1, 6)]
    
    movimentacoes = crear_movimentacoes(4, produtos)
    
    # Verificar se foram criadas 4 movimentau00e7u00f5es
    assert len(movimentacoes) == 4
    
    # Verificar se o modelo EstoqueMovimentacao foi chamado 4 vezes
    assert mock_models["estoque"].call_count == 4
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count >= 4
    assert mock_db_session.commit.called

def test_crear_custos_indiretos(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de custos indiretos"""
    custos = crear_custos_indiretos(2)
    
    # Verificar se foram criados custos para 2 meses
    assert len(custos) > 0
    
    # Verificar se foram criadas categorias de custo
    assert mock_models["custo_categoria"].call_count > 0
    
    # Verificar se foram criados registros de custo
    assert mock_models["custo"].call_count > 0
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count > 0
    assert mock_db_session.commit.called

def test_crear_pratos(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de pratos"""
    # Criar mocks
    produtos = [MagicMock(id=i, nome=f"Produto {i}") for i in range(1, 6)]
    
    pratos = crear_pratos(3, produtos)
    
    # Verificar se foram criados 3 pratos
    assert len(pratos) == 3
    
    # Verificar se o modelo Prato foi chamado 3 vezes
    assert mock_models["prato"].call_count == 3
    
    # Verificar se foram criados insumos para os pratos
    assert mock_models["prato_insumo"].call_count > 0
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count > 0
    assert mock_db_session.commit.called

def test_crear_cardapios(mock_db_session, mock_models, mock_faker, mock_random):
    """Testa a funu00e7u00e3o de criau00e7u00e3o de cardu00e1pios"""
    # Criar mocks
    pratos = [MagicMock(id=i, nome=f"Prato {i}") for i in range(1, 6)]
    
    cardapios = crear_cardapios(2, pratos)
    
    # Verificar se foram criados 2 cardu00e1pios
    assert len(cardapios) == 2
    
    # Verificar se o modelo Cardapio foi chamado 2 vezes
    assert mock_models["cardapio"].call_count == 2
    
    # Verificar se foram criadas seu00e7u00f5es para os cardu00e1pios
    assert mock_models["secao"].call_count > 0
    
    # Verificar se foram criados itens para as seu00e7u00f5es
    assert mock_models["item"].call_count > 0
    
    # Verificar se foram adicionados ao banco
    assert mock_db_session.add.call_count > 0
    assert mock_db_session.commit.called

def test_main_execution():
    """Testa a execuu00e7u00e3o principal do script"""
    with patch('app.scripts.seed_data.seed_database') as mock_seed:
        mock_seed.return_value = {
            "fornecedores": 5,
            "produtos": 20,
            "notas": 10,
            "movimentacoes": 30,
            "custos": 3,
            "pratos": 8,
            "cardapios": 2
        }
        
        # Simular execuu00e7u00e3o como script principal
        from app.scripts.seed_data import __name__ as module_name
        original_name = module_name
        try:
            import sys
            sys.modules['app.scripts.seed_data'].__name__ = '__main__'
            # Reimportar para executar o bloco if __name__ == '__main__'
            import importlib
            importlib.reload(sys.modules['app.scripts.seed_data'])
            
            # Verificar se seed_database foi chamado
            mock_seed.assert_called_once()
        finally:
            # Restaurar o nome original
            sys.modules['app.scripts.seed_data'].__name__ = original_name
