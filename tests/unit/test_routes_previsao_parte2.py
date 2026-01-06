import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta
from io import BytesIO
import pandas as pd
import numpy as np
from flask import url_for

from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_cardapio import CardapioItem, Cardapio
from app.models.modelo_prato import Prato
from app.routes.previsao.views import calcular_media_movel, calcular_regressao_linear

@pytest.fixture
def mock_historico_vendas():
    """Mock para o histórico de vendas"""
    venda1 = MagicMock(spec=HistoricoVendas)
    venda1.id = 1
    venda1.data = date(2023, 5, 15)
    venda1.cardapio_item_id = 1
    venda1.prato_id = None
    venda1.quantidade = 2
    venda1.valor_unitario = 25.90
    venda1.valor_total = 51.80
    venda1.periodo_dia = "noite"
    venda1.dia_semana = 0  # Segunda-feira
    venda1.cardapio_item = MagicMock(nome="Item de Cardápio Teste")
    
    venda2 = MagicMock(spec=HistoricoVendas)
    venda2.id = 2
    venda2.data = date(2023, 5, 16)
    venda2.cardapio_item_id = None
    venda2.prato_id = 1
    venda2.quantidade = 3
    venda2.valor_unitario = 19.90
    venda2.valor_total = 59.70
    venda2.periodo_dia = "tarde"
    venda2.dia_semana = 1  # Terça-feira
    venda2.prato = MagicMock(nome="Prato Teste")
    
    return [venda1, venda2]

@pytest.fixture
def mock_fatores_sazonalidade():
    """Mock para fatores de sazonalidade"""
    fator1 = MagicMock(spec=FatorSazonalidade)
    fator1.id = 1
    fator1.mes = 12
    fator1.dia_semana = None
    fator1.periodo_dia = None
    fator1.evento = "Natal"
    fator1.cardapio_item_id = None
    fator1.prato_id = None
    fator1.categoria_id = None
    fator1.fator = 1.5
    fator1.descricao = "Aumento nas vendas durante o Natal"
    
    fator2 = MagicMock(spec=FatorSazonalidade)
    fator2.id = 2
    fator2.mes = None
    fator2.dia_semana = 6  # Domingo
    fator2.periodo_dia = "almoço"
    fator2.evento = None
    fator2.cardapio_item_id = None
    fator2.prato_id = None
    fator2.categoria_id = 1
    fator2.fator = 1.3
    fator2.descricao = "Aumento nos almoços de domingo"
    
    return [fator1, fator2]

class TestImportacaoExportacao:
    """Testes específicos para as funcionalidades de importação e exportação"""
    
    def test_importar_historico_get(self, client):
        """Testa a rota GET para importar histórico de vendas"""
        response = client.get('/previsao/historico/importar')
        
        assert response.status_code == 200
        assert b'Importar Hist' in response.data  # Parte do título da página
        assert b'<form' in response.data
        assert b'enctype="multipart/form-data"' in response.data
    
    def test_importar_historico_post_sucesso(self, client):
        """Testa a importação bem-sucedida de um arquivo CSV"""
        with patch('app.routes.previsao.views.request') as mock_request, \
             patch('app.routes.previsao.views.pd.read_csv') as mock_read_csv, \
             patch('app.routes.previsao.views.HistoricoVendas') as mock_modelo, \
             patch('app.routes.previsao.views.CardapioItem') as mock_cardapio_item, \
             patch('app.routes.previsao.views.Prato') as mock_prato, \
             patch('app.routes.previsao.views.db.session'):
            
            # Criar dados de teste para o DataFrame
            mock_df = pd.DataFrame({
                'data': ['2023-05-01', '2023-05-02'],
                'item_id': [1, 2],
                'tipo_item': ['cardapio_item', 'prato'],
                'quantidade': [2, 3],
                'valor_unitario': [25.90, 19.90],
                'periodo_dia': ['noite', 'tarde']
            })
            mock_read_csv.return_value = mock_df
            
            # Mock para o arquivo
            mock_file = MagicMock()
            mock_file.filename = 'vendas.csv'
            mock_file.save = MagicMock()
            mock_request.files = {'arquivo': mock_file}
            
            # Mock para itens de cardápio e pratos
            mock_cardapio_item.query.get.return_value = MagicMock(id=1, nome='Item Teste')
            mock_prato.query.get.return_value = MagicMock(id=2, nome='Prato Teste')
            
            # Fazer a requisição
            response = client.post(
                '/previsao/historico/importar',
                data={'submit': 'Importar'},
                follow_redirects=True
            )
            
            # Verificar o resultado
            assert response.status_code == 200
    
    def test_importar_historico_post_erro(self, client):
        """Testa a importação com erro de formato de arquivo"""
        with patch('app.routes.previsao.views.request') as mock_request:
            # Mock para o arquivo com formato inválido
            mock_file = MagicMock()
            mock_file.filename = 'vendas.txt'
            mock_request.files = {'arquivo': mock_file}
            
            # Fazer a requisição
            response = client.post(
                '/previsao/historico/importar',
                data={'submit': 'Importar'},
                follow_redirects=True
            )
            
            # Verificar o resultado
            assert response.status_code == 200
    
    def test_exportar_historico_get(self, client):
        """Testa a rota GET para exportar histórico de vendas"""
        response = client.get('/previsao/historico/exportar')
        
        assert response.status_code == 200
        assert b'Exportar Hist' in response.data  # Parte do título da página
        assert b'<form' in response.data
    
    def test_exportar_historico_post_csv(self, client, mock_historico_vendas):
        """Testa a exportação do histórico em formato CSV"""
        with patch('app.routes.previsao.views.HistoricoVendas') as mock_modelo, \
             patch('app.routes.previsao.views.CardapioItem') as mock_cardapio_item, \
             patch('app.routes.previsao.views.Prato') as mock_prato, \
             patch('app.routes.previsao.views.datetime'):
            
            # Configurar mocks
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = mock_historico_vendas
            mock_modelo.query = mock_query
            
            # Dados do formulário
            form_data = {
                'data_inicio': '2023-05-01',
                'data_fim': '2023-05-31',
                'formato': 'csv'
            }
            
            # Fazer a requisição
            response = client.post(
                '/previsao/exportar-historico',
                data=form_data
            )
            
            # Verificar o resultado
            assert response.status_code == 200
            assert 'text/csv' in response.content_type
    
    def test_exportar_historico_post_excel(self, client, mock_historico_vendas):
        """Testa a exportação do histórico em formato Excel"""
        with patch('app.routes.previsao.views.HistoricoVendas') as mock_modelo, \
             patch('app.routes.previsao.views.CardapioItem') as mock_cardapio_item, \
             patch('app.routes.previsao.views.Prato') as mock_prato, \
             patch('app.routes.previsao.views.pd.DataFrame') as mock_df, \
             patch('app.routes.previsao.views.BytesIO') as mock_bytesio, \
             patch('app.routes.previsao.views.datetime'):
            
            # Configurar mocks
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = mock_historico_vendas
            mock_modelo.query = mock_query
            
            # Mock para o DataFrame e Excel
            mock_df_instance = MagicMock()
            mock_df.return_value = mock_df_instance
            mock_df_instance.to_excel = MagicMock()
            
            # Dados do formulário
            form_data = {
                'data_inicio': '2023-05-01',
                'data_fim': '2023-05-31',
                'formato': 'excel'
            }
            
            # Fazer a requisição
            response = client.post(
                '/previsao/exportar-historico',
                data=form_data
            )
            
            # Verificar o resultado
            assert response.status_code == 200

class TestAlgoritmosPrevisao:
    """Testes adicionais para algoritmos de previsão"""
    
    def test_media_movel_com_dados_sazonais(self):
        """Testa o algoritmo de média móvel com dados que apresentam sazonalidade"""
        # Dados com padrão semanal (mais vendas nos fins de semana)
        dados = [10, 12, 10, 15, 20, 30, 40, 12, 10, 11, 18, 22, 32, 42]
        
        # Janela de 7 dias (uma semana)
        resultado, confiabilidade = calcular_media_movel(dados, janela=7)
        
        # Verificar resultado
        assert len(resultado) == len(dados) + 7
        assert 0 <= confiabilidade <= 1
        
        # A média da última semana
        media_ultima_semana = sum(dados[-7:]) / 7
        # As previsões devem ser iguais à média da última semana
        for i in range(len(dados), len(resultado)):
            assert resultado[i] == pytest.approx(media_ultima_semana)
    
    def test_regressao_linear_com_tendencia_negativa(self):
        """Testa o algoritmo de regressão linear com tendência negativa"""
        # Dados com tendência decrescente
        dados = [100, 95, 90, 85, 80, 75, 70]
        
        # Previsão para 7 dias
        resultado, confiabilidade = calcular_regressao_linear(dados)
        
        # Verificar resultado
        assert len(resultado) == len(dados) + 7
        assert resultado[len(dados)] < dados[-1]  # O próximo valor previsto deve ser menor que o último
        
        # A previsão deve continuar a tendência decrescente
        for i in range(len(dados), len(resultado)-1):
            assert resultado[i] > resultado[i+1]

def test_registrar_venda_classmethod():
    """Testa o método de classe para registrar vendas"""
    with patch('app.models.modelo_previsao.db.session') as mock_session:
        # Parâmetros de teste
        data = '2023-05-15'
        item_id = 1
        tipo_item = 'cardapio_item'
        quantidade = 2
        valor_unitario = 25.90
        periodo_dia = 'noite'
        
        # Chamar o método
        HistoricoVendas.registrar_venda(
            data=data,
            item_id=item_id,
            tipo_item=tipo_item,
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            periodo_dia=periodo_dia
        )
        
        # Verificar se o objeto foi adicionado e commit foi chamado
        assert mock_session.add.called
        assert mock_session.commit.called

def test_previsao_demanda_get_set_valores():
    """Testa os métodos get/set de valores previstos em PrevisaoDemanda"""
    # Criar objeto de previsão
    previsao = PrevisaoDemanda()
    
    # Valores de teste
    valores_teste = {
        '2023-05-01': 10,
        '2023-05-02': 15,
        '2023-05-03': 12
    }
    
    # Definir valores
    previsao.set_valores_previstos(valores_teste)
    
    # Verificar valores
    valores_obtidos = previsao.get_valores_previstos()
    assert valores_obtidos == valores_teste
    
    # Testar obtenção de valor específico
    valor_dia = previsao.get_previsao_para_data('2023-05-02')
    assert valor_dia == 15
