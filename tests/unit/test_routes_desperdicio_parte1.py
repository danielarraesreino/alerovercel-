import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto

# Testes para rotas do mu00f3dulo de desperdu00edcio (parte 1)
@pytest.mark.usefixtures('client')
class TestRoutesDesperdicioParte1:
    
    def test_index(self, client, monkeypatch):
        """Testa a rota principal do mu00f3dulo de desperdu00edcio"""
        # Mock para estatu00edsticas de desperdu00edcio
        mock_stats = [
            {'categoria': 'Vencidos', 'valor': 500.0, 'percentual': 50},
            {'categoria': 'Quebrados', 'valor': 300.0, 'percentual': 30},
            {'categoria': 'Outros', 'valor': 200.0, 'percentual': 20}
        ]
        
        # Mock para registros recentes
        mock_registros = [
            MagicMock(
                id=1, 
                data_registro=datetime.now(), 
                categoria=MagicMock(nome='Vencidos', cor='#FF0000'),
                produto=MagicMock(nome='Produto Teste'),
                quantidade=2.5,
                valor_estimado=50.0
            )
        ]
        
        # Mock para metas
        mock_metas = [
            MagicMock(
                id=1,
                categoria=MagicMock(nome='Vencidos'),
                valor_inicial=1000.0,
                meta_reducao_percentual=20.0,
                progresso_atual=lambda: {'percentual_concluido': 60, 'status': 'em_progresso'}
            )
        ]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is RegistroDesperdicio:
                query = MagicMock()
                query.join().order_by().limit().all.return_value = mock_registros
                
                # Mock para estatu00edsticas
                stats_query = MagicMock()
                stats_query.group_by().all.return_value = [
                    (1, 'Vencidos', '#FF0000', 500.0),
                    (2, 'Quebrados', '#0000FF', 300.0),
                    (3, 'Outros', '#00FF00', 200.0)
                ]
                query.join().with_entities().group_by = lambda: stats_query
                return query
            elif model is MetaDesperdicio:
                query = MagicMock()
                query.join().filter().all.return_value = mock_metas
                return query
            else:
                return MagicMock()
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Dashboard de Desperdu00edcio' in response.data
    
    def test_listar_categorias(self, client, monkeypatch):
        """Testa a rota de listagem de categorias de desperdu00edcio"""
        # Mock para categorias
        mock_categorias = [
            MagicMock(
                id=1,
                nome='Vencidos',
                descricao='Produtos vencidos',
                cor='#FF0000'
            ),
            MagicMock(
                id=2,
                nome='Quebrados',
                descricao='Produtos quebrados',
                cor='#0000FF'
            )
        ]
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.all.return_value = mock_categorias
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/categorias')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categorias de Desperdu00edcio' in response.data
        assert b'Vencidos' in response.data
        assert b'Quebrados' in response.data
    
    def test_criar_categoria_get(self, client):
        """Testa a rota de criar categoria (GET)"""
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/categoria/criar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Nova Categoria de Desperdu00edcio' in response.data
        assert b'<form' in response.data
    
    def test_criar_categoria_post(self, client, monkeypatch):
        """Testa a rota de criar categoria (POST)"""
        # Mock para CategoriaDesperdicio
        mock_categoria = MagicMock(id=1)
        
        # Criar um mock para a classe CategoriaDesperdicio que inclui o atributo query
        mock_categoria_class = MagicMock()
        mock_categoria_class.return_value = mock_categoria
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = None  # Nenhuma categoria existente com o mesmo nome
        mock_categoria_class.query = mock_query
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.desperdicio.views.CategoriaDesperdicio', mock_categoria_class)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Dados do formulu00e1rio
        form_data = {
            'nome': 'Nova Categoria',
            'descricao': 'Descriu00e7u00e3o da nova categoria',
            'cor': '#00FF00'
        }
        
        # Fazer requisiu00e7u00e3o POST
        response = client.post('/desperdicio/categoria/criar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categorias de Desperdu00edcio' in response.data
    
    def test_editar_categoria(self, client, monkeypatch):
        """Testa a rota de editar categoria"""
        # Mock para categoria existente
        mock_categoria = MagicMock(
            id=1,
            nome='Categoria Existente',
            descricao='Descriu00e7u00e3o original',
            cor='#FF0000'
        )
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_categoria
        
        # Criar um mock para a classe CategoriaDesperdicio que inclui o mu00e9todo get_or_404
        mock_categoria_class = MagicMock()
        mock_categoria_class.query = MagicMock()
        mock_categoria_class.query.get_or_404 = lambda id: mock_categoria
        
        # Aplicar mock para GET
        monkeypatch.setattr('app.routes.desperdicio.views.CategoriaDesperdicio', mock_categoria_class)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/categoria/editar/1')
        
        # Verificar resposta GET
        assert response.status_code == 200
        assert b'Editar Categoria de Desperdu00edcio' in response.data
        assert b'Categoria Existente' in response.data
        
        # Aplicar mock para POST
        # Criar um mock para verificar se ju00e1 existe outra categoria com o mesmo nome
        mock_categoria_existente = MagicMock()
        mock_categoria_existente.filter_by().first.return_value = None  # Nenhuma outra categoria com o mesmo nome
        mock_categoria_class.query = mock_categoria_existente
        
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Dados do formulu00e1rio
        form_data = {
            'nome': 'Categoria Atualizada',
            'descricao': 'Descriu00e7u00e3o atualizada',
            'cor': '#0000FF'
        }
        
        # Fazer requisiu00e7u00e3o POST
        response = client.post('/desperdicio/categoria/editar/1', data=form_data, follow_redirects=True)
        
        # Verificar resposta POST
        assert response.status_code == 200
        assert b'Categorias de Desperdu00edcio' in response.data
        
        # Verificar se os campos foram atualizados
        assert mock_categoria.nome == 'Categoria Atualizada'
        assert mock_categoria.descricao == 'Descriu00e7u00e3o atualizada'
        assert mock_categoria.cor == '#0000FF'
