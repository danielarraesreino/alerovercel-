import pytest
from datetime import datetime, date, timedelta
from app.utils.calculos import (
    calcular_preco_medio_ponderado,
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

# Testes para calcular_preco_medio_ponderado
@pytest.mark.parametrize("estoque_atual, preco_atual, quantidade_nova, preco_novo, esperado", [
    (10.0, 5.0, 5.0, 10.0, 6.6667),         # Caso normal
    (0.0, 0.0, 10.0, 5.0, 5.0),               # Estoque inicial vazio
    (10.0, 5.0, 0.0, 0.0, 5.0),               # Sem compra nova
    (0.0, 0.0, 0.0, 0.0, 0.0),                # Ambos vazios
    (10.0, 5.0, -5.0, 0.0, 10.0),             # Remoção de estoque (comportamento real)
    (5.0, 10.0, 5.0, 20.0, 15.0)              # Caso com preço crescente
])
def test_calcular_preco_medio_ponderado(estoque_atual, preco_atual, quantidade_nova, preco_novo, esperado):
    resultado = calcular_preco_medio_ponderado(estoque_atual, preco_atual, quantidade_nova, preco_novo)
    assert round(resultado, 4) == esperado

# Testes para calcular_custo_direto_prato
@pytest.mark.parametrize("insumos, esperado", [
    # Lista vazia
    ([], (0.0, 0.0, 0.0)),
    # Um insumo obrigatório
    ([{'quantidade': 2.0, 'preco_unitario': 5.0, 'obrigatorio': True}], (10.0, 10.0, 0.0)),
    # Um insumo opcional
    ([{'quantidade': 2.0, 'preco_unitario': 5.0, 'obrigatorio': False}], (10.0, 0.0, 10.0)),
    # Múltiplos insumos mistos
    ([
        {'quantidade': 2.0, 'preco_unitario': 5.0, 'obrigatorio': True},
        {'quantidade': 1.0, 'preco_unitario': 10.0, 'obrigatorio': False},
        {'quantidade': 3.0, 'preco_unitario': 3.0, 'obrigatorio': True}
    ], (29.0, 19.0, 10.0)),
    # Caso com valores faltantes (deveria usar defaults)
    ([{'quantidade': 2.0}], (0.0, 0.0, 0.0))
])
def test_calcular_custo_direto_prato(insumos, esperado):
    resultado = calcular_custo_direto_prato(insumos)
    assert resultado == esperado

# Testes para calcular_custo_por_porcao
@pytest.mark.parametrize("custo_total, rendimento, esperado", [
    (100.0, 10.0, 10.0),   # Caso normal
    (100.0, 0.0, 0.0),       # Rendimento zero
    (0.0, 10.0, 0.0),        # Custo zero
    (0.0, 0.0, 0.0)          # Ambos zero
])
def test_calcular_custo_por_porcao(custo_total, rendimento, esperado):
    resultado = calcular_custo_por_porcao(custo_total, rendimento)
    assert resultado == esperado

# Testes para calcular_preco_venda
@pytest.mark.parametrize("custo_total, margem, esperado", [
    (100.0, 30.0, 130.0),   # 30% de margem
    (100.0, 0.0, 100.0),      # Sem margem
    (0.0, 30.0, 0.0),         # Custo zero
    (100.0, 100.0, 200.0)     # 100% de margem
])
def test_calcular_preco_venda(custo_total, margem, esperado):
    resultado = calcular_preco_venda(custo_total, margem)
    assert resultado == esperado

# Testes para calcular_margem_atual
@pytest.mark.parametrize("preco_venda, custo_total, esperado", [
    (130.0, 100.0, 30.0),    # Caso normal
    (100.0, 100.0, 0.0),       # Sem margem
    (0.0, 100.0, 0.0),         # Preço zero (tratamento de erro)
    (100.0, 0.0, 0.0),         # Custo zero (tratamento de erro)
    (200.0, 100.0, 100.0)      # 100% de margem
])
def test_calcular_margem_atual(preco_venda, custo_total, esperado):
    resultado = calcular_margem_atual(preco_venda, custo_total)
    assert resultado == esperado

# Testes para calcular_rateio_custos_indiretos
def test_calcular_rateio_custos_indiretos():
    # Caso normal
    criterio_rateio = {
        1: {'peso': 50},
        2: {'peso': 30},
        3: {'peso': 20}
    }
    resultado = calcular_rateio_custos_indiretos(1000.0, criterio_rateio)
    
    assert len(resultado) == 3
    assert resultado[1]['valor_rateio'] == 500.0
    assert resultado[2]['valor_rateio'] == 300.0
    assert resultado[3]['valor_rateio'] == 200.0
    
    # Caso com peso zero
    criterio_vazio = {}
    resultado_vazio = calcular_rateio_custos_indiretos(1000.0, criterio_vazio)
    assert resultado_vazio == {}
    
    # Caso com pesos negativos
    criterio_negativo = {1: {'peso': -10}, 2: {'peso': -10}}
    resultado_negativo = calcular_rateio_custos_indiretos(1000.0, criterio_negativo)
    assert resultado_negativo == {}

# Testes para calcular_custos_indiretos_periodo
def test_calcular_custos_indiretos_periodo():
    # Prepara datas
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    
    # Dados de exemplo
    custos_por_tipo = {
        'aluguel': [
            {'data': hoje, 'valor': 1000.0},
            {'data': amanha, 'valor': 1000.0}
        ],
        'energia': [
            {'data': ontem, 'valor': 500.0},
            {'data': hoje, 'valor': 600.0}
        ]
    }
    
    # Teste dentro do período (só hoje)
    resultado = calcular_custos_indiretos_periodo(hoje, hoje, custos_por_tipo)
    assert resultado['aluguel'] == 1000.0
    assert resultado['energia'] == 600.0
    assert resultado['total'] == 1600.0
    
    # Teste com período mais amplo
    resultado_amplo = calcular_custos_indiretos_periodo(ontem, amanha, custos_por_tipo)
    assert resultado_amplo['aluguel'] == 2000.0
    assert resultado_amplo['energia'] == 1100.0
    assert resultado_amplo['total'] == 3100.0
    
    # Teste com período sem dados
    data_futura = hoje + timedelta(days=10)
    resultado_vazio = calcular_custos_indiretos_periodo(data_futura, data_futura, custos_por_tipo)
    assert resultado_vazio['aluguel'] == 0.0
    assert resultado_vazio['energia'] == 0.0
    assert resultado_vazio['total'] == 0.0

# Testes para calcular_total_dias_mes
@pytest.mark.parametrize("mes, ano, esperado", [
    (1, 2025, 31),    # Janeiro
    (2, 2024, 29),     # Fevereiro em ano bissexto
    (2, 2025, 28),     # Fevereiro em ano normal
    (4, 2025, 30),     # Abril
    (12, 2025, 31)     # Dezembro
])
def test_calcular_total_dias_mes(mes, ano, esperado):
    resultado = calcular_total_dias_mes(mes, ano)
    assert resultado == esperado

# Testes para calcular_validade_por_periodo
def test_calcular_validade_por_periodo():
    data_base = date(2025, 1, 1)
    resultado = calcular_validade_por_periodo(data_base, 30)
    assert resultado == date(2025, 1, 31)
    
    # Teste com zero dias
    resultado_zero = calcular_validade_por_periodo(data_base, 0)
    assert resultado_zero == data_base
    
    # Teste com dias negativos (menos comum, mas vale testar)
    resultado_negativo = calcular_validade_por_periodo(data_base, -5)
    assert resultado_negativo == date(2024, 12, 27)

# Testes para calcular_estoque_minimo
@pytest.mark.parametrize("consumo_medio, tempo_reposicao, estoque_seguranca, esperado", [
    (10.0, 5, 0.5, 75.0),     # Caso normal com 50% de segurança
    (10.0, 5, 0.0, 50.0),      # Sem estoque de segurança
    (0.0, 5, 0.5, 0.0),        # Sem consumo
    (10.0, 0, 0.5, 0.0),       # Sem tempo de reposição
    (10.0, 5, 1.0, 100.0)      # 100% de segurança
])
def test_calcular_estoque_minimo(consumo_medio, tempo_reposicao, estoque_seguranca, esperado):
    resultado = calcular_estoque_minimo(consumo_medio, tempo_reposicao, estoque_seguranca)
    assert resultado == esperado
