import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
from io import BytesIO
import pandas as pd
import numpy as np

from app.routes.previsao.views import calcular_media_movel, calcular_regressao_linear
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_cardapio import CardapioItem, Cardapio
from app.models.modelo_prato import Prato

# Testes para funu00e7u00f5es de algoritmos de previsu00e3o
def test_calcular_media_movel():
    """Testa o algoritmo de mu00e9dia mu00f3vel"""
    # Dados de teste
    dados = [10, 12, 8, 15, 11, 13, 14]
    
    # Janela padru00e3o (7 dias)
    resultado, confiabilidade = calcular_media_movel(dados)
    
    # Como os dados tu00eam exatamente 7 dias, a previsu00e3o deve ser a mu00e9dia de todos
    media_esperada = sum(dados) / len(dados)
    assert len(resultado) == len(dados) + 7  # Dados originais + 7 dias de previsu00e3o
    for i in range(len(dados), len(resultado)):
        assert resultado[i] == pytest.approx(media_esperada)
    
    # Confiabilidade deve estar entre 0 e 1
    assert 0 <= confiabilidade <= 1
    
    # Janela menor
    resultado_janela_3, confiabilidade_3 = calcular_media_movel(dados, janela=3)
    # u00daltima mu00e9dia = (11 + 13 + 14) / 3
    ultima_media_esperada = (dados[-3] + dados[-2] + dados[-1]) / 3
    assert resultado_janela_3[len(dados)] == pytest.approx(ultima_media_esperada)
    
    # Caso com poucos dados
    dados_pequenos = [10, 12]
    resultado_pequeno, confiabilidade_pequeno = calcular_media_movel(dados_pequenos, janela=7)
    assert len(resultado_pequeno) == len(dados_pequenos) + 7
    assert confiabilidade_pequeno == 0.5  # Confiabilidade baixa por falta de dados

def test_calcular_regressao_linear():
    """Testa o algoritmo de regressu00e3o linear"""
    # Dados de teste (tendência crescente clara)
    dados = [10, 12, 14, 16, 18, 20, 22]
    
    # Previsu00e3o de 7 dias
    resultado, confiabilidade = calcular_regressao_linear(dados)
    
    # Verificar tamanho do resultado
    assert len(resultado) == len(dados) + 7
    
    # Verificar tendência (deve continuar crescendo)
    for i in range(len(dados)-1, len(resultado)-1):
        assert resultado[i+1] > resultado[i]
    
    # Confiabilidade deve ser alta para dados com tendência clara
    assert confiabilidade > 0.7
    
    # Teste com dados aleatórios (baixa confiabilidade esperada)
    dados_aleatorios = [10, 15, 8, 20, 12, 18, 9]
    resultado_aleatorio, confiabilidade_aleatoria = calcular_regressao_linear(dados_aleatorios)
    
    # Confiabilidade deve ser menor para dados sem tendência clara
    assert confiabilidade_aleatoria < confiabilidade

# Testes para rotas
@pytest.mark.usefixtures('client')
class TestRoutesPrevisao:
    
    def test_index(self, client, monkeypatch):
        """Testa a rota principal do mu00f3dulo de previsu00e3o"""
        # Mock para estatísticas de vendas
        mock_query = MagicMock()
        mock_query.join().filter().group_by().order_by().all.return_value = [
            (1, 'Item 1', 10, 250.0),
            (2, 'Item 2', 5, 125.0)
        ]
        
        # Mock para previsões recentes
        mock_query_previsoes = MagicMock()
        mock_query_previsoes.order_by().limit().all.return_value = [
            MagicMock(id=1, metodo='média móvel', data_criacao=datetime.now())
        ]
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', 
                          lambda *args: mock_query if args[0] is not PrevisaoDemanda else mock_query_previsoes)
        
        # Fazer requisição GET
        response = client.get('/previsao/')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Dashboard de Previs\xc3\xa3o' in response.data
    
    def test_listar_historico(self, client, monkeypatch):
        """Testa a rota de listagem de histórico de vendas"""
        # Mock para dados de histórico
        mock_query = MagicMock()
        mock_vendas = [
            MagicMock(
                id=1, 
                data=date.today(), 
                quantidade=5, 
                valor_total=100.0,
                cardapio_item=MagicMock(prato=MagicMock(nome='Prato Teste'))
            )
        ]
        mock_query.join().outerjoin().filter().order_by().paginate.return_value = MagicMock(
            items=mock_vendas,
            pages=1,
            page=1,
            per_page=20,
            total=1
        )
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/historico')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Hist\xc3\xb3rico de Vendas' in response.data
    
    def test_registrar_venda_get(self, client, monkeypatch):
        """Testa a rota de registrar venda (GET)"""
        # Mock para itens de cardápio
        mock_query = MagicMock()
        mock_query.join().all.return_value = [
            MagicMock(id=1, prato=MagicMock(nome='Prato 1'), preco_venda=25.0)
        ]
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/registrar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Registrar Venda' in response.data
    
    def test_registrar_venda_post(self, client, monkeypatch):
        """Testa a rota de registrar venda (POST)"""
        # Mock para buscar item de cardápio
        mock_item = MagicMock(id=1, preco_venda=25.0)
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_item
        
        # Mock para HistoricoVendas.registrar_venda
        mock_historico = MagicMock()
        mock_registrar = MagicMock(return_value=mock_historico)
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        monkeypatch.setattr('app.routes.previsao.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.previsao.views.db.session.commit', lambda: None)
        monkeypatch.setattr('app.routes.previsao.views.HistoricoVendas.registrar_venda', mock_registrar)
        
        # Dados do formulário
        form_data = {
            'cardapio_item_id': '1',
            'quantidade': '2',
            'valor_unitario': '25.0',
            'data': date.today().strftime('%Y-%m-%d'),
            'periodo_dia': 'tarde'
        }
        
        # Fazer requisição POST
        response = client.post('/previsao/registrar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert mock_registrar.called
    
    def test_gerar_previsao_get(self, client, monkeypatch):
        """Testa a rota de gerar previsão (GET)"""
        # Mock para itens de cardápio
        mock_query = MagicMock()
        mock_query.join().all.return_value = [
            MagicMock(id=1, prato=MagicMock(nome='Prato 1'))
        ]
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/gerar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Gerar Previs\xc3\xa3o de Demanda' in response.data
    
    @patch('app.routes.previsao.views.calcular_media_movel')
    @patch('app.routes.previsao.views.calcular_regressao_linear')
    def test_gerar_previsao_post(self, mock_regressao, mock_media, client, monkeypatch):
        """Testa a rota de gerar previsão (POST)"""
        # Configurar mocks para algoritmos de previsão
        mock_media.return_value = ([10, 12, 15, 15, 15], 0.8)
        mock_regressao.return_value = ([10, 12, 15, 18, 21], 0.9)
        
        # Mock para buscar item de cardápio
        mock_item = MagicMock(id=1)
        mock_query_item = MagicMock()
        mock_query_item.filter_by().first.return_value = mock_item
        
        # Mock para buscar histórico de vendas
        mock_historico = [
            MagicMock(data=date.today() - timedelta(days=2), quantidade=10),
            MagicMock(data=date.today() - timedelta(days=1), quantidade=12)
        ]
        mock_query_historico = MagicMock()
        mock_query_historico.filter().order_by().all.return_value = mock_historico
        
        # Mock para PrevisaoDemanda
        mock_previsao = MagicMock(id=1)
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', 
                          lambda model: mock_query_item if model is CardapioItem else mock_query_historico)
        monkeypatch.setattr('app.routes.previsao.views.PrevisaoDemanda', lambda **kwargs: mock_previsao)
        monkeypatch.setattr('app.routes.previsao.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.previsao.views.db.session.commit', lambda: None)
        
        # Dados do formulário
        data_inicio = date.today().strftime('%Y-%m-%d')
        data_fim = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        form_data = {
            'cardapio_item_id': '1',
            'metodo': 'media_movel',
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'parametros_janela': '7'
        }
        
        # Fazer requisição POST
        response = client.post('/previsao/gerar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert mock_media.called
        assert not mock_regressao.called  # Não deve chamar regressão se o método é média móvel
        
        # Testar com método de regressão linear
        form_data['metodo'] = 'regressao_linear'
        response = client.post('/previsao/gerar', data=form_data, follow_redirects=True)
        
        assert response.status_code == 200
        assert mock_regressao.called
    
    def test_visualizar_previsao(self, client, monkeypatch):
        """Testa a rota de visualizar previsão"""
        # Mock para previsão
        mock_previsao = MagicMock(
            id=1, 
            metodo='média móvel',
            data_inicio=date.today(),
            data_fim=date.today() + timedelta(days=7),
            confiabilidade=0.85,
            cardapio_item=MagicMock(prato=MagicMock(nome='Prato 1')),
            get_valores_previstos=lambda: {
                date.today().strftime('%Y-%m-%d'): 10,
                (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'): 12
            }
        )
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_previsao
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/visualizar/1')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Detalhes da Previs\xc3\xa3o' in response.data
    
    def test_listar_fatores_sazonalidade(self, client, monkeypatch):
        """Testa a rota de listar fatores de sazonalidade"""
        # Mock para fatores
        mock_fatores = [
            MagicMock(
                id=1, 
                dia_semana=5,  # Sábado
                fator=1.2,
                descricao='Aumento aos sábados',
                cardapio_item=MagicMock(prato=MagicMock(nome='Prato 1'))
            )
        ]
        mock_query = MagicMock()
        mock_query.join().all.return_value = mock_fatores
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/fatores')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Fatores de Sazonalidade' in response.data
    
    def test_criar_fator_sazonalidade_get(self, client, monkeypatch):
        """Testa a rota de criar fator de sazonalidade (GET)"""
        # Mock para itens de cardápio
        mock_query = MagicMock()
        mock_query.join().all.return_value = [
            MagicMock(id=1, prato=MagicMock(nome='Prato 1'))
        ]
        
        # Aplicar mock
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        
        # Fazer requisição GET
        response = client.get('/previsao/fatores/criar')
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Novo Fator de Sazonalidade' in response.data
    
    def test_criar_fator_sazonalidade_post(self, client, monkeypatch):
        """Testa a rota de criar fator de sazonalidade (POST)"""
        # Mock para FatorSazonalidade
        mock_fator = MagicMock(id=1)
        
        # Mock para consultas
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = MagicMock(id=1)  # CardapioItem
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        monkeypatch.setattr('app.routes.previsao.views.FatorSazonalidade', lambda **kwargs: mock_fator)
        monkeypatch.setattr('app.routes.previsao.views.db.session.add', lambda *args: None)
        monkeypatch.setattr('app.routes.previsao.views.db.session.commit', lambda: None)
        
        # Dados do formulário
        form_data = {
            'cardapio_item_id': '1',
            'dia_semana': '5',  # Sábado
            'fator': '1.2',
            'descricao': 'Aumento aos sábados'
        }
        
        # Fazer requisição POST
        response = client.post('/previsao/fatores/criar', data=form_data, follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Fatores de Sazonalidade' in response.data
    
    def test_editar_fator_sazonalidade(self, client, monkeypatch):
        """Testa a rota de editar fator de sazonalidade"""
        # Mock para fator existente
        mock_fator = MagicMock(
            id=1, 
            dia_semana=5,
            fator=1.2,
            descricao='Aumento aos sábados',
            cardapio_item_id=1,
            cardapio_item=MagicMock(prato=MagicMock(nome='Prato 1'))
        )
        
        # Mock para consultas
        mock_query_fator = MagicMock()
        mock_query_fator.filter_by().first.return_value = mock_fator
        
        mock_query_item = MagicMock()
        mock_query_item.join().all.return_value = [MagicMock(id=1, prato=MagicMock(nome='Prato 1'))]
        
        # Aplicar mocks para GET
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', 
                          lambda model: mock_query_fator if model is FatorSazonalidade else mock_query_item)
        
        # Fazer requisição GET
        response = client.get('/previsao/fatores/editar/1')
        
        # Verificar resposta GET
        assert response.status_code == 200
        assert b'Editar Fator de Sazonalidade' in response.data
        
        # Configurar mock para POST
        monkeypatch.setattr('app.routes.previsao.views.db.session.commit', lambda: None)
        
        # Dados do formulário
        form_data = {
            'cardapio_item_id': '1',
            'dia_semana': '6',  # Domingo (alterado)
            'fator': '1.3',     # Fator alterado
            'descricao': 'Aumento aos domingos'  # Descrição alterada
        }
        
        # Fazer requisição POST
        response = client.post('/previsao/fatores/editar/1', data=form_data, follow_redirects=True)
        
        # Verificar resposta POST
        assert response.status_code == 200
        assert b'Fatores de Sazonalidade' in response.data
        
        # Verificar se os campos foram atualizados
        assert mock_fator.dia_semana == 6
        assert mock_fator.fator == 1.3
        assert mock_fator.descricao == 'Aumento aos domingos'
    
    def test_excluir_fator_sazonalidade(self, client, monkeypatch):
        """Testa a rota de excluir fator de sazonalidade"""
        # Mock para fator existente
        mock_fator = MagicMock(id=1)
        
        # Mock para consultas
        mock_query = MagicMock()
        mock_query.filter_by().first.return_value = mock_fator
        
        # Aplicar mocks
        monkeypatch.setattr('app.routes.previsao.views.db.session.query', lambda *args: mock_query)
        monkeypatch.setattr('app.routes.previsao.views.db.session.delete', lambda *args: None)
        monkeypatch.setattr('app.routes.previsao.views.db.session.commit', lambda: None)
        
        # Fazer requisição GET
        response = client.get('/previsao/fatores/excluir/1', follow_redirects=True)
        
        # Verificar resposta
        assert response.status_code == 200
        assert b'Fatores de Sazonalidade' in response.data
