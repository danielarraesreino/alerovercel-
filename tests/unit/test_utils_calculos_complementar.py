import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta

from app.utils.calculos import (
    calcular_custo_direto_prato,
    calcular_custo_por_porcao,
    calcular_preco_venda,
    calcular_margem_atual,
    calcular_rateio_custos_indiretos,
    calcular_custos_indiretos_periodo,
    calcular_total_dias_mes,
    calcular_validade_por_periodo,
    calcular_estoque_minimo
)

# Testes para calcular_custo_direto_prato
def test_calcular_custo_direto_prato():
    """Testa o cu00e1lculo de custo direto de um prato"""
    # Caso com insumos obrigatu00f3rios e opcionais
    insumos = [
        {'quantidade': 1, 'preco_unitario': 10.0, 'obrigatorio': True},
        {'quantidade': 2, 'preco_unitario': 5.0, 'obrigatorio': True},
        {'quantidade': 0.5, 'preco_unitario': 8.0, 'obrigatorio': False}
    ]
    
    custo_total, custo_obrigatorios, custo_opcionais = calcular_custo_direto_prato(insumos)
    assert custo_total == 24.0  # 10 + (2*5) + (0.5*8)
    assert custo_obrigatorios == 20.0  # 10 + (2*5)
    assert custo_opcionais == 4.0  # 0.5*8
    
    # Caso com lista vazia
    custo_total, custo_obrigatorios, custo_opcionais = calcular_custo_direto_prato([])
    assert custo_total == 0.0
    assert custo_obrigatorios == 0.0
    assert custo_opcionais == 0.0
    
    # Caso com insumos sem o campo obrigatorio (assume true por padru00e3o)
    insumos_simples = [
        {'quantidade': 3, 'preco_unitario': 7.0}
    ]
    
    custo_total, custo_obrigatorios, custo_opcionais = calcular_custo_direto_prato(insumos_simples)
    assert custo_total == 21.0  # 3*7
    assert custo_obrigatorios == 21.0
    assert custo_opcionais == 0.0

# Testes para calcular_custo_por_porcao
def test_calcular_custo_por_porcao():
    """Testa o cu00e1lculo de custo por poru00e7u00e3o"""
    # Caso normal
    assert calcular_custo_por_porcao(30.0, 5) == 6.0
    
    # Caso com rendimento zero
    assert calcular_custo_por_porcao(30.0, 0) == 0.0
    
    # Caso com rendimento negativo
    assert calcular_custo_por_porcao(30.0, -1) == 0.0
    
    # Caso com custo zero
    assert calcular_custo_por_porcao(0.0, 5) == 0.0

# Testes para calcular_preco_venda
def test_calcular_preco_venda():
    """Testa o cu00e1lculo de preu00e7o de venda baseado no custo e margem"""
    # Casos normais
    assert calcular_preco_venda(100.0, 30) == 130.0  # 30% de margem
    assert calcular_preco_venda(50.0, 20) == 60.0   # 20% de margem
    
    # Caso com margem zero
    assert calcular_preco_venda(100.0, 0) == 100.0
    
    # Caso com margem negativa (situau00e7u00e3o incomum mas possiu00edvel)
    assert calcular_preco_venda(100.0, -10) == 90.0
    
    # Caso com custo zero
    assert calcular_preco_venda(0.0, 50) == 0.0

# Testes para calcular_margem_atual
def test_calcular_margem_atual():
    """Testa o cu00e1lculo de margem atual com base no preu00e7o e custo"""
    # Casos normais
    assert calcular_margem_atual(130.0, 100.0) == 30.0  # 30% de margem
    assert calcular_margem_atual(60.0, 50.0) == 20.0    # 20% de margem
    
    # Caso com preu00e7o igual ao custo
    assert calcular_margem_atual(100.0, 100.0) == 0.0
    
    # Caso com preu00e7o menor que o custo (prejuu00edzo)
    assert calcular_margem_atual(90.0, 100.0) == -10.0
    
    # Casos invru00e1lidos
    assert calcular_margem_atual(0.0, 100.0) == 0.0
    assert calcular_margem_atual(100.0, 0.0) == 0.0
    assert calcular_margem_atual(0.0, 0.0) == 0.0

# Testes para calcular_rateio_custos_indiretos
def test_calcular_rateio_custos_indiretos():
    """Testa o rateio de custos indiretos entre produtos/pratos"""
    # Caso normal
    criterio_rateio = {
        '1': {'peso': 50},
        '2': {'peso': 30},
        '3': {'peso': 20}
    }
    
    rateio = calcular_rateio_custos_indiretos(1000.0, criterio_rateio)
    assert len(rateio) == 3
    assert rateio['1'] == 500.0  # 50% de 1000
    assert rateio['2'] == 300.0  # 30% de 1000
    assert rateio['3'] == 200.0  # 20% de 1000
    
    # Caso com pesos iguais
    criterio_iguais = {
        'A': {'peso': 1},
        'B': {'peso': 1},
        'C': {'peso': 1}
    }
    
    rateio_iguais = calcular_rateio_custos_indiretos(300.0, criterio_iguais)
    assert len(rateio_iguais) == 3
    assert rateio_iguais['A'] == 100.0
    assert rateio_iguais['B'] == 100.0
    assert rateio_iguais['C'] == 100.0
    
    # Caso com lista vazia
    assert calcular_rateio_custos_indiretos(1000.0, {}) == {}
    
    # Caso com pesos zeros
    criterio_zeros = {
        'X': {'peso': 0},
        'Y': {'peso': 0}
    }
    
    assert calcular_rateio_custos_indiretos(1000.0, criterio_zeros) == {}

# Testes para calcular_custos_indiretos_periodo
def test_calcular_custos_indiretos_periodo():
    """Testa o cu00e1lculo de custos indiretos em um peru00edodo"""
    # Dados de teste
    data_inicio = date(2023, 3, 1)
    data_fim = date(2023, 3, 31)
    
    # Custos por tipo
    custos_por_tipo = {
        'aluguel': [
            {'valor': 2000.0, 'periodicidade': 'mensal'}
        ],
        'energia': [
            {'valor': 300.0, 'periodicidade': 'mensal'}
        ],
        'agua': [
            {'valor': 10.0, 'periodicidade': 'diaria'}
        ],
        'servicos': [
            {'valor': 500.0, 'periodicidade': 'semanal'}
        ]
    }
    
    custos = calcular_custos_indiretos_periodo(data_inicio, data_fim, custos_por_tipo)
    
    # Verificau00e7u00f5es
    assert len(custos) == 4  # Quatro tipos de custo
    assert custos['aluguel'] == 2000.0  # Mensal (1 mu00eas)
    assert custos['energia'] == 300.0   # Mensal (1 mu00eas)
    assert custos['agua'] == 310.0      # Diu00e1ria (31 dias * 10)
    # A quantidade de semanas em maru00e7o de 2023 u00e9 aproximadamente 4.43 semanas
    # (31 dias / 7 dias por semana = 4.43)
    assert custos['servicos'] > 2000.0 and custos['servicos'] < 2500.0  # ~4.43 semanas * 500
    
    # Caso com peru00edodo mais curto
    data_inicio_curto = date(2023, 3, 15)
    data_fim_curto = date(2023, 3, 20)
    
    custos_curto = calcular_custos_indiretos_periodo(data_inicio_curto, data_fim_curto, custos_por_tipo)
    
    # Verificau00e7u00f5es para peru00edodo mais curto
    assert len(custos_curto) == 4
    # Para peru00edodo parcial, os custos mensais su00e3o proporcionais
    # 6 dias / 31 dias = ~0.194 do mu00eas
    assert custos_curto['aluguel'] < 2000.0
    assert custos_curto['energia'] < 300.0
    assert custos_curto['agua'] == 60.0  # 6 dias * 10

# Testes para calcular_total_dias_mes
def test_calcular_total_dias_mes():
    """Testa o cu00e1lculo do total de dias em um mu00eas"""
    # Casos normais
    assert calcular_total_dias_mes(1, 2023) == 31  # Janeiro
    assert calcular_total_dias_mes(4, 2023) == 30  # Abril
    assert calcular_total_dias_mes(2, 2023) == 28  # Fevereiro em ano nu00e3o bissexto
    assert calcular_total_dias_mes(2, 2024) == 29  # Fevereiro em ano bissexto
    
    # Casos limites
    assert calcular_total_dias_mes(12, 2023) == 31  # Dezembro
    
    # Casos invru00e1lidos (mu00eas fora do intervalo 1-12)
    with pytest.raises(ValueError):
        calcular_total_dias_mes(13, 2023)
    
    with pytest.raises(ValueError):
        calcular_total_dias_mes(0, 2023)

# Testes para calcular_validade_por_periodo
def test_calcular_validade_por_periodo():
    """Testa o cu00e1lculo da data de validade"""
    # Caso normal
    data_producao = date(2023, 5, 15)
    assert calcular_validade_por_periodo(data_producao, 5) == date(2023, 5, 20)
    
    # Caso com mudanu00e7a de mu00eas
    assert calcular_validade_por_periodo(data_producao, 20) == date(2023, 6, 4)
    
    # Caso com mudanu00e7a de ano
    data_fim_ano = date(2023, 12, 25)
    assert calcular_validade_por_periodo(data_fim_ano, 10) == date(2024, 1, 4)
    
    # Caso com dias de validade zero ou negativo
    assert calcular_validade_por_periodo(data_producao, 0) == data_producao
    assert calcular_validade_por_periodo(data_producao, -5) == data_producao

# Testes para calcular_estoque_minimo
def test_calcular_estoque_minimo():
    """Testa o cu00e1lculo do estoque mu00ednimo recomendado"""
    # Caso normal
    assert calcular_estoque_minimo(10.0, 3, 0.5) == 45.0  # 10*3*(1+0.5)
    
    # Caso sem estoque de seguranu00e7a
    assert calcular_estoque_minimo(10.0, 3, 0.0) == 30.0  # 10*3
    
    # Caso com consumo zero
    assert calcular_estoque_minimo(0.0, 5, 0.5) == 0.0
    
    # Caso com tempo de reposiu00e7u00e3o zero
    assert calcular_estoque_minimo(10.0, 0, 0.5) == 0.0
    
    # Caso com valores negativos (incomum, mas devemos tratar)
    assert calcular_estoque_minimo(-5.0, 3, 0.5) == 0.0
    assert calcular_estoque_minimo(10.0, -2, 0.5) == 0.0
    assert calcular_estoque_minimo(10.0, 3, -0.2) == 24.0  # 10*3*(1-0.2)
