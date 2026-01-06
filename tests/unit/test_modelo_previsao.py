import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_prato import Prato
from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem

@pytest.fixture
def setup_cardapio_item(session):
    """Fixture para criar um item de cardápio para testes"""
    item = CardapioItem(
        nome='Item de Teste',
        descricao='Item para testes',
        preco=10.0,
        categoria='Teste',
        disponivel=True
    )
    session.add(item)
    session.commit()
    return item

@pytest.mark.parametrize(
    "data_teste,quantidade,valor_unitario",
    [
        (datetime.now().date(), 10, 10.0),
        (datetime.now().date() - timedelta(days=1), 5, 10.0),
        (datetime.now().date() - timedelta(days=7), 15, 10.0),
    ],
)
def test_historico_vendas_create(session, setup_cardapio_item, data_teste, quantidade, valor_unitario):
    """Testa a criau00e7u00e3o de registros de histu00f3rico de vendas"""
    # Arrange & Act
    venda = HistoricoVendas(
        data=data_teste,
        cardapio_item_id=setup_cardapio_item.id,
        quantidade=quantidade,
        valor_unitario=valor_unitario,
        valor_total=quantidade * valor_unitario
    )
    session.add(venda)
    session.commit()
    
    # Assert
    assert venda.id is not None
    assert venda.data == data_teste
    assert venda.cardapio_item_id == setup_cardapio_item.id
    assert venda.quantidade == quantidade
    assert venda.valor_unitario == valor_unitario
    assert venda.valor_total == quantidade * valor_unitario

@pytest.mark.parametrize(
    "data_inicio,data_fim,metodo,valores_previstos",
    [
        (datetime.now().date(), datetime.now().date() + timedelta(days=7), "média_móvel", '{"2025-05-22": 10, "2025-05-23": 10, "2025-05-24": 10, "2025-05-25": 10, "2025-05-26": 10, "2025-05-27": 10, "2025-05-28": 10}'),
        (datetime.now().date(), datetime.now().date() + timedelta(days=7), "regressão_linear", '{"2025-05-22": 5, "2025-05-23": 6, "2025-05-24": 7, "2025-05-25": 8, "2025-05-26": 9, "2025-05-27": 10, "2025-05-28": 11}'),
    ],
)
def test_previsao_demanda_create(session, setup_cardapio_item, data_inicio, data_fim, metodo, valores_previstos):
    """Testa a criau00e7u00e3o de registros de previsu00e3o de demanda"""
    # Arrange & Act
    previsao = PrevisaoDemanda(
        cardapio_item_id=setup_cardapio_item.id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        metodo=metodo,
        valores_previstos=valores_previstos,
        data_criacao=datetime.now()
    )
    session.add(previsao)
    session.commit()
    
    # Assert
    assert previsao.id is not None
    assert previsao.cardapio_item_id == setup_cardapio_item.id
    assert previsao.data_inicio == data_inicio
    assert previsao.data_fim == data_fim
    assert previsao.metodo == metodo
    assert previsao.valores_previstos == valores_previstos

@pytest.mark.parametrize(
    "dia_semana,fator,descricao",
    [
        (0, 1.2, "Segunda-feira"),
        (None, 0.8, "Janeiro"),
        (None, 1.5, "Feriado Nacional"),
    ],
)
def test_fator_sazonalidade_create(session, setup_cardapio_item, dia_semana, fator, descricao):
    """Testa a criau00e7u00e3o de registros de fatores de sazonalidade"""
    # Arrange & Act
    fator_sazonalidade = FatorSazonalidade(
        cardapio_item_id=setup_cardapio_item.id,
        dia_semana=dia_semana,
        fator=fator,
        descricao=descricao
    )
    session.add(fator_sazonalidade)
    session.commit()
    
    # Assert
    assert fator_sazonalidade.id is not None
    assert fator_sazonalidade.dia_semana == dia_semana
    assert fator_sazonalidade.fator == fator
    assert fator_sazonalidade.descricao == descricao

def test_relacionamento_previsao_historico(session):
    """Testa os relacionamentos entre os modelos de previsu00e3o"""
    # Arrange
    # Criar um item de cardápio para teste
    item = CardapioItem(
        nome='Item para Relacionamento',
        descricao='Item para teste de relacionamento',
        preco=15.0,
        categoria='Teste',
        disponivel=True
    )
    session.add(item)
    session.commit()
    
    # Criar alguns registros de histórico
    for i in range(5):
        venda = HistoricoVendas(
            data=datetime.now().date() - timedelta(days=i),
            cardapio_item_id=item.id,
            quantidade=10 + i,
            valor_unitario=item.preco,
            valor_total=(10 + i) * item.preco
        )
        session.add(venda)
    
    # Criar uma previsão para esse item de cardápio
    previsao = PrevisaoDemanda(
        cardapio_item_id=item.id,
        data_inicio=datetime.now().date(),
        data_fim=datetime.now().date() + timedelta(days=7),
        metodo="média_móvel",
        valores_previstos='{"2025-05-22": 12, "2025-05-23": 12, "2025-05-24": 12, "2025-05-25": 12, "2025-05-26": 12, "2025-05-27": 12, "2025-05-28": 12}',
        data_criacao=datetime.now()
    )
    session.add(previsao)
    session.commit()
    
    # Act
    historico = session.query(HistoricoVendas).filter_by(cardapio_item_id=item.id).all()
    previsoes = session.query(PrevisaoDemanda).filter_by(cardapio_item_id=item.id).all()
    
    # Assert
    assert len(historico) == 5
    assert len(previsoes) == 1
    assert previsoes[0].cardapio_item_id == historico[0].cardapio_item_id

def test_criar_historico_vendas(session):
    """Testa a criação de um registro de histórico de vendas"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar registro de venda
    venda = HistoricoVendas.registrar_venda(
        data=date.today(),
        item_id=prato.id,
        tipo_item='prato',
        quantidade=2,
        valor_unitario=Decimal("30.00"),
        periodo_dia="noite",
        clima="ensolarado",
        temperatura=25.5
    )
    
    assert venda.id is not None
    assert venda.quantidade == 2
    assert venda.valor_unitario == Decimal("30.00")
    assert venda.valor_total == Decimal("60.00")
    assert venda.periodo_dia == "noite"
    assert venda.clima == "ensolarado"
    assert venda.temperatura == 25.5
    assert venda.dia_semana == date.today().weekday()
    assert venda.mes == date.today().month

def test_historico_vendas_com_cardapio(session):
    """Testa a criação de um registro de histórico de vendas com item de cardápio"""
    # Criar cardápio e seção
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
    
    # Criar prato e item de cardápio
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    item = CardapioItem(
        secao_id=secao.id,
        prato_id=prato.id,
        ordem=1,
        preco_venda=Decimal("35.00")
    )
    session.add(item)
    session.commit()
    
    # Criar registro de venda
    venda = HistoricoVendas.registrar_venda(
        data=date.today(),
        item_id=item.id,
        tipo_item='cardapio_item',
        quantidade=3,
        valor_unitario=Decimal("35.00"),
        evento_especial="Promoção"
    )
    
    assert venda.cardapio_item_id == item.id
    assert venda.prato_id is None
    assert venda.quantidade == 3
    assert venda.valor_total == Decimal("105.00")
    assert venda.evento_especial == "Promoção"

def test_historico_vendas_to_dict(session):
    """Testa a conversão do histórico de vendas para dicionário"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar registro de venda
    venda = HistoricoVendas.registrar_venda(
        data=date.today(),
        item_id=prato.id,
        tipo_item='prato',
        quantidade=2,
        valor_unitario=Decimal("30.00")
    )
    
    venda_dict = venda.to_dict()
    assert venda_dict['quantidade'] == 2
    assert venda_dict['valor_unitario'] == 30.00
    assert venda_dict['valor_total'] == 60.00
    assert venda_dict['prato']['nome'] == "Prato Teste"

def test_criar_previsao_demanda(session):
    """Testa a criação de uma previsão de demanda"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar previsão
    previsao = PrevisaoDemanda(
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=7),
        prato_id=prato.id,
        metodo="media_movel",
        parametros=json.dumps({"janela": 7}),
        valores_previstos=json.dumps({
            date.today().isoformat(): 10,
            (date.today() + timedelta(days=1)).isoformat(): 12
        }),
        confiabilidade=0.85
    )
    session.add(previsao)
    session.commit()
    
    assert previsao.id is not None
    assert previsao.prato_id == prato.id
    assert previsao.metodo == "media_movel"
    assert previsao.confiabilidade == 0.85
    assert len(previsao.get_valores_previstos()) == 2

def test_previsao_demanda_get_previsao(session):
    """Testa a obtenção de previsão para uma data específica"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar previsão
    data_hoje = date.today()
    previsao = PrevisaoDemanda(
        data_inicio=data_hoje,
        data_fim=data_hoje + timedelta(days=7),
        prato_id=prato.id,
        metodo="media_movel",
        valores_previstos=json.dumps({
            data_hoje.isoformat(): 10,
            (data_hoje + timedelta(days=1)).isoformat(): 12
        })
    )
    session.add(previsao)
    session.commit()
    
    # Testar obtenção de previsão
    assert previsao.get_previsao_para_data(data_hoje) == 10
    assert previsao.get_previsao_para_data(data_hoje + timedelta(days=1)) == 12
    assert previsao.get_previsao_para_data(data_hoje + timedelta(days=2)) is None

def test_previsao_demanda_to_dict(session):
    """Testa a conversão da previsão de demanda para dicionário"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar previsão
    data_hoje = date.today()
    previsao = PrevisaoDemanda(
        data_inicio=data_hoje,
        data_fim=data_hoje + timedelta(days=7),
        prato_id=prato.id,
        metodo="media_movel",
        parametros=json.dumps({"janela": 7}),
        valores_previstos=json.dumps({
            data_hoje.isoformat(): 10
        }),
        confiabilidade=0.85
    )
    session.add(previsao)
    session.commit()
    
    previsao_dict = previsao.to_dict()
    assert previsao_dict['metodo'] == "media_movel"
    assert previsao_dict['confiabilidade'] == 0.85
    assert previsao_dict['parametros'] == {"janela": 7}
    assert previsao_dict['prato']['nome'] == "Prato Teste"

def test_criar_fator_sazonalidade(session):
    """Testa a criação de um fator de sazonalidade"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar fator de sazonalidade
    fator = FatorSazonalidade(
        mes=12,  # Dezembro
        periodo_dia="noite",
        prato_id=prato.id,
        fator=1.2,  # Aumento de 20%
        descricao="Aumento de demanda no fim de ano"
    )
    session.add(fator)
    session.commit()
    
    assert fator.id is not None
    assert fator.mes == 12
    assert fator.periodo_dia == "noite"
    assert fator.prato_id == prato.id
    assert fator.fator == 1.2
    assert fator.descricao == "Aumento de demanda no fim de ano"

def test_fator_sazonalidade_dia_semana(session):
    """Testa a criação de um fator de sazonalidade para dia da semana"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar fator de sazonalidade para sexta-feira
    fator = FatorSazonalidade(
        dia_semana=4,  # Sexta-feira
        periodo_dia="noite",
        prato_id=prato.id,
        fator=1.5,  # Aumento de 50%
        descricao="Happy Hour"
    )
    session.add(fator)
    session.commit()
    
    assert fator.dia_semana == 4
    assert fator.mes is None
    assert fator.fator == 1.5

def test_fator_sazonalidade_evento(session):
    """Testa a criação de um fator de sazonalidade para evento especial"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar fator de sazonalidade para evento
    fator = FatorSazonalidade(
        evento="Dia dos Namorados",
        prato_id=prato.id,
        fator=2.0,  # Dobro da demanda
        descricao="Aumento de demanda no Dia dos Namorados"
    )
    session.add(fator)
    session.commit()
    
    assert fator.evento == "Dia dos Namorados"
    assert fator.mes is None
    assert fator.dia_semana is None
    assert fator.fator == 2.0

def test_fator_sazonalidade_to_dict(session):
    """Testa a conversão do fator de sazonalidade para dicionário"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar fator de sazonalidade
    fator = FatorSazonalidade(
        mes=12,
        periodo_dia="noite",
        prato_id=prato.id,
        fator=1.2,
        descricao="Aumento de demanda no fim de ano"
    )
    session.add(fator)
    session.commit()
    
    fator_dict = fator.to_dict()
    assert fator_dict['mes'] == 12
    assert fator_dict['periodo_dia'] == "noite"
    assert fator_dict['fator'] == 1.2
    assert fator_dict['descricao'] == "Aumento de demanda no fim de ano"
    assert fator_dict['prato']['nome'] == "Prato Teste"

def test_fator_sazonalidade_repr(session):
    """Testa a representação em string do fator de sazonalidade"""
    # Criar prato
    prato = Prato(
        nome="Prato Teste",
        rendimento=1,
        unidade_rendimento="porção",
        preco_venda=Decimal("30.00")
    )
    session.add(prato)
    session.commit()
    
    # Criar fator de sazonalidade
    fator = FatorSazonalidade(
        mes=12,
        periodo_dia="noite",
        prato_id=prato.id,
        fator=1.2,
        descricao="Aumento de demanda no fim de ano"
    )
    session.add(fator)
    session.commit()
    
    expected = "<Fator 1.2 para Prato Teste em Mês 12>"
    assert repr(fator) == expected
