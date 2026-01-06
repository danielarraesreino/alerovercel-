import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.models.modelo_desperdicio import MetaDesperdicio, CategoriaDesperdicio, RegistroDesperdicio
from app.extensions import db

@pytest.fixture
def mock_db_session():
    with patch('app.models.modelo_desperdicio.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_categoria_desperdicio():
    categoria = MagicMock(spec=CategoriaDesperdicio)
    categoria.id = 1
    categoria.nome = 'Sobras de Preparo'
    categoria.descricao = 'Sobras durante o preparo dos alimentos'
    categoria.cor = '#FF5733'
    return categoria

@pytest.fixture
def mock_registro_desperdicio(mock_categoria_desperdicio):
    registro = MagicMock(spec=RegistroDesperdicio)
    registro.id = 1
    registro.categoria_id = mock_categoria_desperdicio.id
    registro.categoria = mock_categoria_desperdicio
    registro.produto_id = 1
    registro.quantidade = 2.5
    registro.unidade_medida = 'kg'
    registro.data_registro = date.today()
    registro.valor_estimado = Decimal('25.50')
    registro.motivo = 'Produção excessiva'
    return registro

def test_meta_desperdicio_criacao():
    """Testa a criação básica de uma meta de desperdício"""
    data_inicio = date.today()
    data_fim = data_inicio + timedelta(days=90)
    
    meta = MetaDesperdicio(
        categoria_id=1,
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=20.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        descricao='Meta para redução de sobras de preparo'
    )
    
    assert meta.categoria_id == 1
    assert meta.valor_inicial == Decimal('1000.00')
    assert meta.meta_reducao_percentual == 20.0
    assert meta.data_inicio == data_inicio
    assert meta.data_fim == data_fim
    assert meta.descricao == 'Meta para redução de sobras de preparo'
    assert meta.valor_meta == Decimal('800.00')  # 1000 - 20%
    assert meta.status == 'Em andamento'

def test_meta_desperdicio_valor_meta():
    """Testa o cálculo do valor meta com base no percentual de redução"""
    # Teste com percentual positivo (redução)
    meta_reducao = MetaDesperdicio(
        valor_inicial=Decimal('500.00'),
        meta_reducao_percentual=30.0
    )
    assert meta_reducao.valor_meta == Decimal('350.00')  # 500 - 30%
    
    # Teste com percentual zero (manutenção)
    meta_manutencao = MetaDesperdicio(
        valor_inicial=Decimal('500.00'),
        meta_reducao_percentual=0.0
    )
    assert meta_manutencao.valor_meta == Decimal('500.00')  # 500 - 0%
    
    # Teste com percentual negativo (aumento controlado)
    meta_aumento = MetaDesperdicio(
        valor_inicial=Decimal('500.00'),
        meta_reducao_percentual=-10.0
    )
    assert meta_aumento.valor_meta == Decimal('550.00')  # 500 + 10%

def test_meta_desperdicio_status_property():
    """Testa a propriedade status da meta"""
    hoje = date.today()
    
    # Meta em andamento
    meta_andamento = MetaDesperdicio(
        data_inicio=hoje - timedelta(days=10),
        data_fim=hoje + timedelta(days=20),
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=10.0
    )
    assert meta_andamento.status == 'Em andamento'
    
    # Meta não iniciada
    meta_futura = MetaDesperdicio(
        data_inicio=hoje + timedelta(days=10),
        data_fim=hoje + timedelta(days=40),
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=10.0
    )
    assert meta_futura.status == 'Não iniciada'
    
    # Meta finalizada
    meta_finalizada = MetaDesperdicio(
        data_inicio=hoje - timedelta(days=40),
        data_fim=hoje - timedelta(days=10),
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=10.0
    )
    assert meta_finalizada.status == 'Finalizada'

def test_meta_desperdicio_valor_atual(mock_db_session):
    """Testa o cálculo do valor atual de desperdício durante o período da meta"""
    with patch('app.models.modelo_desperdicio.db.session.query') as mock_query:
        # Configurar o mock para retornar um valor de soma
        mock_filtro = MagicMock()
        mock_filtro.filter.return_value = mock_filtro
        mock_filtro.scalar.return_value = 750.0
        
        mock_query.return_value = mock_filtro
        
        # Criar meta
        meta = MetaDesperdicio(
            categoria_id=1,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today() + timedelta(days=30),
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=20.0
        )
        
        # Testar valor atual
        valor_atual = meta.valor_atual
        
        # Verificações
        assert valor_atual == Decimal('750.0')
        assert mock_query.called

def test_meta_desperdicio_progresso(mock_db_session):
    """Testa o cálculo do progresso da meta"""
    with patch.object(MetaDesperdicio, 'valor_atual', new_callable=lambda: Decimal('600.00')):
        # Meta com redução (valor atual < valor inicial)
        meta = MetaDesperdicio(
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=50.0  # Meta: reduzir para 500
        )
        
        # O progresso deve ser 80% (atingiu 400 de redução de 500 necessários)
        assert meta.progresso == 80.0
    
    with patch.object(MetaDesperdicio, 'valor_atual', new_callable=lambda: Decimal('1100.00')):
        # Meta com aumento (valor atual > valor inicial)
        meta = MetaDesperdicio(
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=50.0  # Meta: reduzir para 500
        )
        
        # O progresso deve ser negativo, pois piorou em vez de melhorar
        assert meta.progresso < 0
    
    with patch.object(MetaDesperdicio, 'valor_atual', new_callable=lambda: Decimal('500.00')):
        # Meta alcançada exatamente
        meta = MetaDesperdicio(
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=50.0  # Meta: reduzir para 500
        )
        
        # O progresso deve ser 100%
        assert meta.progresso == 100.0
    
    with patch.object(MetaDesperdicio, 'valor_atual', new_callable=lambda: Decimal('400.00')):
        # Meta superada
        meta = MetaDesperdicio(
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=50.0  # Meta: reduzir para 500
        )
        
        # O progresso deve ser > 100%
        assert meta.progresso > 100.0

def test_meta_desperdicio_economia_projetada():
    """Testa o cálculo da economia projetada pela meta"""
    # Meta com valor positivo
    meta = MetaDesperdicio(
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=30.0,
        custo_medio_kg=Decimal('15.00'),
        qtd_media_kg=Decimal('5.00')
    )
    
    economia = meta.economia_projetada
    assert economia == Decimal('300.00')  # 30% de 1000
    
    # Meta com valor zero
    meta_zero = MetaDesperdicio(
        valor_inicial=Decimal('0.00'),
        meta_reducao_percentual=30.0
    )
    
    assert meta_zero.economia_projetada == Decimal('0.00')

def test_meta_desperdicio_repr(mock_categoria_desperdicio):
    """Testa a representação em string da meta"""
    with patch.object(MetaDesperdicio, 'categoria', mock_categoria_desperdicio):
        meta = MetaDesperdicio(
            categoria_id=1,
            valor_inicial=Decimal('1000.00'),
            meta_reducao_percentual=20.0,
            data_inicio=date(2023, 5, 1),
            data_fim=date(2023, 7, 31)
        )
        
        repr_str = repr(meta)
        assert 'Sobras de Preparo' in repr_str
        assert '20.0%' in repr_str
        assert '2023-05-01' in repr_str or '01/05/2023' in repr_str
        assert '2023-07-31' in repr_str or '31/07/2023' in repr_str

def test_meta_desperdicio_crud_operations(mock_db_session):
    """Testa as operações CRUD para metas de desperdício"""
    # Criação
    meta = MetaDesperdicio(
        categoria_id=1,
        valor_inicial=Decimal('1000.00'),
        meta_reducao_percentual=20.0,
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=90)
    )
    
    # Mock do commit e add
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    
    # Simular adição ao banco
    db.session.add(meta)
    db.session.commit()
    
    # Verificar se os métodos foram chamados
    assert mock_db_session.add.called
    assert mock_db_session.add.call_args[0][0] == meta
    assert mock_db_session.commit.called
    
    # Simular atualização
    meta.meta_reducao_percentual = 25.0
    meta.descricao = 'Meta atualizada'
    db.session.commit()
    
    # Verificar se o commit foi chamado novamente
    assert mock_db_session.commit.call_count == 2
    
    # Simular remoção
    db.session.delete(meta)
    db.session.commit()
    
    # Verificar se delete e commit foram chamados
    assert mock_db_session.delete.called
    assert mock_db_session.delete.call_args[0][0] == meta
    assert mock_db_session.commit.call_count == 3
