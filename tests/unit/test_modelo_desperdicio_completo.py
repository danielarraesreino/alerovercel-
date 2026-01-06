import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto

# Fixtures para facilitar os testes
@pytest.fixture
def categoria_desperdicio(session):
    """Cria uma categoria de desperdu00edcio para os testes"""
    categoria = CategoriaDesperdicio(
        nome='Vencidos Teste',
        descricao='Produtos vencidos para testes',
        cor='#FF0000'
    )
    session.add(categoria)
    session.commit()
    return categoria

@pytest.fixture
def produto_teste(session):
    """Cria um produto para os testes"""
    produto = Produto(
        nome='Produto Teste Desperdu00edcio',
        descricao='Produto para testar desperdu00edcio',
        unidade_medida='kg',
        preco_unitario=15.75,
        estoque_atual=50.0,
        estoque_minimo=10.0,
        categoria='Teste'
    )
    session.add(produto)
    session.commit()
    return produto

# Testes para CategoriaDesperdicio
def test_categoria_desperdicio_crud(session):
    """Teste CRUD completo para CategoriaDesperdicio"""
    # CREATE: Criar categoria
    categoria = CategoriaDesperdicio(
        nome='Quebrados',
        descricao='Produtos quebrados durante manuseio',
        cor='#0000FF'
    )
    session.add(categoria)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    categoria_db = session.query(CategoriaDesperdicio).filter_by(id=categoria.id).first()
    assert categoria_db is not None
    assert categoria_db.nome == 'Quebrados'
    assert categoria_db.cor == '#0000FF'
    
    # UPDATE: Atualizar valores
    categoria_db.nome = 'Quebrados e Danificados'
    categoria_db.cor = '#0000CC'
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    categoria_atualizada = session.query(CategoriaDesperdicio).filter_by(id=categoria.id).first()
    assert categoria_atualizada.nome == 'Quebrados e Danificados'
    assert categoria_atualizada.cor == '#0000CC'
    
    # DELETE: Remover registro
    session.delete(categoria_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    categoria_removida = session.query(CategoriaDesperdicio).filter_by(id=categoria.id).first()
    assert categoria_removida is None

def test_categoria_desperdicio_validacoes(session):
    """Testa as validau00e7u00f5es do modelo CategoriaDesperdicio"""
    # Testar nome obrigatu00f3rio
    categoria_sem_nome = CategoriaDesperdicio(
        descricao='Teste sem nome',
        cor='#CCCCCC'
    )
    session.add(categoria_sem_nome)
    
    # Deve falhar ao tentar persistir
    with pytest.raises(Exception):
        session.commit()
    
    session.rollback()
    
    # Testar nome u00fanico
    categoria1 = CategoriaDesperdicio(nome='Nome Duplicado', cor='#AAAAAA')
    session.add(categoria1)
    session.commit()
    
    categoria2 = CategoriaDesperdicio(nome='Nome Duplicado', cor='#BBBBBB')
    session.add(categoria2)
    
    # Deve falhar por nome duplicado
    with pytest.raises(Exception):
        session.commit()
        
    session.rollback()

# Testes para RegistroDesperdicio
def test_registro_desperdicio_crud(session, categoria_desperdicio, produto_teste):
    """Teste CRUD completo para RegistroDesperdicio"""
    data_atual = datetime.now()
    
    # CREATE: Criar registro
    registro = RegistroDesperdicio(
        categoria_id=categoria_desperdicio.id,
        produto_id=produto_teste.id,
        quantidade=2.5,
        unidade_medida='kg',
        valor_estimado=39.38,  # 2.5 * 15.75
        data_registro=data_atual,
        motivo='Produto vencido',
        responsavel='Funcionu00e1rio Teste',
        local='Estoque',
        descricao='Registro de teste'
    )
    session.add(registro)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    registro_db = session.query(RegistroDesperdicio).filter_by(id=registro.id).first()
    assert registro_db is not None
    assert registro_db.quantidade == 2.5
    assert registro_db.valor_estimado == 39.38
    assert registro_db.motivo == 'Produto vencido'
    
    # UPDATE: Atualizar valores
    registro_db.quantidade = 3.0
    registro_db.valor_estimado = 47.25  # 3.0 * 15.75
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    registro_atualizado = session.query(RegistroDesperdicio).filter_by(id=registro.id).first()
    assert registro_atualizado.quantidade == 3.0
    assert registro_atualizado.valor_estimado == 47.25
    
    # DELETE: Remover registro
    session.delete(registro_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    registro_removido = session.query(RegistroDesperdicio).filter_by(id=registro.id).first()
    assert registro_removido is None

def test_registro_desperdicio_relacionamentos(session, categoria_desperdicio, produto_teste):
    """Testa os relacionamentos do modelo RegistroDesperdicio"""
    # Criar registro
    registro = RegistroDesperdicio(
        categoria_id=categoria_desperdicio.id,
        produto_id=produto_teste.id,
        quantidade=1.5,
        unidade_medida='kg',
        valor_estimado=23.63,
        data_registro=datetime.now(),
        motivo='Teste de relacionamento'
    )
    session.add(registro)
    session.commit()
    
    # Verificar relacionamento com categoria
    assert registro.categoria is not None
    assert registro.categoria.id == categoria_desperdicio.id
    assert registro.categoria.nome == 'Vencidos Teste'
    
    # Verificar relacionamento com produto
    assert registro.produto is not None
    assert registro.produto.id == produto_teste.id
    assert registro.produto.nome == 'Produto Teste Desperdu00edcio'
    
    # Verificar relacionamento reverso (categoria -> registros)
    categoria_atualizada = session.query(CategoriaDesperdicio).filter_by(id=categoria_desperdicio.id).first()
    assert len(categoria_atualizada.registros) > 0
    assert categoria_atualizada.registros[0].id == registro.id
    
    # Verificar relacionamento reverso (produto -> registros_desperdicio)
    produto_atualizado = session.query(Produto).filter_by(id=produto_teste.id).first()
    assert len(produto_atualizado.registros_desperdicio) > 0
    assert produto_atualizado.registros_desperdicio[0].id == registro.id

def test_registro_desperdicio_metodos_agregacao(session, categoria_desperdicio, produto_teste):
    """Testa mu00e9todos de agregau00e7u00e3o e cu00e1lculo de desperdu00edcio"""
    # Criar mu00faltiplos registros para o mesmo produto e categoria
    for i in range(5):
        registro = RegistroDesperdicio(
            categoria_id=categoria_desperdicio.id,
            produto_id=produto_teste.id,
            quantidade=1.0,
            unidade_medida='kg',
            valor_estimado=15.75,
            data_registro=datetime.now() - timedelta(days=i),
            motivo=f'Teste {i}'
        )
        session.add(registro)
    session.commit()
    
    # Obter total de desperdu00edcio por categoria
    total_por_categoria = session.query(
        CategoriaDesperdicio.id,
        CategoriaDesperdicio.nome,
        func.sum(RegistroDesperdicio.valor_estimado).label('total_valor'),
        func.sum(RegistroDesperdicio.quantidade).label('total_quantidade')
    ).join(RegistroDesperdicio).group_by(CategoriaDesperdicio.id).first()
    
    assert total_por_categoria is not None
    assert total_por_categoria.id == categoria_desperdicio.id
    assert round(total_por_categoria.total_valor, 2) == round(15.75 * 5, 2)
    assert total_por_categoria.total_quantidade == 5.0
    
    # Obter total de desperdu00edcio por produto
    total_por_produto = session.query(
        Produto.id,
        Produto.nome,
        func.sum(RegistroDesperdicio.valor_estimado).label('total_valor'),
        func.sum(RegistroDesperdicio.quantidade).label('total_quantidade')
    ).join(RegistroDesperdicio).group_by(Produto.id).first()
    
    assert total_por_produto is not None
    assert total_por_produto.id == produto_teste.id
    assert round(total_por_produto.total_valor, 2) == round(15.75 * 5, 2)
    assert total_por_produto.total_quantidade == 5.0

# Testes para MetaDesperdicio
def test_meta_desperdicio_crud(session, categoria_desperdicio):
    """Teste CRUD completo para MetaDesperdicio"""
    data_inicio = date.today()
    data_fim = data_inicio + timedelta(days=30)
    
    # CREATE: Criar meta
    meta = MetaDesperdicio(
        categoria_id=categoria_desperdicio.id,
        valor_inicial=1000.0,
        meta_reducao_percentual=20.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        descricao='Meta de teste para reduu00e7u00e3o de desperdu00edcios',
        responsavel='Gerente Teste',
        acoes_propostas='Au00e7u00f5es de teste para reduu00e7u00e3o'
    )
    session.add(meta)
    session.commit()
    
    # READ: Verificar se foi salvo corretamente
    meta_db = session.query(MetaDesperdicio).filter_by(id=meta.id).first()
    assert meta_db is not None
    assert meta_db.meta_reducao_percentual == 20.0
    assert meta_db.valor_inicial == 1000.0
    assert meta_db.responsavel == 'Gerente Teste'
    
    # UPDATE: Atualizar valores
    meta_db.meta_reducao_percentual = 25.0
    meta_db.acoes_propostas = 'Au00e7u00f5es atualizadas de teste'
    session.commit()
    
    # Verificar atualizau00e7u00e3o
    meta_atualizada = session.query(MetaDesperdicio).filter_by(id=meta.id).first()
    assert meta_atualizada.meta_reducao_percentual == 25.0
    assert meta_atualizada.acoes_propostas == 'Au00e7u00f5es atualizadas de teste'
    
    # DELETE: Remover registro
    session.delete(meta_db)
    session.commit()
    
    # Verificar remou00e7u00e3o
    meta_removida = session.query(MetaDesperdicio).filter_by(id=meta.id).first()
    assert meta_removida is None

def test_meta_desperdicio_calculo_valor_absoluto(session, categoria_desperdicio):
    """Testa o cu00e1lculo do valor absoluto da meta de reduu00e7u00e3o"""
    # Criar meta com 20% de reduu00e7u00e3o
    meta = MetaDesperdicio(
        categoria_id=categoria_desperdicio.id,
        valor_inicial=1000.0,
        meta_reducao_percentual=20.0,
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=30)
    )
    session.add(meta)
    session.commit()
    
    # Verificar cu00e1lculo do valor absoluto
    assert meta.meta_valor_absoluto() == 800.0  # 1000 - (1000 * 20%)
    
    # Atualizar percentual e verificar novamente
    meta.meta_reducao_percentual = 50.0
    session.commit()
    assert meta.meta_valor_absoluto() == 500.0  # 1000 - (1000 * 50%)
    
    # Testar valor mu00ednimo (0%)
    meta.meta_reducao_percentual = 0.0
    session.commit()
    assert meta.meta_valor_absoluto() == 1000.0  # Sem reduu00e7u00e3o
    
    # Testar valor mu00e1ximo (100%)
    meta.meta_reducao_percentual = 100.0
    session.commit()
    assert meta.meta_valor_absoluto() == 0.0  # Reduu00e7u00e3o total

def test_meta_desperdicio_progresso(session, categoria_desperdicio, produto_teste):
    """Testa o cu00e1lculo de progresso da meta de reduu00e7u00e3o"""
    data_inicio = date.today() - timedelta(days=15)
    data_fim = date.today() + timedelta(days=15)
    
    # Criar meta
    meta = MetaDesperdicio(
        categoria_id=categoria_desperdicio.id,
        valor_inicial=1000.0,
        meta_reducao_percentual=20.0,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    session.add(meta)
    
    # Criar alguns registros de desperdu00edcio para a categoria
    for i in range(5):
        # Registros dentro do peru00edodo da meta
        registro = RegistroDesperdicio(
            categoria_id=categoria_desperdicio.id,
            produto_id=produto_teste.id,
            quantidade=1.0,
            unidade_medida='kg',
            valor_estimado=50.0,  # 250.0 no total
            data_registro=data_inicio + timedelta(days=i)
        )
        session.add(registro)
    session.commit()
    
    # Calcular progresso
    progresso = meta.progresso_atual()
    
    # Verificar resultados
    assert isinstance(progresso, dict)
    assert progresso['valor_meta'] == 800.0
    assert progresso['valor_atual'] == 250.0
    assert progresso['percentual_meta'] == 20.0
    assert progresso['percentual_concluido'] == 75.0  # Reduziu 750 de 1000, que u00e9 75%
    assert progresso['status'] == 'em_progresso'
    
    # Adicionar mais registros para ultrapassar a meta
    for i in range(3):
        registro = RegistroDesperdicio(
            categoria_id=categoria_desperdicio.id,
            produto_id=produto_teste.id,
            quantidade=1.0,
            unidade_medida='kg',
            valor_estimado=200.0,  # 600.0 adicionais, total 850.0
            data_registro=data_inicio + timedelta(days=10+i)
        )
        session.add(registro)
    session.commit()
    
    # Recalcular progresso
    progresso_atualizado = meta.progresso_atual()
    
    # Verificar resultados
    assert progresso_atualizado['valor_atual'] == 850.0
    # A meta era reduzir para 800, mas estu00e1 em 850, entu00e3o nu00e3o atingiu
    assert progresso_atualizado['status'] == 'atrasado'
    # Calculando percentual: conseguimos reduzir 150 de 1000, que u00e9 15%
    assert progresso_atualizado['percentual_concluido'] == 15.0
