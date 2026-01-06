import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio

# Testes para rotas do mu00f3dulo de desperdu00edcio (parte 3 - Metas)
@pytest.mark.usefixtures('client')
class TestRoutesDesperdicioParte3:
    
    def test_listar_metas(self, client, monkeypatch):
        """Testa a rota de listagem de metas de reduu00e7u00e3o de desperdu00edcio"""
        # Mock para metas
        mock_metas = [
            MagicMock(
                id=1,
                categoria=MagicMock(nome='Vencidos', cor='#FF0000'),
                valor_inicial=1000.0,
                meta_reducao_percentual=20.0,
                data_inicio=date.today() - timedelta(days=30),
                data_fim=date.today() + timedelta(days=30),
                responsavel='Gerente Teste',
                progresso_atual=lambda: {'percentual_concluido': 60, 'status': 'em_progresso'}
            )
        ]
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.join().all.return_value = mock_metas
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Metas de Redu\xc3\xa7\xc3\xa3o de Desperdu\xc3\xadcio' in response.data
        assert b'Vencidos' in response.data
        assert b'60%' in response.data
    
    def test_criar_meta_get(self, client, monkeypatch):
        """Testa a rota de criar meta (GET)"""
        # Mock para categorias
        mock_categorias = [
            MagicMock(id=1, nome='Vencidos'),
            MagicMock(id=2, nome='Quebrados')
        ]
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.all.return_value = mock_categorias
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas/criar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Nova Meta de Redu\xc3\xa7\xc3\xa3o de Desperdu\xc3\xadcio' in response.data
        assert b'Vencidos' in response.data
    
    def test_criar_meta_post(self, client, monkeypatch):
        """Testa a rota de criar meta (POST)"""
        # Mock para MetaDesperdicio
        mock_meta = MagicMock(id=1)
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.desperdicio.views.MetaDesperdicio', lambda **kwargs: mock_meta)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Dados do formulu00e1rio
        data_inicio = date.today().strftime('%Y-%m-%d')
        data_fim = (date.today() + timedelta(days=90)).strftime('%Y-%m-%d')
        form_data = {
            'categoria_id': '1',
            'valor_inicial': '1000',
            'meta_reducao_percentual': '20',
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'responsavel': 'Gerente Teste',
            'descricao': 'Meta de teste',
            'acoes_propostas': 'Au00e7u00f5es para teste'
        }
        
        # Fazer requisiu00e7u00e3o POST
        response = client.post('/desperdicio/metas/criar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Metas de Redu\xc3\xa7\xc3\xa3o de Desperdu\xc3\xadcio' in response.data
    
    def test_visualizar_meta(self, client, monkeypatch):
        """Testa a rota de visualizar detalhes de uma meta"""
        # Mock para meta existente
        mock_meta = MagicMock(
            id=1,
            categoria=MagicMock(nome='Vencidos', cor='#FF0000'),
            valor_inicial=1000.0,
            meta_reducao_percentual=20.0,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today() + timedelta(days=30),
            responsavel='Gerente Teste',
            descricao='Descriu00e7u00e3o da meta',
            acoes_propostas='Au00e7u00f5es propostas para a meta',
            meta_valor_absoluto=lambda: 800.0,
            progresso_atual=lambda: {
                'valor_meta': 800.0,
                'valor_atual': 400.0,
                'percentual_meta': 20.0,
                'percentual_concluido': 60.0,
                'status': 'em_progresso',
                'dias_decorridos': 30,
                'dias_totais': 60,
                'percentual_tempo': 50.0
            }
        )
        
        # Mock para registros da categoria
        mock_registros = [
            MagicMock(
                data_registro=date.today() - timedelta(days=20),
                quantidade=2.5,
                valor_estimado=50.0,
                produto=MagicMock(nome='Produto 1')
            ),
            MagicMock(
                data_registro=date.today() - timedelta(days=10),
                quantidade=1.5,
                valor_estimado=30.0,
                produto=MagicMock(nome='Produto 2')
            )
        ]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is MetaDesperdicio:
                query = MagicMock()
                query.filter_by().first.return_value = mock_meta
                return query
            elif model is RegistroDesperdicio:
                query = MagicMock()
                query.join().filter().order_by().all.return_value = mock_registros
                return query
            else:
                return MagicMock()
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas/visualizar/1')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Detalhes da Meta de Redu\xc3\xa7\xc3\xa3o' in response.data
        assert b'Vencidos' in response.data
        assert b'60%' in response.data
        assert b'Gerente Teste' in response.data
    
    def test_editar_meta(self, client, monkeypatch):
        """Testa a rota de editar meta"""
        # Mock para meta existente
        mock_meta = MagicMock(
            id=1,
            categoria_id=1,
            categoria=MagicMock(nome='Vencidos'),
            valor_inicial=1000.0,
            meta_reducao_percentual=20.0,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today() + timedelta(days=30),
            responsavel='Gerente Teste',
            descricao='Descriu00e7u00e3o original',
            acoes_propostas='Au00e7u00f5es originais'
        )
        
        # Mock para categorias
        mock_categorias = [MagicMock(id=1, nome='Vencidos')]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is MetaDesperdicio:
                query = MagicMock()
                query.filter_by().first.return_value = mock_meta
                return query
            elif model is CategoriaDesperdicio:
                query = MagicMock()
                query.all.return_value = mock_categorias
                return query
            else:
                return MagicMock()
        
        # Aplicar mock para GET
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas/editar/1')
        
        # Verificar resposta GET
        assert response.status_code == 200
        assert b'Editar Meta de Redu\xc3\xa7\xc3\xa3o' in response.data
        
        # Aplicar mock para POST
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Dados do formulu00e1rio
        data_inicio = date.today().strftime('%Y-%m-%d')
        data_fim = (date.today() + timedelta(days=60)).strftime('%Y-%m-%d')
        form_data = {
            'categoria_id': '1',
            'valor_inicial': '1000',
            'meta_reducao_percentual': '25',  # Alterado
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'responsavel': 'Novo Gerente',    # Alterado
            'descricao': 'Descriu00e7u00e3o atualizada',  # Alterado
            'acoes_propostas': 'Au00e7u00f5es atualizadas'   # Alterado
        }
        
        # Fazer requisiu00e7u00e3o POST
        response = client.post('/desperdicio/metas/editar/1', data=form_data, follow_redirects=True)
        
        # Verificar resposta POST
        assert response.status_code == 200
        assert b'Metas de Redu\xc3\xa7\xc3\xa3o de Desperdu\xc3\xadcio' in response.data
        
        # Verificar se os campos foram atualizados
        assert mock_meta.meta_reducao_percentual == 25.0
        assert mock_meta.responsavel == 'Novo Gerente'
        assert mock_meta.descricao == 'Descriu00e7u00e3o atualizada'
        assert mock_meta.acoes_propostas == 'Au00e7u00f5es atualizadas'
    
    def test_excluir_meta(self, client, monkeypatch):
        """Testa a rota de excluir meta"""
        # Mock para meta existente
        mock_meta = MagicMock(id=1)
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_meta
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.delete', lambda *args: None)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas/excluir/1', follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Metas de Redu\xc3\xa7\xc3\xa3o de Desperdu\xc3\xadcio' in response.data
    
    def test_relatorios_desperdicio(self, client, monkeypatch):
        """Testa a rota de relatu00f3rios de desperdu00edcio"""
        # Mock para estatu00edsticas
        mock_categorias = [
            MagicMock(id=1, nome='Vencidos', cor='#FF0000'),
            MagicMock(id=2, nome='Quebrados', cor='#0000FF')
        ]
        
        # Mock para estatu00edsticas por categoria
        mock_stats_categoria = [
            (1, 'Vencidos', '#FF0000', 500.0),
            (2, 'Quebrados', '#0000FF', 300.0)
        ]
        
        # Mock para estatu00edsticas por mu00eas
        mock_stats_mes = [
            (1, 200.0),  # Janeiro
            (2, 300.0),  # Fevereiro
            (3, 250.0)   # Maru00e7o
        ]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is CategoriaDesperdicio:
                query = MagicMock()
                query.all.return_value = mock_categorias
                return query
            elif model is RegistroDesperdicio:
                query = MagicMock()
                
                # Mock para estatu00edsticas por categoria
                categoria_query = MagicMock()
                categoria_query.group_by().all.return_value = mock_stats_categoria
                query.join().with_entities().group_by = lambda: categoria_query
                
                # Mock para estatu00edsticas por mu00eas
                mes_query = MagicMock()
                mes_query.group_by().all.return_value = mock_stats_mes
                query.with_entities().filter().group_by = lambda: mes_query
                
                return query
            else:
                return MagicMock()
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/relatorios')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Relat\xc3\xb3rios de Desperdu\xc3\xadcio' in response.data
        
        # Testar com filtros
        response_filtrada = client.get('/desperdicio/relatorios?ano=2025&categoria_id=1')
        assert response_filtrada.status_code == 200
