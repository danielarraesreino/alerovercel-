import pytest
from decimal import Decimal
from app.models.modelo_prato import Prato, PratoInsumo
from app.models.modelo_produto import Produto

def test_criar_prato(session):
    """Testa a criação de um prato básico"""
    prato = Prato(
        nome="Risoto de Cogumelos",
        descricao="Risoto cremoso com cogumelos frescos",
        categoria="Prato Principal",
        rendimento=4,
        unidade_rendimento="porções",
        tempo_preparo=30,
        preco_venda=Decimal("45.00"),
        margem=Decimal("30.00"),
        custo_indireto=Decimal("5.00")
    )
    session.add(prato)
    session.commit()
    
    assert prato.id is not None
    assert prato.nome == "Risoto de Cogumelos"
    assert prato.rendimento == 4
    assert prato.preco_venda == Decimal("45.00")
    assert prato.ativo is True

def test_prato_com_insumos(session):
    """Testa a criação de um prato com insumos"""
    # Criar produtos
    arroz = Produto(
        nome="Arroz Arbóreo",
        unidade="kg",
        preco_unitario=Decimal("15.00")
    )
    cogumelos = Produto(
        nome="Cogumelos",
        unidade="kg",
        preco_unitario=Decimal("40.00")
    )
    session.add_all([arroz, cogumelos])
    session.commit()
    
    # Criar prato
    prato = Prato(
        nome="Risoto",
        rendimento=4,
        unidade_rendimento="porções"
    )
    session.add(prato)
    session.commit()
    
    # Adicionar insumos
    insumo1 = PratoInsumo(
        prato_id=prato.id,
        produto_id=arroz.id,
        quantidade=0.5,
        ordem=1
    )
    insumo2 = PratoInsumo(
        prato_id=prato.id,
        produto_id=cogumelos.id,
        quantidade=0.3,
        ordem=2
    )
    session.add_all([insumo1, insumo2])
    session.commit()
    
    assert len(prato.insumos) == 2
    assert prato.insumos[0].produto.nome == "Arroz Arbóreo"
    assert prato.insumos[1].produto.nome == "Cogumelos"

def test_calcular_custos_prato(session):
    """Testa o cálculo de custos do prato"""
    # Criar produtos
    arroz = Produto(
        nome="Arroz",
        unidade="kg",
        preco_unitario=Decimal("10.00")
    )
    frango = Produto(
        nome="Frango",
        unidade="kg",
        preco_unitario=Decimal("15.00")
    )
    session.add_all([arroz, frango])
    session.commit()
    
    # Criar prato
    prato = Prato(
        nome="Arroz com Frango",
        rendimento=4,
        unidade_rendimento="porções",
        custo_indireto=Decimal("5.00")
    )
    session.add(prato)
    session.commit()
    
    # Adicionar insumos
    insumo1 = PratoInsumo(
        prato_id=prato.id,
        produto_id=arroz.id,
        quantidade=0.5,
        ordem=1
    )
    insumo2 = PratoInsumo(
        prato_id=prato.id,
        produto_id=frango.id,
        quantidade=0.3,
        ordem=2
    )
    session.add_all([insumo1, insumo2])
    session.commit()
    
    # Verificar cálculos
    assert prato.custo_direto_total == Decimal("9.50")  # (0.5 * 10) + (0.3 * 15)
    assert prato.custo_direto_por_porcao == Decimal("2.375")  # 9.50 / 4
    assert prato.custo_total_por_porcao == Decimal("7.375")  # 2.375 + 5.00

def test_calcular_preco_sugerido(session):
    """Testa o cálculo do preço sugerido"""
    prato = Prato(
        nome="Teste",
        rendimento=2,
        unidade_rendimento="porções",
        custo_direto_total=Decimal("20.00"),
        custo_indireto=Decimal("10.00"),
        margem=Decimal("30.00")
    )
    
    preco_sugerido = prato.calcular_preco_sugerido()
    assert preco_sugerido == Decimal("39.00")  # (15 + 10) * 1.3

def test_atualizar_preco_sugerido(session):
    """Testa a atualização do preço sugerido"""
    prato = Prato(
        nome="Teste",
        rendimento=2,
        unidade_rendimento="porções",
        custo_direto_total=Decimal("20.00"),
        custo_indireto=Decimal("10.00"),
        margem=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    preco_atualizado = prato.atualizar_preco_sugerido()
    assert preco_atualizado == Decimal("39.00")
    assert prato.preco_venda == Decimal("39.00")

def test_prato_constraints(session):
    """Testa as restrições do modelo de prato"""
    # Testar rendimento negativo
    with pytest.raises(Exception):
        prato = Prato(
            nome="Teste",
            rendimento=-2,
            unidade_rendimento="porções"
        )
        session.add(prato)
        session.commit()
    
    # Testar margem negativa
    with pytest.raises(Exception):
        prato = Prato(
            nome="Teste",
            rendimento=2,
            unidade_rendimento="porções",
            margem=Decimal("-10.00")
        )
        session.add(prato)
        session.commit()
    
    # Testar preço de venda negativo
    with pytest.raises(Exception):
        prato = Prato(
            nome="Teste",
            rendimento=2,
            unidade_rendimento="porções",
            preco_venda=Decimal("-10.00")
        )
        session.add(prato)
        session.commit()

def test_prato_to_dict(session):
    """Testa a conversão do prato para dicionário"""
    prato = Prato(
        nome="Teste",
        descricao="Descrição teste",
        categoria="Categoria Teste",
        rendimento=4,
        unidade_rendimento="porções",
        tempo_preparo=30,
        preco_venda=Decimal("40.00"),
        margem=Decimal("30.00"),
        custo_indireto=Decimal("5.00")
    )
    session.add(prato)
    session.commit()
    
    prato_dict = prato.to_dict()
    assert prato_dict['nome'] == "Teste"
    assert prato_dict['descricao'] == "Descrição teste"
    assert prato_dict['categoria'] == "Categoria Teste"
    assert prato_dict['rendimento'] == 4
    assert prato_dict['preco_venda'] == 40.00
    assert prato_dict['margem'] == 30.00
    assert prato_dict['custo_indireto'] == 5.00 