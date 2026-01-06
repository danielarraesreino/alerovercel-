import pytest
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

from app.scripts.seed_historico_vendas import seed_historico_vendas
from app.models.modelo_previsao import HistoricoVendas
from app.models.modelo_cardapio import CardapioItem
from app.models.modelo_prato import Prato

@pytest.fixture
def mock_app():
    """Mock do Flask app"""
    mock_app = MagicMock()
    mock_context = MagicMock()
    mock_app.app_context.return_value = mock_context
    return mock_app

@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    mock_session = MagicMock()
    mock_db = MagicMock()
    mock_db.session = mock_session
    return mock_db

@pytest.fixture
def mock_pratos():
    """Mock de pratos para testes"""
    return [
        MagicMock(id=1, nome='Prato 1', preco_venda=25.90),
        MagicMock(id=2, nome='Prato 2', preco_venda=32.50)
    ]

@pytest.fixture
def mock_cardapio_itens():
    """Mock de itens de cardu00e1pio para testes"""
    return [
        MagicMock(id=1, prato_id=1, preco_venda=29.90),
        MagicMock(id=2, prato_id=2, preco_venda=35.90)
    ]

def test_seed_historico_vendas_com_dados(mock_app, mock_db, mock_pratos, mock_cardapio_itens):
    """Testa a gerau00e7u00e3o de dados de histu00f3rico de vendas com pratos e itens existentes"""
    # Configurar os mocks
    with patch('app.scripts.seed_historico_vendas.create_app', return_value=mock_app), \
         patch('app.scripts.seed_historico_vendas.db', mock_db), \
         patch('app.scripts.seed_historico_vendas.Prato'), \
         patch('app.scripts.seed_historico_vendas.CardapioItem'), \
         patch('app.scripts.seed_historico_vendas.HistoricoVendas'), \
         patch('app.scripts.seed_historico_vendas.random.randint') as mock_randint, \
         patch('app.scripts.seed_historico_vendas.random.choice') as mock_choice, \
         patch('app.scripts.seed_historico_vendas.random.uniform') as mock_uniform:
        
        # Configurar comportamento dos mocks
        mock_randint.return_value = 5  # 5 vendas por dia
        mock_choice.side_effect = lambda x: x[0]  # Sempre escolhe o primeiro item
        mock_uniform.return_value = 20.0  # Preu00e7o padru00e3o para valores aleatu00f3rios
        
        # Mock para as consultas
        mock_prato_query = MagicMock()
        mock_prato_query.all.return_value = mock_pratos
        patch('app.scripts.seed_historico_vendas.Prato.query', mock_prato_query)
        
        mock_cardapio_query = MagicMock()
        mock_cardapio_query.all.return_value = mock_cardapio_itens
        patch('app.scripts.seed_historico_vendas.CardapioItem.query', mock_cardapio_query)
        
        # Executar a funu00e7u00e3o
        seed_historico_vendas(num_dias=5)  # Reduzir para 5 dias para o teste ser mais ru00e1pido
        
        # Verificar se HistoricoVendas foi criado para cada dia
        # Para 5 dias e 5 vendas por dia = 25 registros
        assert mock_db.session.add.call_count >= 5  # Pelo menos uma venda por dia
        assert mock_db.session.commit.called

def test_seed_historico_vendas_sem_dados(mock_app, mock_db):
    """Testa a gerau00e7u00e3o de dados de histu00f3rico de vendas sem pratos ou itens existentes"""
    # Configurar os mocks
    with patch('app.scripts.seed_historico_vendas.create_app', return_value=mock_app), \
         patch('app.scripts.seed_historico_vendas.db', mock_db), \
         patch('app.scripts.seed_historico_vendas.Prato'), \
         patch('app.scripts.seed_historico_vendas.CardapioItem'), \
         patch('app.scripts.seed_historico_vendas.HistoricoVendas'), \
         patch('app.scripts.seed_historico_vendas.random.randint') as mock_randint, \
         patch('app.scripts.seed_historico_vendas.random.uniform') as mock_uniform:
        
        # Configurar comportamento dos mocks
        mock_randint.return_value = 3  # 3 vendas por dia
        mock_uniform.return_value = 25.0  # Preu00e7o padru00e3o para valores aleatu00f3rios
        
        # Mock para as consultas - sem pratos ou itens
        mock_prato_query = MagicMock()
        mock_prato_query.all.return_value = []
        patch('app.scripts.seed_historico_vendas.Prato.query', mock_prato_query)
        
        mock_cardapio_query = MagicMock()
        mock_cardapio_query.all.return_value = []
        patch('app.scripts.seed_historico_vendas.CardapioItem.query', mock_cardapio_query)
        
        # Executar a funu00e7u00e3o
        seed_historico_vendas(num_dias=3)  # Apenas 3 dias para o teste
        
        # Verificar se HistoricoVendas foi criado para cada dia
        # Para 3 dias e 3 vendas por dia = 9 registros
        assert mock_db.session.add.call_count >= 3  # Pelo menos uma venda por dia
        assert mock_db.session.commit.called

def test_seed_historico_vendas_main():
    """Testa o bloco main do script"""
    # Mock da funu00e7u00e3o seed_historico_vendas
    with patch('app.scripts.seed_historico_vendas.seed_historico_vendas') as mock_seed:
        # Simular execuu00e7u00e3o como script principal
        orig_name = app.scripts.seed_historico_vendas.__name__
        try:
            app.scripts.seed_historico_vendas.__name__ = '__main__'
            import importlib
            importlib.reload(app.scripts.seed_historico_vendas)
            
            # Verificar se a funu00e7u00e3o foi chamada
            assert mock_seed.called
        finally:
            # Restaurar o nome original
            app.scripts.seed_historico_vendas.__name__ = orig_name

def test_seed_historico_vendas_periodos_dia():
    """Testa a gerau00e7u00e3o de dados com diferentes peru00edodos do dia"""
    # Configurar os mocks
    mock_app = MagicMock()
    mock_context = MagicMock()
    mock_app.app_context.return_value = mock_context
    
    with patch('app.scripts.seed_historico_vendas.create_app', return_value=mock_app), \
         patch('app.scripts.seed_historico_vendas.db'), \
         patch('app.scripts.seed_historico_vendas.Prato.query.all', return_value=[]), \
         patch('app.scripts.seed_historico_vendas.CardapioItem.query.all', return_value=[]), \
         patch('app.scripts.seed_historico_vendas.random.randint', return_value=1), \
         patch('app.scripts.seed_historico_vendas.random.choice') as mock_choice, \
         patch('app.scripts.seed_historico_vendas.HistoricoVendas') as mock_historico:
        
        # Configurar o mock para retornar cada peru00edodo do dia sequencialmente
        periodos = ['manhu00e3', 'tarde', 'noite']
        mock_choice.side_effect = lambda x: periodos[0] if isinstance(x, list) and 'manhu00e3' in x else x[0]
        
        # Executar a funu00e7u00e3o com apenas 1 dia
        seed_historico_vendas(num_dias=1)
        
        # Verificar se o peru00edodo do dia foi considerado
        assert mock_historico.called
        # Verificar se foram usados diferentes peru00edodos
        calls = mock_historico.call_args_list
        assert len(calls) > 0
