import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.models.modelo_produto import Produto
from app.models.modelo_fornecedor import Fornecedor
from app.extensions import db

def test_criar_produto(session):
    """Testa a criação de um produto básico"""
    produto = Produto(
        nome="Arroz",
        unidade="kg",
        preco_unitario=Decimal("5.00"),
        estoque_minimo=10,
        estoque_atual=20
    )
    session.add(produto)
    session.commit()
    
    assert produto.id is not None
    assert produto.nome == "Arroz"
    assert produto.preco_unitario == Decimal("5.00")
    assert produto.estoque_atual == 20
    assert produto.ativo is True

def test_produto_com_fornecedor(session):
    """Testa a criação de um produto com fornecedor"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        cnpj="12345678901234",
        razao_social="Fornecedor Teste",
        nome_fantasia="Teste"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar produto
    produto = Produto(
        nome="Feijão",
        unidade="kg",
        preco_unitario=Decimal("8.00"),
        fornecedor_id=fornecedor.id
    )
    session.add(produto)
    session.commit()
    
    assert produto.fornecedor.id == fornecedor.id
    assert produto.fornecedor.razao_social == "Fornecedor Teste"

def test_calcular_valor_em_estoque(session):
    """Testa o cálculo do valor total em estoque"""
    produto = Produto(
        nome="Açúcar",
        unidade="kg",
        preco_unitario=Decimal("4.00"),
        estoque_atual=50
    )
    session.add(produto)
    session.commit()
    
    valor_estoque = produto.calcular_valor_em_estoque()
    assert valor_estoque == 200.00  # 50 * 4.00

def test_verificar_estoque_em_falta(session):
    """Testa a verificação de estoque em falta"""
    produto = Produto(
        nome="Sal",
        unidade="kg",
        preco_unitario=Decimal("2.00"),
        estoque_minimo=10,
        estoque_atual=5
    )
    session.add(produto)
    session.commit()
    
    assert produto.esta_em_falta() is True
    
    # Atualizar estoque
    produto.estoque_atual = 15
    assert produto.esta_em_falta() is False

def test_atualizar_estoque(session):
    """Testa a atualização de estoque"""
    produto = Produto(
        nome="Farinha",
        unidade="kg",
        preco_unitario=Decimal("3.00"),
        estoque_atual=100
    )
    session.add(produto)
    session.commit()
    
    # Testar entrada
    novo_estoque = produto.atualizar_estoque(50, "entrada")
    assert novo_estoque == 150
    
    # Testar saída
    novo_estoque = produto.atualizar_estoque(30, "saída")
    assert novo_estoque == 120
    
    # Testar saída com estoque insuficiente
    with pytest.raises(ValueError):
        produto.atualizar_estoque(200, "saída")

def test_produto_to_dict(session):
    """Testa a conversão do produto para dicionário"""
    produto = Produto(
        nome="Óleo",
        unidade="l",
        preco_unitario=Decimal("10.00"),
        estoque_minimo=5,
        estoque_atual=20,
        categoria="Óleos",
        marca="Teste"
    )
    session.add(produto)
    session.commit()
    
    produto_dict = produto.to_dict()
    assert produto_dict['nome'] == "Óleo"
    assert produto_dict['preco_unitario'] == 10.00
    assert produto_dict['estoque_atual'] == 20
    assert produto_dict['categoria'] == "Óleos"
    assert produto_dict['marca'] == "Teste"

def test_produto_constraints(session):
    """Testa as restrições do modelo de produto"""
    # Testar estoque negativo
    with pytest.raises(Exception):
        produto = Produto(
            nome="Teste",
            unidade="kg",
            preco_unitario=Decimal("5.00"),
            estoque_atual=-10
        )
        session.add(produto)
        session.commit()
    
    # Testar preço negativo
    with pytest.raises(Exception):
        produto = Produto(
            nome="Teste",
            unidade="kg",
            preco_unitario=Decimal("-5.00")
        )
        session.add(produto)
        session.commit()
    
    # Testar estoque mínimo negativo
    with pytest.raises(Exception):
        produto = Produto(
            nome="Teste",
            unidade="kg",
            preco_unitario=Decimal("5.00"),
            estoque_minimo=-5
        )
        session.add(produto)
        session.commit()

def test_produto_criacao():
    """Testa a criau00e7u00e3o bu00e1sica de um produto"""
    produto = Produto(
        codigo="P001",
        nome="Produto Teste",
        descricao="Descriu00e7u00e3o do produto de teste",
        unidade_medida="kg",
        preco_unitario=Decimal('15.90'),
        estoque_minimo=5.0,
        estoque_atual=10.0,
        ativo=True,
        categoria="Alimentos",
        marca="Marca Teste"
    )
    
    assert produto.codigo == "P001"
    assert produto.nome == "Produto Teste"
    assert produto.descricao == "Descriu00e7u00e3o do produto de teste"
    assert produto.unidade_medida == "kg"
    assert produto.preco_unitario == Decimal('15.90')
    assert produto.estoque_minimo == 5.0
    assert produto.estoque_atual == 10.0
    assert produto.ativo is True
    assert produto.categoria == "Alimentos"
    assert produto.marca == "Marca Teste"

def test_produto_calcular_valor_em_estoque():
    """Testa o cu00e1lculo do valor em estoque"""
    produto = Produto(
        nome="Produto Teste",
        unidade_medida="kg",
        preco_unitario=Decimal('15.90'),
        estoque_atual=10.0
    )
    
    # 15.90 * 10.0 = 159.0
    assert produto.calcular_valor_em_estoque() == 159.0
    
    # Testar com estoque zero
    produto.estoque_atual = 0.0
    assert produto.calcular_valor_em_estoque() == 0.0

def test_produto_esta_em_falta():
    """Testa a verificau00e7u00e3o de estoque em falta"""
    # Produto com estoque acima do mu00ednimo
    produto = Produto(
        nome="Produto Teste",
        unidade_medida="kg",
        estoque_minimo=5.0,
        estoque_atual=10.0
    )
    assert produto.esta_em_falta() is False
    
    # Produto com estoque igual ao mu00ednimo
    produto.estoque_atual = 5.0
    assert produto.esta_em_falta() is False
    
    # Produto com estoque abaixo do mu00ednimo
    produto.estoque_atual = 4.9
    assert produto.esta_em_falta() is True
    
    # Produto com estoque zero
    produto.estoque_atual = 0.0
    assert produto.esta_em_falta() is True

def test_produto_atualizar_estoque():
    """Testa a atualizau00e7u00e3o de estoque"""
    produto = Produto(
        nome="Produto Teste",
        unidade_medida="kg",
        estoque_atual=10.0
    )
    
    # Testar entrada de estoque
    produto.atualizar_estoque(5.0, "entrada")
    assert produto.estoque_atual == 15.0
    
    # Testar sau00edda de estoque
    produto.atualizar_estoque(3.0, "sau00edda")
    assert produto.estoque_atual == 12.0
    
    # Testar sau00edda maior que o estoque (nu00e3o deve permitir)
    with pytest.raises(ValueError):
        produto.atualizar_estoque(20.0, "sau00edda")
    assert produto.estoque_atual == 12.0  # Estoque nu00e3o deve mudar
    
    # Resetar para um valor conhecido
    produto.estoque_atual = 10.0
    
    # Testar novamente a entrada de estoque
    produto.atualizar_estoque(2.0, "entrada")
    assert produto.estoque_atual == 12.0

def test_produto_relacionamentos(session):
    """Testa os relacionamentos do modelo Produto"""
    # Criar mocks para os relacionamentos
    fornecedor = MagicMock()
    fornecedor.id = 1
    fornecedor.razao_social = "Fornecedor Teste"
    
    # Criar produto e associar com fornecedor
    produto = Produto(
        nome="Produto Teste",
        unidade_medida="kg",
        fornecedor_id=fornecedor.id
    )
    produto.fornecedor = fornecedor
    
    # Verificar relacionamento com fornecedor
    assert produto.fornecedor.id == 1
    assert produto.fornecedor.razao_social == "Fornecedor Teste"

def test_produto_repr():
    """Testa a representau00e7u00e3o em string do modelo"""
    produto = Produto(
        nome="Produto Teste",
        unidade_medida="kg"
    )
    expected = "<Produto Produto Teste (kg)>"
    assert repr(produto) == expected
