import pytest
import json
from datetime import datetime, date, timedelta
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_cardapio import CardapioItem
from app.models.modelo_prato import Prato

# Fixtures para facilitar testes com dados relacionados
@pytest.fixture
def cardapio_item(session):
    # Cria um prato para associar ao item
    prato = Prato(
        nome='Prato Teste',
        descricao='Prato para testes de previsu00e3o',
        categoria='Principal',
        tempo_preparo=15,
        preco_venda=25.0
    )
    session.add(prato)
    session.flush()
    
    # Cria um item de cardu00e1pio
    item = CardapioItem(
        secao_id=1,  # Asumindo que temos uma seu00e7u00e3o padru00e3o para testes
        prato_id=prato.id,
        preco_venda=30.0,
        disponivel=True,
        ordem=1
    )
    session.add(item)
    session.commit()
    return item

# Testes para HistoricoVendas
def test_historico_vendas_crud(session, cardapio_item):
    """Teste CRUD completo para HistoricoVendas"""
    # CREATE: Criar registro de venda
    data_venda = date.today()
    venda = HistoricoVendas(
        data=data_venda,
        cardapio_item_id=cardapio_item.id,
        quantidade=5,
        valor_unitario=30.0,
        valor_total=150.0,
        periodo_dia='noite',
        dia_semana=data_venda.weekday(),
        semana_mes=1,
        mes=data_venda.month
    )
    session.add(venda)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    venda_db = session.query(HistoricoVendas).filter_by(id=venda.id).first()
    assert venda_db is not None
    assert venda_db.quantidade == 5
    assert venda_db.valor_total == 150.0
    assert venda_db.cardapio_item_id == cardapio_item.id
    
    # UPDATE: Atualizar valores
    venda_db.quantidade = 10
    venda_db.valor_total = 300.0
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    venda_atualizada = session.query(HistoricoVendas).filter_by(id=venda.id).first()
    assert venda_atualizada.quantidade == 10
    assert venda_atualizada.valor_total == 300.0
    
    # DELETE: Remover registro
    session.delete(venda_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    venda_removida = session.query(HistoricoVendas).filter_by(id=venda.id).first()
    assert venda_removida is None

def test_historico_vendas_relacionamentos(session, cardapio_item):
    """Testa os relacionamentos do modelo HistoricoVendas"""
    # Criar registro de venda
    venda = HistoricoVendas(
        data=date.today(),
        cardapio_item_id=cardapio_item.id,
        quantidade=3,
        valor_unitario=30.0,
        valor_total=90.0,
        periodo_dia='tarde'
    )
    session.add(venda)
    session.commit()
    
    # Verificar relacionamento com CardapioItem
    assert venda.cardapio_item is not None
    assert venda.cardapio_item.id == cardapio_item.id
    assert venda.cardapio_item.preco_venda == 30.0
    
    # Verificar relacionamento inverso (cardapio_item -> historico_vendas)
    item_atualizado = session.query(CardapioItem).filter_by(id=cardapio_item.id).first()
    assert len(item_atualizado.historico_vendas) > 0
    assert item_atualizado.historico_vendas[0].id == venda.id

def test_historico_vendas_registrar_venda_classmethod(session, cardapio_item):
    """Testa o mu00e9todo de classe registrar_venda"""
    # Registrar venda usando o mu00e9todo de classe
    data_str = date.today().strftime('%Y-%m-%d')
    venda = HistoricoVendas.registrar_venda(
        data=data_str,
        item_id=cardapio_item.id,
        tipo_item='cardapio_item',
        quantidade=5,
        valor_unitario=30.0,
        periodo_dia='noite',
        evento_especial='Teste',
        clima='ensolarado',
        temperatura=25.5
    )
    session.add(venda)
    session.commit()
    
    # Verificar se todos os campos foram preenchidos corretamente
    assert venda.id is not None
    assert venda.quantidade == 5
    assert venda.valor_total == 150.0  # 5 * 30.0
    assert venda.clima == 'ensolarado'
    assert venda.temperatura == 25.5
    assert venda.evento_especial == 'Teste'
    
    # Verificar campos calculados
    hoje = date.today()
    assert venda.dia_semana == hoje.weekday()
    assert venda.mes == hoje.month

# Testes para PrevisaoDemanda
def test_previsao_demanda_crud(session, cardapio_item):
    """Teste CRUD completo para PrevisaoDemanda"""
    # Dados de exemplo para previsu00e3o
    data_inicio = date.today()
    data_fim = data_inicio + timedelta(days=7)
    valores = {
        data_inicio.strftime('%Y-%m-%d'): 10,
        (data_inicio + timedelta(days=1)).strftime('%Y-%m-%d'): 12,
        (data_inicio + timedelta(days=2)).strftime('%Y-%m-%d'): 15
    }
    
    # CREATE: Criar previsu00e3o
    previsao = PrevisaoDemanda(
        data_inicio=data_inicio,
        data_fim=data_fim,
        cardapio_item_id=cardapio_item.id,
        metodo='mu00e9dia_mu00f3vel',
        parametros=json.dumps({'janela': 7}),
        valores_previstos=json.dumps(valores),
        confiabilidade=0.85
    )
    session.add(previsao)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    previsao_db = session.query(PrevisaoDemanda).filter_by(id=previsao.id).first()
    assert previsao_db is not None
    assert previsao_db.metodo == 'mu00e9dia_mu00f3vel'
    assert previsao_db.confiabilidade == 0.85
    assert previsao_db.cardapio_item_id == cardapio_item.id
    
    # UPDATE: Atualizar valores
    valores_atualizados = valores.copy()
    valores_atualizados[(data_inicio + timedelta(days=3)).strftime('%Y-%m-%d')] = 18
    previsao_db.valores_previstos = json.dumps(valores_atualizados)
    previsao_db.confiabilidade = 0.9
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    previsao_atualizada = session.query(PrevisaoDemanda).filter_by(id=previsao.id).first()
    assert previsao_atualizada.confiabilidade == 0.9
    valores_recuperados = json.loads(previsao_atualizada.valores_previstos)
    assert len(valores_recuperados) == 4
    
    # DELETE: Remover registro
    session.delete(previsao_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    previsao_removida = session.query(PrevisaoDemanda).filter_by(id=previsao.id).first()
    assert previsao_removida is None

def test_previsao_demanda_metodos_auxiliares(session, cardapio_item):
    """Testa os mu00e9todos auxiliares de PrevisaoDemanda"""
    # Dados de exemplo
    data_inicio = date.today()
    valores = {
        data_inicio.strftime('%Y-%m-%d'): 10,
        (data_inicio + timedelta(days=1)).strftime('%Y-%m-%d'): 12,
        (data_inicio + timedelta(days=2)).strftime('%Y-%m-%d'): 15
    }
    
    # Criar previsu00e3o
    previsao = PrevisaoDemanda(
        data_inicio=data_inicio,
        data_fim=data_inicio + timedelta(days=2),
        cardapio_item_id=cardapio_item.id,
        metodo='mu00e9dia_mu00f3vel',
        valores_previstos=json.dumps(valores)
    )
    session.add(previsao)
    session.commit()
    
    # Testar get_valores_previstos()
    valores_dict = previsao.get_valores_previstos()
    assert isinstance(valores_dict, dict)
    assert len(valores_dict) == 3
    assert valores_dict[data_inicio.strftime('%Y-%m-%d')] == 10
    
    # Testar set_valores_previstos()
    novos_valores = {
        data_inicio.strftime('%Y-%m-%d'): 20,
        (data_inicio + timedelta(days=1)).strftime('%Y-%m-%d'): 25
    }
    previsao.set_valores_previstos(novos_valores)
    session.commit()
    
    # Verificar se os valores foram atualizados
    valores_atualizados = previsao.get_valores_previstos()
    assert len(valores_atualizados) == 2
    assert valores_atualizados[data_inicio.strftime('%Y-%m-%d')] == 20
    
    # Testar get_previsao_para_data()
    valor_data_especifica = previsao.get_previsao_para_data(data_inicio)
    assert valor_data_especifica == 20
    
    # Testar data inexistente
    data_inexistente = data_inicio + timedelta(days=10)
    valor_data_inexistente = previsao.get_previsao_para_data(data_inexistente)
    assert valor_data_inexistente is None

# Testes para FatorSazonalidade
def test_fator_sazonalidade_crud(session, cardapio_item):
    """Teste CRUD completo para FatorSazonalidade"""
    # CREATE: Criar fator de sazonalidade
    fator = FatorSazonalidade(
        dia_semana=5,  # Su00e1bado
        cardapio_item_id=cardapio_item.id,
        fator=1.2,
        descricao='Aumento de 20% aos su00e1bados'
    )
    session.add(fator)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    fator_db = session.query(FatorSazonalidade).filter_by(id=fator.id).first()
    assert fator_db is not None
    assert fator_db.dia_semana == 5
    assert fator_db.fator == 1.2
    assert fator_db.cardapio_item_id == cardapio_item.id
    
    # UPDATE: Atualizar valores
    fator_db.fator = 1.3
    fator_db.descricao = 'Aumento de 30% aos su00e1bados'
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    fator_atualizado = session.query(FatorSazonalidade).filter_by(id=fator.id).first()
    assert fator_atualizado.fator == 1.3
    assert fator_atualizado.descricao == 'Aumento de 30% aos su00e1bados'
    
    # DELETE: Remover registro
    session.delete(fator_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    fator_removido = session.query(FatorSazonalidade).filter_by(id=fator.id).first()
    assert fator_removido is None

def test_combinacoes_fatores_sazonalidade(session, cardapio_item):
    """Testa diferentes combinau00e7u00f5es de fatores sazonais"""
    # Criar diferentes tipos de fatores sazonais
    fatores = [
        # Fator por dia da semana
        FatorSazonalidade(
            dia_semana=6,  # Domingo
            cardapio_item_id=cardapio_item.id,
            fator=1.5,
            descricao='Aumento aos domingos'
        ),
        # Fator por mu00eas
        FatorSazonalidade(
            mes=12,  # Dezembro
            cardapio_item_id=cardapio_item.id,
            fator=1.3,
            descricao='Aumento em dezembro'
        ),
        # Fator por peru00edodo do dia
        FatorSazonalidade(
            periodo_dia='noite',
            cardapio_item_id=cardapio_item.id,
            fator=1.2,
            descricao='Aumento no peru00edodo noturno'
        ),
        # Fator por evento
        FatorSazonalidade(
            evento='Natal',
            cardapio_item_id=cardapio_item.id,
            fator=2.0,
            descricao='Aumento no Natal'
        )
    ]
    
    for fator in fatores:
        session.add(fator)
    session.commit()
    
    # Verificar se todos foram salvos
    fatores_db = session.query(FatorSazonalidade).filter_by(cardapio_item_id=cardapio_item.id).all()
    assert len(fatores_db) == 4
    
    # Verificar relacionamento com CardapioItem
    item_db = session.query(CardapioItem).filter_by(id=cardapio_item.id).first()
    assert len(item_db.fatores_sazonalidade) == 4
    
    # Testar cada tipo de fator
    fator_dia = session.query(FatorSazonalidade).filter_by(dia_semana=6).first()
    assert fator_dia.fator == 1.5
    
    fator_mes = session.query(FatorSazonalidade).filter_by(mes=12).first()
    assert fator_mes.fator == 1.3
    
    fator_periodo = session.query(FatorSazonalidade).filter_by(periodo_dia='noite').first()
    assert fator_periodo.fator == 1.2
    
    fator_evento = session.query(FatorSazonalidade).filter_by(evento='Natal').first()
    assert fator_evento.fator == 2.0
