import pytest
from decimal import Decimal
from datetime import datetime, date
from app.models.modelo_pedido import Pedido, PedidoItem
from app.models.modelo_prato import Prato
from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem

def test_criar_pedido(session):
    """Testa a criação de um pedido básico"""
    pedido = Pedido(
        numero_mesa=1,
        status="aberto",
        observacoes="Sem cebola"
    )
    session.add(pedido)
    session.commit()
    
    assert pedido.id is not None
    assert pedido.numero_mesa == 1
    assert pedido.status == "aberto"
    assert pedido.observacoes == "Sem cebola"
    assert pedido.data_hora is not None
    assert pedido.valor_total == Decimal("0.00")

def test_pedido_com_itens(session):
    """Testa a criação de um pedido com itens"""
    # Criar pratos
    prato1 = Prato(
        nome="Salada",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("25.00")
    )
    prato2 = Prato(
        nome="Filé",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("45.00")
    )
    session.add_all([prato1, prato2])
    session.commit()
    
    # Criar pedido
    pedido = Pedido(
        numero_mesa=1,
        status="aberto"
    )
    session.add(pedido)
    session.commit()
    
    # Adicionar itens
    item1 = PedidoItem(
        pedido_id=pedido.id,
        prato_id=prato1.id,
        quantidade=2,
        preco_unitario=prato1.preco_venda
    )
    item2 = PedidoItem(
        pedido_id=pedido.id,
        prato_id=prato2.id,
        quantidade=1,
        preco_unitario=prato2.preco_venda
    )
    session.add_all([item1, item2])
    session.commit()
    
    assert len(pedido.itens) == 2
    assert pedido.valor_total == Decimal("95.00")  # (2 * 25) + 45
    assert pedido.itens[0].prato.nome == "Salada"
    assert pedido.itens[1].prato.nome == "Filé"

def test_pedido_com_cardapio(session):
    """Testa a criação de um pedido com itens do cardápio"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar cardápio com seção e item
    cardapio = Cardapio(
        nome="Cardápio Teste",
        data_inicio=date.today()
    )
    session.add(cardapio)
    session.commit()
    
    secao = CardapioSecao(
        cardapio_id=cardapio.id,
        nome="Pratos",
        ordem=1
    )
    session.add(secao)
    session.commit()
    
    cardapio_item = CardapioItem(
        secao_id=secao.id,
        prato_id=prato.id,
        ordem=1,
        preco_venda=Decimal("35.00")  # Preço específico no cardápio
    )
    session.add(cardapio_item)
    session.commit()
    
    # Criar pedido
    pedido = Pedido(
        numero_mesa=1,
        status="aberto",
        cardapio_id=cardapio.id
    )
    session.add(pedido)
    session.commit()
    
    # Adicionar item do cardápio
    item = PedidoItem(
        pedido_id=pedido.id,
        prato_id=prato.id,
        quantidade=1,
        preco_unitario=cardapio_item.preco_venda
    )
    session.add(item)
    session.commit()
    
    assert pedido.valor_total == Decimal("35.00")  # Usa o preço do cardápio
    assert pedido.itens[0].preco_unitario == Decimal("35.00")

def test_atualizar_status_pedido(session):
    """Testa a atualização do status do pedido"""
    pedido = Pedido(
        numero_mesa=1,
        status="aberto"
    )
    session.add(pedido)
    session.commit()
    
    pedido.status = "em_preparo"
    session.commit()
    
    assert pedido.status == "em_preparo"
    assert pedido.data_hora_atualizacao is not None

def test_calcular_tempo_espera(session):
    """Testa o cálculo do tempo de espera do pedido"""
    pedido = Pedido(
        numero_mesa=1,
        status="aberto"
    )
    session.add(pedido)
    session.commit()
    
    # Simular passagem de tempo
    pedido.data_hora = datetime.now() - timedelta(minutes=30)
    session.commit()
    
    assert pedido.tempo_espera_minutos == 30

def test_pedido_to_dict(session):
    """Testa a conversão do pedido para dicionário"""
    pedido = Pedido(
        numero_mesa=1,
        status="aberto",
        observacoes="Teste"
    )
    session.add(pedido)
    session.commit()
    
    pedido_dict = pedido.to_dict()
    assert pedido_dict['numero_mesa'] == 1
    assert pedido_dict['status'] == "aberto"
    assert pedido_dict['observacoes'] == "Teste"
    assert pedido_dict['valor_total'] == 0.00
    assert pedido_dict['itens'] == []

def test_item_to_dict(session):
    """Testa a conversão do item do pedido para dicionário"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar pedido
    pedido = Pedido(
        numero_mesa=1,
        status="aberto"
    )
    session.add(pedido)
    session.commit()
    
    # Criar item
    item = PedidoItem(
        pedido_id=pedido.id,
        prato_id=prato.id,
        quantidade=2,
        preco_unitario=Decimal("30.00"),
        observacoes="Sem cebola"
    )
    session.add(item)
    session.commit()
    
    item_dict = item.to_dict()
    assert item_dict['quantidade'] == 2
    assert item_dict['preco_unitario'] == 30.00
    assert item_dict['observacoes'] == "Sem cebola"
    assert item_dict['prato']['nome'] == "Prato Teste"
    assert item_dict['valor_total'] == 60.00  # 2 * 30.00

def test_pedido_constraints(session):
    """Testa as restrições do pedido"""
    # Teste de número de mesa negativo
    with pytest.raises(ValueError):
        pedido = Pedido(
            numero_mesa=-1,
            status="aberto"
        )
        session.add(pedido)
        session.commit()
    
    # Teste de status inválido
    with pytest.raises(ValueError):
        pedido = Pedido(
            numero_mesa=1,
            status="status_invalido"
        )
        session.add(pedido)
        session.commit()

def test_item_constraints(session):
    """Testa as restrições do item do pedido"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar pedido
    pedido = Pedido(
        numero_mesa=1,
        status="aberto"
    )
    session.add(pedido)
    session.commit()
    
    # Teste de quantidade negativa
    with pytest.raises(ValueError):
        item = PedidoItem(
            pedido_id=pedido.id,
            prato_id=prato.id,
            quantidade=-1,
            preco_unitario=Decimal("30.00")
        )
        session.add(item)
        session.commit()
    
    # Teste de preço unitário negativo
    with pytest.raises(ValueError):
        item = PedidoItem(
            pedido_id=pedido.id,
            prato_id=prato.id,
            quantidade=1,
            preco_unitario=Decimal("-30.00")
        )
        session.add(item)
        session.commit() 