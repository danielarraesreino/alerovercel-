import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from app.models.modelo_previsao import FatorSazonalidade
from app.extensions import db

@pytest.fixture
def mock_db_session():
    with patch('app.models.modelo_previsao.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_cardapio_item():
    mock_item = MagicMock()
    mock_item.id = 1
    mock_item.nome = 'Item de Teste'
    return mock_item

@pytest.fixture
def mock_prato():
    mock_prato = MagicMock()
    mock_prato.id = 2
    mock_prato.nome = 'Prato de Teste'
    return mock_prato

def test_fator_sazonalidade_criacao():
    """Testa a criação do modelo FatorSazonalidade"""
    # Criação com dia da semana
    fator_dia = FatorSazonalidade(
        dia_semana=5,  # Sexta-feira
        fator=1.2,
        descricao='Aumento de demanda às sextas-feiras'
    )
    
    assert fator_dia.dia_semana == 5
    assert fator_dia.fator == 1.2
    assert fator_dia.descricao == 'Aumento de demanda às sextas-feiras'
    assert fator_dia.mes is None
    
    # Criação com mês
    fator_mes = FatorSazonalidade(
        mes=12,  # Dezembro
        fator=1.5,
        descricao='Aumento de demanda em dezembro'
    )
    
    assert fator_mes.mes == 12
    assert fator_mes.fator == 1.5
    assert fator_mes.descricao == 'Aumento de demanda em dezembro'
    assert fator_mes.dia_semana is None
    
    # Criação com período do dia
    fator_periodo = FatorSazonalidade(
        periodo_dia='noite',
        fator=0.8,
        descricao='Redução de demanda à noite'
    )
    
    assert fator_periodo.periodo_dia == 'noite'
    assert fator_periodo.fator == 0.8
    assert fator_periodo.descricao == 'Redução de demanda à noite'
    
    # Criação com evento
    fator_evento = FatorSazonalidade(
        evento='Natal',
        fator=2.0,
        descricao='Aumento de demanda no Natal'
    )
    
    assert fator_evento.evento == 'Natal'
    assert fator_evento.fator == 2.0
    assert fator_evento.descricao == 'Aumento de demanda no Natal'

def test_fator_sazonalidade_para_item(mock_cardapio_item):
    """Testa a criação de fator para item específico"""
    fator = FatorSazonalidade(
        cardapio_item_id=mock_cardapio_item.id,
        dia_semana=0,  # Segunda-feira
        fator=0.7,
        descricao='Menor demanda às segundas'
    )
    
    assert fator.cardapio_item_id == mock_cardapio_item.id
    assert fator.prato_id is None
    assert fator.categoria_id is None

def test_fator_sazonalidade_para_prato(mock_prato):
    """Testa a criação de fator para prato específico"""
    fator = FatorSazonalidade(
        prato_id=mock_prato.id,
        mes=7,  # Julho
        fator=1.3,
        descricao='Maior demanda em julho'
    )
    
    assert fator.prato_id == mock_prato.id
    assert fator.cardapio_item_id is None
    assert fator.categoria_id is None

def test_fator_sazonalidade_para_categoria():
    """Testa a criação de fator para categoria inteira"""
    categoria_id = 3
    fator = FatorSazonalidade(
        categoria_id=categoria_id,
        evento='Feriados',
        fator=1.4,
        descricao='Aumento em feriados para categoria'
    )
    
    assert fator.categoria_id == categoria_id
    assert fator.cardapio_item_id is None
    assert fator.prato_id is None

def test_fator_sazonalidade_representacao(mock_cardapio_item):
    """Testa a representação em string do modelo"""
    # Teste com cardapio_item_id
    with patch.object(FatorSazonalidade, 'cardapio_item', mock_cardapio_item):
        fator = FatorSazonalidade(
            cardapio_item_id=mock_cardapio_item.id,
            dia_semana=6,  # Domingo
            fator=1.1
        )
        repr_str = repr(fator)
        assert 'Item de Teste' in repr_str
        assert 'dia_semana=6' in repr_str or 'Domingo' in repr_str

    # Teste com dia da semana
    fator_dia = FatorSazonalidade(
        dia_semana=3,  # Quarta-feira
        fator=1.0
    )
    repr_str = repr(fator_dia)
    assert 'dia_semana=3' in repr_str or 'Quarta' in repr_str
    
    # Teste com mês
    fator_mes = FatorSazonalidade(
        mes=6,  # Junho
        fator=1.2
    )
    repr_str = repr(fator_mes)
    assert 'mes=6' in repr_str or 'Junho' in repr_str
    
    # Teste com evento
    fator_evento = FatorSazonalidade(
        evento='Páscoa',
        fator=1.3
    )
    repr_str = repr(fator_evento)
    assert 'Páscoa' in repr_str

def test_fator_sazonalidade_combinado():
    """Testa a criação de fator com múltiplos critérios combinados"""
    fator = FatorSazonalidade(
        dia_semana=5,  # Sexta-feira
        periodo_dia='noite',
        fator=1.8,
        descricao='Aumento na noite de sexta-feira'
    )
    
    assert fator.dia_semana == 5
    assert fator.periodo_dia == 'noite'
    assert fator.fator == 1.8
    assert fator.descricao == 'Aumento na noite de sexta-feira'

def test_fator_sazonalidade_crud_operations(mock_db_session):
    """Testa as operações CRUD para o modelo FatorSazonalidade"""
    # Criação
    fator = FatorSazonalidade(
        dia_semana=2,  # Terça-feira
        fator=0.9,
        descricao='Fator de teste para CRUD'
    )
    
    # Mock do commit e add
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    
    # Simular adição ao banco
    db.session.add(fator)
    db.session.commit()
    
    # Verificar se os métodos foram chamados
    assert mock_db_session.add.called
    assert mock_db_session.add.call_args[0][0] == fator
    assert mock_db_session.commit.called
    
    # Simular atualização
    fator.fator = 1.1
    fator.descricao = 'Descrição atualizada'
    db.session.commit()
    
    # Verificar se o commit foi chamado novamente
    assert mock_db_session.commit.call_count == 2
    
    # Simular remoção
    db.session.delete(fator)
    db.session.commit()
    
    # Verificar se delete e commit foram chamados
    assert mock_db_session.delete.called
    assert mock_db_session.delete.call_args[0][0] == fator
    assert mock_db_session.commit.call_count == 3
