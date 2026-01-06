import pytest
from decimal import Decimal
from datetime import datetime, date
from app.models.modelo_custo import CustoIndireto
from app.models.modelo_prato import Prato

def test_criar_custo_indireto(session):
    """Testa a criação de um custo indireto"""
    custo = CustoIndireto(
        descricao="Aluguel",
        valor=Decimal("5000.00"),
        data_referencia=date.today(),
        tipo="Aluguel",
        recorrente=True
    )
    session.add(custo)
    session.commit()
    
    assert custo.id is not None
    assert custo.descricao == "Aluguel"
    assert custo.valor == Decimal("5000.00")
    assert custo.recorrente is True

def test_get_total_por_periodo(session):
    """Testa o cálculo do total de custos por período"""
    # Criar custos para diferentes meses
    custo1 = CustoIndireto(
        descricao="Aluguel Jan",
        valor=Decimal("5000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Aluguel"
    )
    custo2 = CustoIndireto(
        descricao="Aluguel Fev",
        valor=Decimal("5000.00"),
        data_referencia=date(2024, 2, 1),
        tipo="Aluguel"
    )
    custo3 = CustoIndireto(
        descricao="Energia Jan",
        valor=Decimal("1000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Energia"
    )
    session.add_all([custo1, custo2, custo3])
    session.commit()
    
    # Calcular total para janeiro
    total_jan = CustoIndireto.get_total_por_periodo(
        date(2024, 1, 1),
        date(2024, 1, 31)
    )
    assert total_jan == 6000.00  # 5000 + 1000
    
    # Calcular total para fevereiro
    total_fev = CustoIndireto.get_total_por_periodo(
        date(2024, 2, 1),
        date(2024, 2, 29)
    )
    assert total_fev == 5000.00

def test_calcular_rateio_por_prato(session):
    """Testa o cálculo do rateio por prato"""
    # Criar custos para o mês
    custo1 = CustoIndireto(
        descricao="Aluguel",
        valor=Decimal("5000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Aluguel"
    )
    custo2 = CustoIndireto(
        descricao="Energia",
        valor=Decimal("1000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Energia"
    )
    session.add_all([custo1, custo2])
    session.commit()
    
    # Calcular rateio para 1000 pratos
    valor_rateio = CustoIndireto.calcular_rateio_por_prato(
        date(2024, 1, 1),
        1000
    )
    assert valor_rateio == 6.00  # (5000 + 1000) / 1000

def test_atualizar_rateio_pratos(session):
    """Testa a atualização do rateio em todos os pratos"""
    # Criar custos
    custo = CustoIndireto(
        descricao="Aluguel",
        valor=Decimal("5000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Aluguel"
    )
    session.add(custo)
    session.commit()
    
    # Criar pratos
    prato1 = Prato(
        nome="Prato 1",
        rendimento=2,
        unidade_rendimento="porções"
    )
    prato2 = Prato(
        nome="Prato 2",
        rendimento=2,
        unidade_rendimento="porções"
    )
    session.add_all([prato1, prato2])
    session.commit()
    
    # Atualizar rateio
    num_pratos, valor_rateio = CustoIndireto.atualizar_rateio_pratos(
        date(2024, 1, 1),
        1000
    )
    
    assert num_pratos == 2
    assert valor_rateio == 5.00  # 5000 / 1000
    
    # Verificar se os pratos foram atualizados
    session.refresh(prato1)
    session.refresh(prato2)
    assert prato1.custo_indireto == Decimal("5.00")
    assert prato2.custo_indireto == Decimal("5.00")

def test_custo_indireto_to_dict(session):
    """Testa a conversão do custo indireto para dicionário"""
    custo = CustoIndireto(
        descricao="Teste",
        valor=Decimal("1000.00"),
        data_referencia=date.today(),
        tipo="Teste",
        recorrente=True,
        observacao="Observação teste"
    )
    session.add(custo)
    session.commit()
    
    custo_dict = custo.to_dict()
    assert custo_dict['descricao'] == "Teste"
    assert custo_dict['valor'] == 1000.00
    assert custo_dict['tipo'] == "Teste"
    assert custo_dict['recorrente'] is True
    assert custo_dict['observacao'] == "Observação teste"

def test_custo_indireto_constraints(session):
    """Testa as restrições do modelo de custo indireto"""
    # Testar valor negativo
    with pytest.raises(Exception):
        custo = CustoIndireto(
            descricao="Teste",
            valor=Decimal("-1000.00"),
            data_referencia=date.today()
        )
        session.add(custo)
        session.commit()

def test_calcular_rateio_sem_producao(session):
    """Testa o cálculo de rateio quando não há produção"""
    # Criar custo
    custo = CustoIndireto(
        descricao="Aluguel",
        valor=Decimal("5000.00"),
        data_referencia=date(2024, 1, 1),
        tipo="Aluguel"
    )
    session.add(custo)
    session.commit()
    
    # Calcular rateio com produção zero
    valor_rateio = CustoIndireto.calcular_rateio_por_prato(
        date(2024, 1, 1),
        0
    )
    assert valor_rateio == 0  # Deve retornar 0 quando não há produção 