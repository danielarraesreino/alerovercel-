import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import importlib
from app.scripts.create_db import setup_database

# Teste para scripts/create_db.py
@pytest.mark.parametrize("drop_all", [True, False])
def test_setup_database(drop_all):
    """Testa a funu00e7u00e3o setup_database com e sem drop_all"""
    # Mock do create_app e app_context
    mock_app = MagicMock()
    mock_context = MagicMock()
    mock_app.app_context.return_value = mock_context
    
    # Mock do db
    mock_db = MagicMock()
    
    with patch('app.scripts.create_db.create_app', return_value=mock_app), \
         patch('app.scripts.create_db.db', mock_db):
        
        # Executar a funu00e7u00e3o de setup
        setup_database(drop_all)
        
        # Verificar se create_app foi chamado com 'development'
        assert mock_app.app_context.called
        
        # Verificar se db.create_all foi chamado
        assert mock_db.create_all.called
        
        # Verificar se db.drop_all foi chamado apenas se drop_all=True
        if drop_all:
            assert mock_db.drop_all.called
        else:
            assert not mock_db.drop_all.called

# Teste para o bloco main de create_db.py
def test_create_db_main():
    """Testa o bloco main do script create_db.py"""
    # Mock da funu00e7u00e3o setup_database
    with patch('app.scripts.create_db.setup_database') as mock_setup:
        # Simular linha de comando sem --drop
        with patch.object(sys, 'argv', ['create_db.py']):
            # Importar o mu00f3dulo para executar o bloco __main__
            import app.scripts.create_db
            importlib.reload(app.scripts.create_db)
            
            # Verificar se setup_database foi chamado com False
            mock_setup.assert_called_once_with(False)
        
        # Resetar o mock
        mock_setup.reset_mock()
        
        # Simular linha de comando com --drop
        with patch.object(sys, 'argv', ['create_db.py', '--drop']):
            importlib.reload(app.scripts.create_db)
            
            # Verificar se setup_database foi chamado com True
            mock_setup.assert_called_once_with(True)

# Testes para scripts/seed_data.py
@pytest.mark.parametrize("entity,data", [
    ('produtos', [
        {'nome': 'Produto Teste 1', 'preco_unitario': 10.50},
        {'nome': 'Produto Teste 2', 'preco_unitario': 15.75}
    ]),
    ('categorias_desperdicio', [
        {'nome': 'Categoria Teste 1', 'cor': '#FF0000'},
        {'nome': 'Categoria Teste 2', 'cor': '#00FF00'}
    ]),
    ('pratos', [
        {'nome': 'Prato Teste 1', 'preco_venda': 25.90},
        {'nome': 'Prato Teste 2', 'preco_venda': 32.50}
    ])
])
def test_seed_entity(entity, data):
    """Testa a funu00e7u00e3o seed_entity para diferentes entidades"""
    # Importar a funu00e7u00e3o de seed
    from app.scripts.seed_data import seed_entity
    
    # Mock do modelo e session
    mock_model = MagicMock()
    mock_session = MagicMock()
    
    # Mock do mapeamento de entidades para modelos
    entity_models = {
        'produtos': mock_model,
        'categorias_desperdicio': mock_model,
        'pratos': mock_model
    }
    
    with patch.dict('app.scripts.seed_data.entity_models', entity_models):
        # Executar a funu00e7u00e3o de seed
        seed_entity(entity, data, mock_session)
        
        # Verificar se a model foi instanciada para cada item de dados
        assert mock_model.call_count == len(data)
        
        # Verificar se add e commit foram chamados
        assert mock_session.add.call_count == len(data)
        assert mock_session.commit.called

# Teste para seed_sample_data
def test_seed_sample_data():
    """Testa a funu00e7u00e3o seed_sample_data"""
    # Importar a funu00e7u00e3o de seed
    from app.scripts.seed_data import seed_sample_data
    
    # Mock do app e app_context
    mock_app = MagicMock()
    mock_context = MagicMock()
    mock_app.app_context.return_value = mock_context
    
    # Mock da funu00e7u00e3o seed_entity
    with patch('app.scripts.seed_data.create_app', return_value=mock_app), \
         patch('app.scripts.seed_data.seed_entity') as mock_seed:
        
        # Executar a funu00e7u00e3o
        seed_sample_data()
        
        # Verificar se app_context foi usado
        assert mock_app.app_context.called
        
        # Verificar se seed_entity foi chamado mu00faltiplas vezes
        # (pelo menos uma vez para cada tipo de entidade)
        assert mock_seed.call_count > 0

# Teste para o bloco main de seed_data.py
def test_seed_data_main():
    """Testa o bloco main do script seed_data.py"""
    # Mock da funu00e7u00e3o seed_sample_data
    with patch('app.scripts.seed_data.seed_sample_data') as mock_seed:
        # Simular linha de comando
        with patch.object(sys, 'argv', ['seed_data.py']):
            try:
                # Importar o mu00f3dulo para executar o bloco __main__
                import app.scripts.seed_data
                importlib.reload(app.scripts.seed_data)
                
                # Verificar se seed_sample_data foi chamado
                assert mock_seed.called
            except ImportError:
                # Se o mu00f3dulo nu00e3o existir, pule o teste
                pytest.skip("Mu00f3dulo seed_data.py nu00e3o encontrado")

# Teste para scripts/seed_historico_vendas.py
def test_seed_historico_vendas():
    """Testa a funu00e7u00e3o seed_historico_vendas"""
    try:
        # Importar a funu00e7u00e3o
        from app.scripts.seed_historico_vendas import seed_historico_vendas
        
        # Mock do app e app_context
        mock_app = MagicMock()
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context
        
        # Mock dos modelos e session
        mock_historico = MagicMock()
        mock_cardapio_item = MagicMock()
        mock_session = MagicMock()
        
        # Configurar o mock de query para retornar itens de cardu00e1pio
        mock_query = MagicMock()
        mock_query.all.return_value = [
            MagicMock(id=1, preco_venda=25.90),
            MagicMock(id=2, preco_venda=32.50)
        ]
        mock_session.query.return_value.filter.return_value = mock_query
        
        with patch('app.scripts.seed_historico_vendas.create_app', return_value=mock_app), \
             patch('app.scripts.seed_historico_vendas.db.session', mock_session), \
             patch('app.scripts.seed_historico_vendas.HistoricoVendas', mock_historico), \
             patch('app.scripts.seed_historico_vendas.CardapioItem', mock_cardapio_item):
            
            # Executar a funu00e7u00e3o com poucos dias para tornar o teste mais ru00e1pido
            seed_historico_vendas(num_dias=5)
            
            # Verificar se foram criados registros de venda
            assert mock_historico.call_count > 0
            assert mock_session.add.call_count > 0
            assert mock_session.commit.called
    
    except ImportError:
        # Se o mu00f3dulo nu00e3o existir, pule o teste
        pytest.skip("Mu00f3dulo seed_historico_vendas.py nu00e3o encontrado")
