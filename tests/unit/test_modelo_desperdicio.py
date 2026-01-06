import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_produto import Produto
from app.models.modelo_prato import Prato

@pytest.fixture
def setup_produto(session):
    """Fixture para criar um produto para testes"""
    produto = Produto(
        nome='Produto de Teste',
        descricao='Produto para testes',
        preco_unitario=20.0,
        codigo='123456789',
        unidade_medida='kg',
        estoque_minimo=5,
        estoque_atual=15
    )
    session.add(produto)
    session.commit()
    return produto

@pytest.mark.parametrize(
    "nome,descricao,cor",
    [
        ("Expirado", "Produtos vencidos", "#FF0000"),
        ("Sobra", "Sobra de produu00e7u00e3o", "#FFA500"),
        ("Dano", "Produtos danificados", "#FFFF00"),
    ],
)
def test_categoria_desperdicio_create(session, nome, descricao, cor):
    """Testa a criau00e7u00e3o de categorias de desperdu00edcio"""
    # Arrange & Act
    categoria = CategoriaDesperdicio(
        nome=nome,
        descricao=descricao,
        cor=cor
    )
    session.add(categoria)
    session.commit()
    
    # Assert
    assert categoria.id is not None
    assert categoria.nome == nome
    assert categoria.descricao == descricao
    assert categoria.cor == cor

def test_registro_desperdicio_create(session, setup_produto):
    """Testa a criau00e7u00e3o de registros de desperdu00edcio"""
    # Arrange
    categoria = CategoriaDesperdicio(
        nome="Teste", 
        descricao="Categoria de teste", 
        cor="#0000FF"
    )
    session.add(categoria)
    session.commit()
    
    # Act
    data_registro = datetime.now()
    registro = RegistroDesperdicio(
        categoria_id=categoria.id,
        produto_id=setup_produto.id,
        quantidade=5.0,
        unidade_medida="kg",
        valor_estimado=50.0,
        data_registro=data_registro,
        motivo="Vencido",
        responsavel="Testador",
        local="Estoque",
        descricao="Teste de registro"
    )
    session.add(registro)
    session.commit()
    
    # Assert
    assert registro.id is not None
    assert registro.categoria_id == categoria.id
    assert registro.produto_id == setup_produto.id
    assert registro.quantidade == 5.0
    assert registro.unidade_medida == "kg"
    assert registro.valor_estimado == 50.0
    assert registro.data_registro == data_registro
    assert registro.motivo == "Vencido"
    assert registro.responsavel == "Testador"
    assert registro.local == "Estoque"
    assert registro.descricao == "Teste de registro"

def test_meta_desperdicio_create(session):
    """Testa a criau00e7u00e3o de metas de reduu00e7u00e3o de desperdu00edcio"""
    # Arrange & Act
    data_inicio = datetime.now().date()
    data_fim = data_inicio + timedelta(days=30)
    meta = MetaDesperdicio(
        categoria_id=None,  # Meta para todas as categorias
        valor_inicial=1000.0,
        meta_reducao_percentual=20.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        descricao="Reduzir desperdu00edcio em 20%",
        responsavel="Gerente",
        acoes_propostas="Melhorar o controle de estoque e treinamento da equipe"
    )
    session.add(meta)
    session.commit()
    
    # Assert
    assert meta.id is not None
    assert meta.categoria_id is None
    assert meta.valor_inicial == 1000.0
    assert meta.meta_reducao_percentual == 20.0
    assert meta.data_inicio == data_inicio
    assert meta.data_fim == data_fim
    assert meta.descricao == "Reduzir desperdu00edcio em 20%"
    assert meta.responsavel == "Gerente"
    assert meta.acoes_propostas == "Melhorar o controle de estoque e treinamento da equipe"
    
    # Verificar a propriedade que calcula o valor absoluto da meta
    assert meta.meta_valor_absoluto == 800.0

def test_relacionamentos_desperdicio(session, setup_produto):
    """Testa os relacionamentos entre os modelos de desperdu00edcio"""
    # Arrange
    # Criar uma categoria
    categoria = CategoriaDesperdicio(
        nome="Categoria Teste",
        descricao="Categoria para testes",
        cor="#00FF00"
    )
    session.add(categoria)
    session.commit()
    
    # Criar registros associados a essa categoria
    for i in range(3):
        registro = RegistroDesperdicio(
            categoria_id=categoria.id,
            produto_id=setup_produto.id,
            quantidade=i+1.5,
            unidade_medida="kg",
            valor_estimado=(i+1) * 10.0,
            data_registro=datetime.now() - timedelta(days=i),
            motivo="Teste",
            local="Estoque",
            responsavel="Tester",
            descricao=f"Registro de teste {i+1}"
        )
        session.add(registro)
    
    # Criar uma meta para essa categoria
    meta = MetaDesperdicio(
        categoria_id=categoria.id,
        valor_inicial=100.0,
        meta_reducao_percentual=20.0,
        data_inicio=datetime.now().date(),
        data_fim=datetime.now().date() + timedelta(days=30),
        descricao="Meta para categoria de teste",
        responsavel="Gerente de Teste"
    )
    session.add(meta)
    session.commit()
    
    # Act
    categoria_db = session.query(CategoriaDesperdicio).filter_by(id=categoria.id).first()
    registros = session.query(RegistroDesperdicio).filter_by(categoria_id=categoria.id).all()
    metas = session.query(MetaDesperdicio).filter_by(categoria_id=categoria.id).all()
    
    # Assert
    assert categoria_db is not None
    assert len(registros) == 3
    assert len(metas) == 1
    assert metas[0].categoria_id == categoria.id
    
    # Verificar se a relau00e7u00e3o entre categoria e registros estu00e1 funcionando
    assert all(registro.categoria_id == categoria.id for registro in registros)
    
    # Verificar se o relacionamento bidirecional está funcionando
    assert len(categoria_db.registros) == 3
    assert categoria_db.registros[0].categoria.id == categoria.id
    
    # Verificar se o relacionamento com produto está funcionando
    for registro in registros:
        assert registro.produto.id == setup_produto.id
    
    # Verificar se a meta está corretamente relacionada com a categoria
    assert metas[0].categoria.id == categoria.id

def test_criar_categoria_desperdicio(session):
    """Testa a criação de uma categoria de desperdício"""
    categoria = CategoriaDesperdicio(
        nome="Sobras de Preparo",
        descricao="Alimentos que sobraram durante o preparo",
        cor="#FF0000"
    )
    session.add(categoria)
    session.commit()
    
    assert categoria.id is not None
    assert categoria.nome == "Sobras de Preparo"
    assert categoria.ativo is True

def test_criar_registro_desperdicio_produto(session):
    """Testa a criação de um registro de desperdício para produto"""
    # Criar produto
    produto = Produto(
        nome="Arroz",
        unidade="kg",
        preco_unitario=Decimal("5.00")
    )
    session.add(produto)
    session.commit()
    
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Sobras")
    session.add(categoria)
    session.commit()
    
    # Criar registro
    registro = RegistroDesperdicio(
        categoria_id=categoria.id,
        produto_id=produto.id,
        quantidade=2.5,
        unidade="kg",
        valor_estimado=Decimal("12.50"),
        motivo="Preparo excessivo",
        responsavel="João",
        local="Cozinha"
    )
    session.add(registro)
    session.commit()
    
    assert registro.id is not None
    assert registro.quantidade == 2.5
    assert registro.valor_estimado == Decimal("12.50")
    assert registro.item_nome == "Arroz"
    assert registro.tipo_item == "Produto/Insumo"

def test_criar_registro_desperdicio_prato(session):
    """Testa a criação de um registro de desperdício para prato"""
    # Criar prato
    prato = Prato(
        nome="Risoto",
        rendimento=4,
        unidade_rendimento="porções"
    )
    session.add(prato)
    session.commit()
    
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Estragado")
    session.add(categoria)
    session.commit()
    
    # Criar registro
    registro = RegistroDesperdicio(
        categoria_id=categoria.id,
        prato_id=prato.id,
        quantidade=2,
        unidade="porções",
        valor_estimado=Decimal("30.00"),
        motivo="Prato não servido",
        responsavel="Maria",
        local="Salão"
    )
    session.add(registro)
    session.commit()
    
    assert registro.id is not None
    assert registro.quantidade == 2
    assert registro.valor_estimado == Decimal("30.00")
    assert registro.item_nome == "Risoto"
    assert registro.tipo_item == "Prato"

def test_criar_meta_desperdicio(session):
    """Testa a criação de uma meta de desperdício"""
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Sobras")
    session.add(categoria)
    session.commit()
    
    # Criar meta
    meta = MetaDesperdicio(
        descricao="Reduzir sobras em 20%",
        data_inicio=date.today(),
        data_fim=date.today().replace(month=date.today().month + 1),
        categoria_id=categoria.id,
        valor_inicial=100.0,
        valor_meta=80.0,
        meta_reducao_percentual=20.0,
        acoes_propostas="Melhorar planejamento de produção",
        responsavel="Chef"
    )
    session.add(meta)
    session.commit()
    
    assert meta.id is not None
    assert meta.valor_inicial == 100.0
    assert meta.valor_meta == 80.0
    assert meta.meta_reducao_percentual == 20.0
    assert meta.status == "Em Andamento"

def test_meta_desperdicio_progresso(session):
    """Testa o cálculo de progresso da meta de desperdício"""
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Sobras")
    session.add(categoria)
    session.commit()
    
    # Criar meta
    meta = MetaDesperdicio(
        descricao="Reduzir sobras em 50%",
        data_inicio=date.today(),
        data_fim=date.today().replace(month=date.today().month + 1),
        categoria_id=categoria.id,
        valor_inicial=100.0,
        valor_meta=50.0,
        meta_reducao_percentual=50.0
    )
    session.add(meta)
    session.commit()
    
    # Simular progresso
    assert meta.progresso == 0  # Inicialmente 0%
    
    # Simular redução de 25%
    meta.valor_atual = 75.0
    assert meta.progresso == 50  # 50% da meta atingida

def test_registro_desperdicio_validacoes(session):
    """Testa as validações do registro de desperdício"""
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Sobras")
    session.add(categoria)
    session.commit()
    
    # Testar quantidade negativa
    with pytest.raises(Exception):
        registro = RegistroDesperdicio(
            categoria_id=categoria.id,
            quantidade=-1,
            unidade="kg"
        )
        session.add(registro)
        session.commit()
    
    # Testar sem produto ou prato
    with pytest.raises(Exception):
        registro = RegistroDesperdicio(
            categoria_id=categoria.id,
            quantidade=1,
            unidade="kg"
        )
        session.add(registro)
        session.commit()

def test_meta_desperdicio_status(session):
    """Testa os diferentes status possíveis de uma meta de desperdício"""
    # Criar categoria
    categoria = CategoriaDesperdicio(nome="Sobras")
    session.add(categoria)
    session.commit()
    
    # Criar meta
    meta = MetaDesperdicio(
        descricao="Reduzir sobras",
        data_inicio=date.today(),
        data_fim=date.today().replace(month=date.today().month + 1),
        categoria_id=categoria.id,
        valor_inicial=100.0,
        valor_meta=80.0,
        meta_reducao_percentual=20.0
    )
    session.add(meta)
    session.commit()
    
    # Testar status inicial
    assert meta.status == "Em Andamento"
    
    # Testar meta concluída
    meta.data_fim = date.today().replace(day=date.today().day - 1)
    meta.valor_atual = 75.0
    assert meta.status == "Concluída"
    
    # Testar meta atrasada
    meta.valor_atual = 90.0
    assert meta.status == "Atrasada"
    
    # Testar meta cancelada
    meta.ativo = False
    assert meta.status == "Cancelada"
