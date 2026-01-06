import pytest
from unittest.mock import patch, MagicMock, call
import sys

from app.scripts.create_db import setup_database

@pytest.fixture
def mock_db():
    with patch('app.scripts.create_db.db') as mock_db:
        yield mock_db

@pytest.fixture
def mock_app():
    with patch('app.scripts.create_db.create_app') as mock_create_app:
        mock_app = MagicMock()
        mock_context = MagicMock()
        mock_app.app_context.return_value = mock_context
        mock_create_app.return_value = mock_app
        yield mock_app

def test_setup_database_create(mock_db, mock_app):
    """Testa a criação do banco de dados sem drop"""
    # Chamar a função com drop=False
    setup_database(drop=False)
    
    # Verificar se create_app foi chamado com o ambiente correto
    from app.scripts.create_db import create_app
    create_app.assert_called_once_with('development')
    
    # Verificar se app_context foi usado
    mock_app.app_context.assert_called_once()
    
    # Verificar se db.create_all foi chamado, mas não db.drop_all
    mock_db.create_all.assert_called_once()
    mock_db.drop_all.assert_not_called()
    
    # Verificar mensagem impressa
    assert any('Criando' in call[0][0] for call in sys.stdout.write.call_args_list)

def test_setup_database_drop_and_create(mock_db, mock_app):
    """Testa a criação do banco de dados com drop"""
    # Chamar a função com drop=True
    setup_database(drop=True)
    
    # Verificar se create_app foi chamado com o ambiente correto
    from app.scripts.create_db import create_app
    create_app.assert_called_once_with('development')
    
    # Verificar se app_context foi usado
    mock_app.app_context.assert_called_once()
    
    # Verificar se tanto db.drop_all quanto db.create_all foram chamados
    mock_db.drop_all.assert_called_once()
    mock_db.create_all.assert_called_once()
    
    # Verificar mensagens impressas
    assert any('Excluindo' in call[0][0] for call in sys.stdout.write.call_args_list)
    assert any('Criando' in call[0][0] for call in sys.stdout.write.call_args_list)

def test_setup_database_custom_environment(mock_db, mock_app):
    """Testa a criação do banco de dados com ambiente personalizado"""
    # Chamar a função com ambiente personalizado
    setup_database(drop=False, environment='testing')
    
    # Verificar se create_app foi chamado com o ambiente correto
    from app.scripts.create_db import create_app
    create_app.assert_called_once_with('testing')
    
    # Verificar se app_context foi usado
    mock_app.app_context.assert_called_once()
    
    # Verificar se db.create_all foi chamado
    mock_db.create_all.assert_called_once()

def test_main_execution(mock_db, mock_app):
    """Testa a execução direta do script"""
    with patch('app.scripts.create_db.setup_database') as mock_setup:
        # Simular execução como script principal
        from app.scripts.create_db import __name__ as module_name
        original_name = module_name
        try:
            sys.modules['app.scripts.create_db'].__name__ = '__main__'
            # Reimportar para executar o bloco if __name__ == '__main__'
            import importlib
            importlib.reload(sys.modules['app.scripts.create_db'])
            
            # Verificar se setup_database foi chamado
            mock_setup.assert_called_once()
        finally:
            # Restaurar o nome original
            sys.modules['app.scripts.create_db'].__name__ = original_name
