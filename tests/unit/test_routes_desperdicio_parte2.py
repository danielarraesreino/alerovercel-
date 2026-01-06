import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto

# Testes para rotas do mu00f3dulo de desperdu00edcio (parte 2)
@pytest.mark.usefixtures('client')
class TestRoutesDesperdicioParte2:
    
    def test_acessar_categoria(self, client, monkeypatch):
        """Testa o acesso u00e0 lista de categorias"""
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
        monkeypatch.setattr('app.routes.desperdicio.views.CategoriaDesperdicio.query', mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/categorias')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Categorias de Desperdu00edcio' in response.data
    
    def test_listar_registros(self, client, monkeypatch):
        """Testa a rota de listagem de registros de desperdu00edcio"""
        # Mock para registros
        mock_registros = [
            MagicMock(
                id=1,
                data_registro=datetime.now(),
                categoria=MagicMock(nome='Vencidos', cor='#FF0000'),
                produto=MagicMock(nome='Produto Teste'),
                quantidade=2.5,
                unidade_medida='kg',
                valor_estimado=50.0,
                motivo='Produto vencido',
                responsavel='Funcionu00e1rio Teste'
            )
        ]
        
        # Mock para categorias (usado no filtro)
        mock_categorias = [
            MagicMock(id=1, nome='Vencidos'),
            MagicMock(id=2, nome='Quebrados')
        ]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is RegistroDesperdicio:
                query = MagicMock()
                # Mock para paginau00e7u00e3o
                query.join().filter().order_by().paginate.return_value = MagicMock(
                    items=mock_registros,
                    pages=1,
                    page=1,
                    per_page=20,
                    total=1
                )
                return query
            elif model is CategoriaDesperdicio:
                query = MagicMock()
                query.all.return_value = mock_categorias
                return query
            else:
                return MagicMock()
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/registros')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registros de Desperdu00edcio' in response.data
        assert b'Produto Teste' in response.data
        
        # Testar com filtros
        response_filtrada = client.get('/desperdicio/registros?categoria_id=1&data_inicio=2025-01-01&data_fim=2025-12-31')
        assert response_filtrada.status_code == 200
    
    def test_registrar_desperdicio_get(self, client, monkeypatch):
        """Testa a rota de registrar desperdu00edcio (GET)"""
        # Mock para categorias
        mock_categorias = [
            MagicMock(id=1, nome='Vencidos'),
            MagicMock(id=2, nome='Quebrados')
        ]
        
        # Mock para produtos
        mock_produtos = [
            MagicMock(id=1, nome='Produto 1', unidade_medida='kg', preco_unitario=20.0),
            MagicMock(id=2, nome='Produto 2', unidade_medida='lt', preco_unitario=15.0)
        ]
        
        # Preparar mocks para consultas
        def mock_query_side_effect(model):
            if model is CategoriaDesperdicio:
                query = MagicMock()
                query.all.return_value = mock_categorias
                return query
            elif model is Produto:
                query = MagicMock()
                query.order_by().all.return_value = mock_produtos
                return query
            else:
                return MagicMock()
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', mock_query_side_effect)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/registro/criar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registrar Desperdu00edcio' in response.data
        assert b'Vencidos' in response.data
        assert b'Produto 1' in response.data
    
    def test_registrar_desperdicio_post(self, client, monkeypatch):
        """Testa a rota de registrar desperdu00edcio (POST)"""
        # Mock para produto (para o cu00e1lculo automru00e1tico do valor)
        mock_produto = MagicMock(id=1, nome='Produto 1', preco_unitario=20.0)
        
        # Mock para RegistroDesperdicio
        mock_registro = MagicMock(id=1)
        
        # Preparar mocks para consultas
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_produto
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        monkeypatch.setattr('app.routes.desperdicio.views.RegistroDesperdicio', lambda **kwargs: mock_registro)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.commit', lambda: None)
        
        # Dados do formulu00e1rio
        form_data = {
            'categoria_id': '1',
            'produto_id': '1',
            'quantidade': '2.5',
            'unidade_medida': 'kg',
            'data_registro': datetime.now().strftime('%Y-%m-%d'),
            'motivo': 'Produto vencido',
            'responsavel': 'Funcionu00e1rio Teste',
            'local': 'Estoque',
            'descricao': 'Registro de teste',
            'calcular_valor': 'on'  # Usar cu00e1lculo automru00e1tico
        }
        
        # Fazer requisiu00e7u00e3o POST
        response = client.post('/desperdicio/registro/criar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registros de Desperdu00edcio' in response.data
        
        # Verificar se o valor foi calculado (2.5 * 20.0 = 50.0)
        assert mock_registro.valor_estimado == 50.0
    
    def test_visualizar_registro(self, client, monkeypatch):
        """Testa a rota de visualizar detalhes de um registro"""
        # Mock para registro existente
        mock_registro = MagicMock(
            id=1,
            data_registro=datetime.now(),
            categoria=MagicMock(nome='Vencidos', cor='#FF0000'),
            produto=MagicMock(nome='Produto Teste', unidade_medida='kg'),
            quantidade=2.5,
            unidade_medida='kg',
            valor_estimado=50.0,
            motivo='Produto vencido',
            responsavel='Funcionu00e1rio Teste',
            local='Estoque',
            descricao='Descriu00e7u00e3o do registro'
        )
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_registro
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/registro/visualizar/1')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Detalhes do Registro de Desperdu00edcio' in response.data
        assert b'Produto Teste' in response.data
        assert b'2.5 kg' in response.data
        assert b'R$ 50.0' in response.data
    
    def test_listar_metas(self, client, monkeypatch):
        """Testa a rota de listagem de metas de reduu00e7u00e3o de desperdu00edcio"""
        # Mock para metas
        mock_metas = [
            MagicMock(
                id=1,
                descricao='Reduzir desperdu00edcio em 20%',
                data_inicio=date.today(),
                data_fim=date.today() + timedelta(days=30),
                valor_inicial=1000.0,
                meta_reducao_percentual=20.0,
                categoria=MagicMock(nome='Vencidos'),
                progresso_atual=MagicMock(return_value=45.0)
            )
        ]
        
        # Preparar mock para consulta
        mock_query = MagicMock()
        mock_query.all.return_value = mock_metas
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.desperdicio.views.MetaDesperdicio.query', mock_query)
        
        # Fazer requisiu00e7u00e3o GET
        response = client.get('/desperdicio/metas')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Metas de Reduu00e7u00e3o de Desperdu00edcio' in response.data
