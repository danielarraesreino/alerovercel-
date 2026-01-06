import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem
from app.models.modelo_prato import Prato
from app.extensions import db

@pytest.fixture
def mock_cardapio():
    """Mock para um cardápio"""
    cardapio = Cardapio(
        id=1,
        nome="Cardápio de Teste",
        descricao="Descrição de teste",
        data_inicio=date(2023, 5, 1),
        data_fim=date(2023, 5, 31),
        ativo=True,
        tipo="semanal",
        temporada="primavera"
    )
    cardapio.secoes = []
    return cardapio

@pytest.fixture
def mock_cardapio_secao(mock_cardapio):
    """Mock para uma seção de cardápio"""
    secao = CardapioSecao(
        id=1,
        cardapio_id=mock_cardapio.id,
        nome="Entradas",
        descricao="Seção de entradas",
        ordem=1
    )
    secao.cardapio = mock_cardapio
    secao.itens = []
    mock_cardapio.secoes.append(secao)
    return secao

@pytest.fixture
def mock_prato():
    """Mock para um prato"""
    prato = MagicMock()
    prato.id = 1
    prato.nome = "Prato de Teste"
    prato.descricao = "Descrição do prato de teste"
    prato.categoria = "entrada"
    prato.preco_venda = Decimal('25.90')
    prato.custo_total = Decimal('10.00')
    return prato

@pytest.fixture
def mock_cardapio_item(mock_cardapio_secao, mock_prato):
    """Mock para um item de cardápio"""
    item = CardapioItem(
        id=1,
        secao_id=mock_cardapio_secao.id,
        prato_id=mock_prato.id,
        ordem=1,
        preco_venda=Decimal('28.90'),  # Preço personalizado para o cardápio
        destaque=True,
        disponivel=True,
        observacao="Item de teste"
    )
    item.secao = mock_cardapio_secao
    item.prato = mock_prato
    mock_cardapio_secao.itens.append(item)
    return item

def test_cardapio_criacao():
    """Testa a criação básica de um cardápio"""
    cardapio = Cardapio(
        nome="Cardápio de Teste",
        descricao="Descrição de teste",
        data_inicio=date(2023, 5, 1),
        data_fim=date(2023, 5, 31),
        ativo=True,
        tipo="semanal",
        temporada="primavera"
    )
    
    assert cardapio.nome == "Cardápio de Teste"
    assert cardapio.descricao == "Descrição de teste"
    assert cardapio.data_inicio == date(2023, 5, 1)
    assert cardapio.data_fim == date(2023, 5, 31)
    assert cardapio.ativo is True
    assert cardapio.tipo == "semanal"
    assert cardapio.temporada == "primavera"
    assert cardapio.secoes == []

def test_cardapio_secao_criacao(mock_cardapio):
    """Testa a criação básica de uma seção de cardápio"""
    secao = CardapioSecao(
        cardapio_id=mock_cardapio.id,
        nome="Entradas",
        descricao="Seção de entradas",
        ordem=1
    )
    
    assert secao.cardapio_id == mock_cardapio.id
    assert secao.nome == "Entradas"
    assert secao.descricao == "Seção de entradas"
    assert secao.ordem == 1
    assert secao.itens == []

def test_cardapio_item_criacao(mock_cardapio_secao, mock_prato):
    """Testa a criação básica de um item de cardápio"""
    item = CardapioItem(
        secao_id=mock_cardapio_secao.id,
        prato_id=mock_prato.id,
        ordem=1,
        preco_venda=Decimal('28.90'),
        destaque=True,
        disponivel=True,
        observacao="Item de teste"
    )
    
    assert item.secao_id == mock_cardapio_secao.id
    assert item.prato_id == mock_prato.id
    assert item.ordem == 1
    assert item.preco_venda == Decimal('28.90')
    assert item.destaque is True
    assert item.disponivel is True
    assert item.observacao == "Item de teste"

def test_cardapio_total_pratos(mock_cardapio, mock_cardapio_secao, mock_cardapio_item):
    """Testa a propriedade total_pratos do cardápio"""
    # Adicionar mais um item à seção
    prato2 = MagicMock()
    prato2.id = 2
    prato2.nome = "Prato de Teste 2"
    prato2.preco_venda = Decimal('35.90')
    
    item2 = CardapioItem(
        id=2,
        secao_id=mock_cardapio_secao.id,
        prato_id=prato2.id,
        ordem=2,
        preco_venda=Decimal('38.90'),
        destaque=False,
        disponivel=True
    )
    item2.prato = prato2
    mock_cardapio_secao.itens.append(item2)
    
    # Adicionar outra seção com um item
    secao2 = CardapioSecao(
        id=2,
        cardapio_id=mock_cardapio.id,
        nome="Pratos Principais",
        descricao="Seção de pratos principais",
        ordem=2
    )
    
    prato3 = MagicMock()
    prato3.id = 3
    prato3.nome = "Prato Principal de Teste"
    prato3.preco_venda = Decimal('45.90')
    
    item3 = CardapioItem(
        id=3,
        secao_id=secao2.id,
        prato_id=prato3.id,
        ordem=1,
        preco_venda=Decimal('48.90'),
        destaque=True,
        disponivel=True
    )
    item3.prato = prato3
    
    secao2.itens = [item3]
    mock_cardapio.secoes.append(secao2)
    
    # Agora temos 2 seções com 3 itens no total
    assert mock_cardapio.total_pratos == 3

def test_cardapio_ticket_medio_estimado(mock_cardapio, mock_cardapio_secao, mock_cardapio_item):
    """Testa a propriedade ticket_medio_estimado do cardápio"""
    # Temos 1 item com preço 28.90
    assert mock_cardapio.ticket_medio_estimado == 28.90
    
    # Adicionar mais um item à seção
    prato2 = MagicMock()
    prato2.id = 2
    prato2.nome = "Prato de Teste 2"
    prato2.preco_venda = Decimal('35.90')
    
    item2 = CardapioItem(
        id=2,
        secao_id=mock_cardapio_secao.id,
        prato_id=prato2.id,
        ordem=2,
        preco_venda=Decimal('41.10'),
        destaque=False,
        disponivel=True
    )
    item2.prato = prato2
    mock_cardapio_secao.itens.append(item2)
    
    # Agora temos 2 itens com preços 28.90 e 41.10, média = 35.00
    assert round(mock_cardapio.ticket_medio_estimado, 2) == 35.00
    
    # Testar com um item sem preço (None)
    item2.preco_venda = None
    assert mock_cardapio.ticket_medio_estimado == 28.90
    
    # Testar cardápio sem itens
    mock_cardapio_secao.itens = []
    assert mock_cardapio.ticket_medio_estimado == 0

def test_cardapio_margem_media(mock_cardapio, mock_cardapio_secao, mock_cardapio_item):
    """Testa a propriedade margem_media do cardápio"""
    # Configure o mock_prato para retornar um valor de custo
    mock_cardapio_item.prato.custo_total_por_porcao = Decimal('10.00')
    
    # Com preço de venda 28.90 e custo 10.00, a margem é (28.90 - 10) / 28.90 = 0.654 = 65.4%
    assert round(mock_cardapio.margem_media, 1) == 65.4

def test_cardapio_item_get_preco_venda(mock_cardapio_item, mock_prato):
    """Testa o método get_preco_venda do item de cardápio"""
    # O item tem preço personalizado
    assert mock_cardapio_item.get_preco_venda() == Decimal('28.90')
    
    # Se não tiver preço personalizado, deve usar o do prato
    mock_cardapio_item.preco_venda = None
    assert mock_cardapio_item.get_preco_venda() == mock_prato.preco_venda

def test_cardapio_repr(mock_cardapio):
    """Testa a representação em string do modelo Cardapio"""
    expected = f"<Cardapio {mock_cardapio.nome}>"
    assert repr(mock_cardapio) == expected

def test_cardapio_secao_repr(mock_cardapio_secao):
    """Testa a representação em string do modelo CardapioSecao"""
    expected = f"<CardapioSecao {mock_cardapio_secao.nome}>"
    assert repr(mock_cardapio_secao) == expected

def test_cardapio_item_repr(mock_cardapio_item):
    """Testa a representação em string do modelo CardapioItem"""
    expected = f"<CardapioItem {mock_cardapio_item.prato.nome}>"
    assert repr(mock_cardapio_item) == expected

def test_criar_cardapio(session):
    """Testa a criação de um cardápio básico"""
    cardapio = Cardapio(
        nome="Cardápio Verão",
        descricao="Cardápio especial de verão",
        data_inicio=date.today(),
        tipo="sazonal",
        temporada="verão"
    )
    session.add(cardapio)
    session.commit()
    
    assert cardapio.id is not None
    assert cardapio.nome == "Cardápio Verão"
    assert cardapio.tipo == "sazonal"
    assert cardapio.ativo is True

def test_cardapio_com_secoes(session):
    """Testa a criação de um cardápio com seções"""
    # Criar cardápio
    cardapio = Cardapio(
        nome="Cardápio Teste",
        data_inicio=date.today()
    )
    session.add(cardapio)
    session.commit()
    
    # Criar seções
    secao1 = CardapioSecao(
        cardapio_id=cardapio.id,
        nome="Entradas",
        ordem=1
    )
    secao2 = CardapioSecao(
        cardapio_id=cardapio.id,
        nome="Pratos Principais",
        ordem=2
    )
    session.add_all([secao1, secao2])
    session.commit()
    
    assert len(cardapio.secoes) == 2
    assert cardapio.secoes[0].nome == "Entradas"
    assert cardapio.secoes[1].nome == "Pratos Principais"

def test_cardapio_com_itens(session):
    """Testa a criação de um cardápio com itens"""
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
    
    # Criar cardápio com seção
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
    
    # Adicionar itens
    item1 = CardapioItem(
        secao_id=secao.id,
        prato_id=prato1.id,
        ordem=1,
        destaque=True
    )
    item2 = CardapioItem(
        secao_id=secao.id,
        prato_id=prato2.id,
        ordem=2
    )
    session.add_all([item1, item2])
    session.commit()
    
    assert len(secao.itens) == 2
    assert secao.itens[0].prato.nome == "Salada"
    assert secao.itens[1].prato.nome == "Filé"
    assert secao.itens[0].destaque is True

def test_calcular_ticket_medio(session):
    """Testa o cálculo do ticket médio do cardápio"""
    # Criar pratos
    prato1 = Prato(
        nome="Prato 1",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    prato2 = Prato(
        nome="Prato 2",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("40.00")
    )
    session.add_all([prato1, prato2])
    session.commit()
    
    # Criar cardápio com seção e itens
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
    
    item1 = CardapioItem(
        secao_id=secao.id,
        prato_id=prato1.id,
        ordem=1
    )
    item2 = CardapioItem(
        secao_id=secao.id,
        prato_id=prato2.id,
        ordem=2
    )
    session.add_all([item1, item2])
    session.commit()
    
    assert cardapio.ticket_medio_estimado == 35.00  # (30 + 40) / 2

def test_preco_especifico_cardapio(session):
    """Testa o preço específico para um item no cardápio"""
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
    
    item = CardapioItem(
        secao_id=secao.id,
        prato_id=prato.id,
        ordem=1,
        preco_venda=Decimal("35.00")  # Preço específico para o cardápio
    )
    session.add(item)
    session.commit()
    
    assert item.get_preco_venda == Decimal("35.00")  # Usa o preço específico
    assert item.prato.preco_venda == Decimal("30.00")  # Preço original do prato

def test_cardapio_to_dict(session):
    """Testa a conversão do cardápio para dicionário"""
    cardapio = Cardapio(
        nome="Cardápio Teste",
        descricao="Descrição teste",
        data_inicio=date.today(),
        tipo="diário",
        temporada="verão"
    )
    session.add(cardapio)
    session.commit()
    
    cardapio_dict = cardapio.to_dict()
    assert cardapio_dict['nome'] == "Cardápio Teste"
    assert cardapio_dict['descricao'] == "Descrição teste"
    assert cardapio_dict['tipo'] == "diário"
    assert cardapio_dict['temporada'] == "verão"
    assert cardapio_dict['ativo'] is True

def test_secao_to_dict(session):
    """Testa a conversão da seção para dicionário"""
    # Criar cardápio
    cardapio = Cardapio(
        nome="Cardápio Teste",
        data_inicio=date.today()
    )
    session.add(cardapio)
    session.commit()
    
    # Criar seção
    secao = CardapioSecao(
        cardapio_id=cardapio.id,
        nome="Seção Teste",
        descricao="Descrição teste",
        ordem=1
    )
    session.add(secao)
    session.commit()
    
    secao_dict = secao.to_dict()
    assert secao_dict['nome'] == "Seção Teste"
    assert secao_dict['descricao'] == "Descrição teste"
    assert secao_dict['ordem'] == 1

def test_item_to_dict(session):
    """Testa a conversão do item para dicionário"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar cardápio com seção
    cardapio = Cardapio(
        nome="Cardápio Teste",
        data_inicio=date.today()
    )
    session.add(cardapio)
    session.commit()
    
    secao = CardapioSecao(
        cardapio_id=cardapio.id,
        nome="Seção Teste",
        ordem=1
    )
    session.add(secao)
    session.commit()
    
    # Criar item
    item = CardapioItem(
        secao_id=secao.id,
        prato_id=prato.id,
        ordem=1,
        preco_venda=Decimal("35.00"),
        destaque=True,
        disponivel=True
    )
    session.add(item)
    session.commit()
    
    item_dict = item.to_dict()
    assert item_dict['ordem'] == 1
    assert item_dict['preco_venda'] == 35.00
    assert item_dict['destaque'] is True
    assert item_dict['disponivel'] is True
    assert item_dict['prato']['nome'] == "Prato Teste"
