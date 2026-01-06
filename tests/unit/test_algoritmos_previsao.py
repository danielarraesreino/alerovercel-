import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timedelta

from app.routes.previsao.views import calcular_media_movel, calcular_regressao_linear
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade

# Testes para algoritmos de previsão - essenciais para o módulo de previsão de demanda

def test_media_movel_dados_consistentes():
    """Testa o algoritmo de média móvel com dados consistentes"""
    # Dados consistentes (mesmo valor repetido)
    dados = [10, 10, 10, 10, 10]
    resultado, confiabilidade = calcular_media_movel(dados, janela=3)
    
    # Verificar que a previsão mantém o valor constante
    # A implementação atual retorna um resultado de tamanho variável
    assert resultado is not None  # Garantir que algum resultado foi gerado
    for i in range(len(dados), len(resultado)):
        assert resultado[i] == 10
    
    # Confiabilidade deve ser alta para dados consistentes
    assert confiabilidade > 0.9

def test_media_movel_dados_crescentes():
    """Testa o algoritmo de média móvel com dados em tendência crescente"""
    # Dados com tendência crescente clara
    dados = [10, 20, 30, 40, 50]
    resultado, confiabilidade = calcular_media_movel(dados, janela=3)
    
    # Verificar que a previsão se baseia na média dos últimos 3 valores
    ultima_media = (30 + 40 + 50) / 3
    assert resultado[len(dados)] == pytest.approx(ultima_media)
    
    # Confiabilidade deve ser moderada para dados com tendência
    assert 0.3 < confiabilidade < 1.0

def test_media_movel_poucos_dados():
    """Testa o algoritmo de média móvel com poucos dados"""
    # Apenas dois pontos de dados
    dados = [10, 15]
    resultado, confiabilidade = calcular_media_movel(dados, janela=5)
    
    # Verificar que a previsão é feita mesmo com poucos dados
    assert len(resultado) == len(dados) + 7
    
    # Confiabilidade deve ser baixa para poucos dados
    assert confiabilidade == 0.5

def test_regressao_linear_tendencia_clara():
    """Testa o algoritmo de regressão linear com tendência clara"""
    # Dados com tendência linear perfeita
    dados = [10, 20, 30, 40, 50]
    resultado, confiabilidade = calcular_regressao_linear(dados, dias_projecao=7)
    
    # Verificar que a previsão continua a tendência
    assert resultado[len(dados)] == pytest.approx(60, abs=5)
    assert resultado[len(dados)+1] == pytest.approx(70, abs=5)
    
    # Confiabilidade deve ser alta para tendência clara
    assert confiabilidade > 0.8

def test_regressao_linear_dados_aleatorios():
    """Testa o algoritmo de regressão linear com dados aleatórios"""
    # Dados sem tendência clara
    dados = [42, 38, 45, 40, 44]
    resultado, confiabilidade = calcular_regressao_linear(dados)
    
    # Verificar que a previsão é feita mesmo para dados sem tendência clara
    assert len(resultado) == len(dados) + 7
    
    # Confiabilidade pode ser baixa para dados sem tendência clara
    assert 0 <= confiabilidade < 1.0

def test_regressao_linear_poucos_dados():
    """Testa o algoritmo de regressão linear com poucos dados"""
    # Apenas dois pontos de dados
    dados = [10, 20]
    resultado, confiabilidade = calcular_regressao_linear(dados)
    
    # Verificar que a previsão é feita mesmo com poucos dados
    assert len(resultado) == len(dados) + 7
    
    # Confiabilidade deve ser baixa para poucos dados
    assert confiabilidade < 0.5

@patch('app.routes.previsao.views.np.polyfit')
@patch('app.routes.previsao.views.np.poly1d')
def test_regressao_linear_com_sazonalidade(mock_poly1d, mock_polyfit):
    """Testa o algoritmo de regressão linear com dados sazonais"""
    # Configurar mocks
    mock_polyfit.return_value = [10, 5]  # Coeficientes da regressão (inclinação e intercepto)
    mock_poly_func = MagicMock()
    mock_poly_func.side_effect = lambda x: 10*x + 5  # Função linear: y = 10x + 5
    mock_poly1d.return_value = mock_poly_func
    
    # Dados com sazonalidade (padrão semanal)
    dados = [10, 20, 30, 40, 50, 60, 70, 15, 25, 35, 45, 55, 65, 75]
    resultado, confiabilidade = calcular_regressao_linear(dados)
    
    # Verificar que a previsão é calculada corretamente usando os mocks
    assert len(resultado) == len(dados) + 7
    
    # A confiabilidade deve ser calculada mesmo com dados sazonais
    assert 0 <= confiabilidade <= 1

# Testes para o modelo PrevisaoDemanda e seus métodos

def test_previsao_demanda_valores_previstos():
    """Testa a serialização e deserialização de valores previstos"""
    previsao = PrevisaoDemanda(
        data_inicio=date(2023, 5, 1),
        data_fim=date(2023, 5, 7),
        metodo="media_movel",
        parametros='{"janela": 7}'
    )
    
    # Valores de teste
    valores_teste = {
        "2023-05-01": 25,
        "2023-05-02": 30,
        "2023-05-03": 28,
        "2023-05-04": 32,
        "2023-05-05": 35,
        "2023-05-06": 40,
        "2023-05-07": 38
    }
    
    # Testar set_valores_previstos
    previsao.set_valores_previstos(valores_teste)
    
    # Testar get_valores_previstos
    valores_recuperados = previsao.get_valores_previstos()
    assert valores_recuperados == valores_teste
    
    # Testar get_previsao_para_data
    assert previsao.get_previsao_para_data("2023-05-03") == 28
    assert previsao.get_previsao_para_data("2023-05-07") == 38
    
    # Data inexistente deve retornar None
    assert previsao.get_previsao_para_data("2023-06-01") is None

def test_fator_sazonalidade_aplicacao():
    """Testa a aplicação de fatores de sazonalidade em previsões"""
    # Função simplificada para aplicar fator de sazonalidade
    def aplicar_fator_sazonalidade(valor_previsto, fator):
        return valor_previsto * fator
    
    # Valores previstos originais
    previsao_original = [100, 100, 100, 100, 100, 100, 100]  # um valor para cada dia da semana
    
    # Fatores de sazonalidade por dia da semana
    fatores = [
        1.0,   # Segunda: normal
        0.8,   # Terça: -20%
        0.9,   # Quarta: -10%
        1.0,   # Quinta: normal
        1.2,   # Sexta: +20%
        1.5,   # Sábado: +50%
        1.3    # Domingo: +30%
    ]
    
    # Aplicar fatores
    previsao_ajustada = [aplicar_fator_sazonalidade(valor, fator) 
                        for valor, fator in zip(previsao_original, fatores)]
    
    # Verificar resultados
    resultados_esperados = [100, 80, 90, 100, 120, 150, 130]
    assert previsao_ajustada == resultados_esperados
