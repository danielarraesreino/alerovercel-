import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.models.modelo_estoque import EstoqueMovimentacao
from app.models.modelo_produto import Produto
from app.extensions import db

@pytest.fixture
def mock_db_session():
    """Mock para o db.session"""
    with patch('app.models.modelo_estoque.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def mock_produto():
    """Mock para um produto"""
    produto = MagicMock()
    produto.id = 1
    produto.nome = 'Produto Teste'
    produto.unidade_medida = 'kg'
    produto.estoque_atual = 10.0
    produto.estoque_minimo = 5.0
    produto.preco_unitario = 15.0
    return produto

def test_estoque_movimentacao_criacao():
    """Testa a criação básica de uma movimentação de estoque"""
    # Teste de entrada
    entrada = EstoqueMovimentacao(
        produto_id=1,
        quantidade=5.0,
        tipo='entrada',
        data_movimentacao=datetime.now(),
        referencia='NF 12345',
        valor_unitario=20.0
    )
    
    assert entrada.produto_id == 1
    assert entrada.quantidade == 5.0
    assert entrada.tipo == 'entrada'
    assert entrada.referencia == 'NF 12345'
    assert float(entrada.valor_unitario) == 20.0
    
    # Teste de saída
    saida = EstoqueMovimentacao(
        produto_id=1,
        quantidade=2.0,
        tipo='saída',
        data_movimentacao=datetime.now(),
        referencia='Pedido 789'
    )
    
    assert saida.produto_id == 1
    assert saida.quantidade == 2.0
    assert saida.tipo == 'saída'
    assert saida.referencia == 'Pedido 789'

def test_valor_total():
    """Testa o cálculo de valor total da movimentação"""
    # Movimentação com valor unitário
    mov_com_valor = EstoqueMovimentacao(
        produto_id=1,
        quantidade=5.0,
        tipo='entrada',
        valor_unitario=10.0
    )
    
    assert mov_com_valor.valor_total == 50.0  # 5 * 10
    
    # Movimentação sem valor unitário
    mov_sem_valor = EstoqueMovimentacao(
        produto_id=1,
        quantidade=5.0,
        tipo='saída',
        valor_unitario=None
    )
    
    assert mov_sem_valor.valor_total is None

def test_registrar_entrada(mock_db_session, mock_produto):
    """Testa o método de classe para registrar entrada de estoque"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Configurar mock para retornar o produto
        mock_query.get.return_value = mock_produto
        
        # Registrar entrada
        movimento = EstoqueMovimentacao.registrar_entrada(
            produto_id=1, 
            quantidade=5.0,
            referencia='NF 54321',
            valor_unitario=18.0,
            observacao='Teste de entrada'
        )
        
        # Verificar se o produto foi atualizado corretamente
        assert mock_produto.estoque_atual == 15.0  # 10 + 5
        assert mock_produto.preco_unitario == 18.0  # Atualizado para o novo valor
        
        # Verificar se a transação foi confirmada
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        
        # Verificar se a movimentação foi criada corretamente
        assert movimento.produto_id == 1
        assert movimento.quantidade == 5.0
        assert movimento.tipo == 'entrada'
        assert float(movimento.valor_unitario) == 18.0
        assert movimento.observacao == 'Teste de entrada'

def test_registrar_entrada_sem_produto(mock_db_session):
    """Testa o método de registrar entrada quando o produto não existe"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Configurar mock para retornar None (produto não existe)
        mock_query.get.return_value = None
        
        # Registrar entrada
        movimento = EstoqueMovimentacao.registrar_entrada(
            produto_id=999, 
            quantidade=5.0,
            referencia='NF Inexistente',
            valor_unitario=20.0
        )
        
        # A movimentação deve ser criada mesmo sem produto
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert movimento.produto_id == 999
        assert movimento.quantidade == 5.0
        assert float(movimento.valor_unitario) == 20.0

def test_registrar_saida(mock_db_session, mock_produto):
    """Testa o método de classe para registrar saída de estoque"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Configurar mock para retornar o produto
        mock_query.get.return_value = mock_produto
        
        # Registrar saída
        movimento = EstoqueMovimentacao.registrar_saida(
            produto_id=1, 
            quantidade=3.0,
            referencia='Pedido 123',
            observacao='Teste de saída'
        )
        
        # Verificar se o produto foi atualizado corretamente
        assert mock_produto.estoque_atual == 7.0  # 10 - 3
        
        # Verificar se a transação foi confirmada
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        
        # Verificar se a movimentação foi criada corretamente
        assert movimento.produto_id == 1
        assert movimento.quantidade == 3.0
        assert movimento.tipo == 'saída'
        assert float(movimento.valor_unitario) == 15.0  # Valor do produto
        assert movimento.observacao == 'Teste de saída'

def test_registrar_saida_estoque_insuficiente(mock_produto):
    """Testa o método de saída quando o estoque é insuficiente"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Configurar mock para retornar o produto
        mock_query.get.return_value = mock_produto
        
        # Tentar registrar saída maior que o estoque disponível
        with pytest.raises(ValueError) as excinfo:
            EstoqueMovimentacao.registrar_saida(
                produto_id=1, 
                quantidade=15.0,  # Estoque atual é 10
                referencia='Pedido Inválido'
            )
        
        # Verificar mensagem de erro
        assert "Estoque insuficiente" in str(excinfo.value)
        assert "Atual: 10.0" in str(excinfo.value)
        assert "Solicitado: 15.0" in str(excinfo.value)

def test_registrar_saida_produto_inexistente():
    """Testa o método de saída quando o produto não existe"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Configurar mock para retornar None (produto não existe)
        mock_query.get.return_value = None
        
        # Tentar registrar saída
        with pytest.raises(ValueError) as excinfo:
            EstoqueMovimentacao.registrar_saida(
                produto_id=999, 
                quantidade=5.0,
                referencia='Produto Inexistente'
            )
        
        # Verificar mensagem de erro
        assert "Produto com ID 999 não encontrado" in str(excinfo.value)

def test_get_produtos_em_falta():
    """Testa o método para obter produtos em falta"""
    with patch('app.models.modelo_estoque.Produto.query') as mock_query:
        # Produtos abaixo do estoque mínimo
        produto1 = MagicMock(id=1, nome='Produto Em Falta', estoque_atual=2.0, estoque_minimo=5.0)
        produto2 = MagicMock(id=2, nome='Outro Produto Em Falta', estoque_atual=0.0, estoque_minimo=3.0)
        
        # Configurar mock para retornar produtos em falta
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [produto1, produto2]
        
        # Obter produtos em falta
        produtos_em_falta = EstoqueMovimentacao.get_produtos_em_falta()
        
        # Verificar resultado
        assert len(produtos_em_falta) == 2
        assert produtos_em_falta[0].id == 1
        assert produtos_em_falta[1].id == 2

def test_repr(mock_produto):
    """Testa a representação em string do modelo"""
    # Criar movimentação com mock de produto
    movimento = EstoqueMovimentacao(
        produto_id=1,
        quantidade=5.0,
        tipo='entrada'
    )
    movimento.produto = mock_produto
    
    # Verificar representação
    repr_str = repr(movimento)
    assert 'EstoqueMovimentacao' in repr_str
    assert 'entrada' in repr_str
    assert '5.0' in repr_str
    assert 'kg' in repr_str
    assert 'Produto Teste' in repr_str

def test_criar_movimentacao_entrada(session):
    """Testa a criação de uma movimentação de entrada"""
    # Criar produto
    produto = Produto(
        nome="Arroz",
        unidade="kg",
        preco_unitario=Decimal("5.00"),
        estoque_atual=0
    )
    session.add(produto)
    session.commit()
    
    # Criar movimentação
    movimentacao = EstoqueMovimentacao(
        produto_id=produto.id,
        quantidade=50,
        tipo="entrada",
        referencia="NF 123",
        valor_unitario=Decimal("5.00")
    )
    session.add(movimentacao)
    session.commit()
    
    assert movimentacao.id is not None
    assert movimentacao.quantidade == 50
    assert movimentacao.tipo == "entrada"
    assert movimentacao.valor_total == Decimal("250.00")
    assert produto.estoque_atual == 50

def test_criar_movimentacao_saida(session):
    """Testa a criação de uma movimentação de saída"""
    # Criar produto
    produto = Produto(
        nome="Feijão",
        unidade="kg",
        preco_unitario=Decimal("8.00"),
        estoque_atual=100
    )
    session.add(produto)
    session.commit()
    
    # Criar movimentação
    movimentacao = EstoqueMovimentacao(
        produto_id=produto.id,
        quantidade=30,
        tipo="saída",
        referencia="Pedido 456"
    )
    session.add(movimentacao)
    session.commit()
    
    assert movimentacao.id is not None
    assert movimentacao.quantidade == 30
    assert movimentacao.tipo == "saída"
    assert movimentacao.valor_total == Decimal("240.00")
    assert produto.estoque_atual == 70

def test_registrar_entrada(session):
    """Testa o método de classe registrar_entrada"""
    # Criar produto
    produto = Produto(
        nome="Açúcar",
        unidade="kg",
        preco_unitario=Decimal("4.00"),
        estoque_atual=0
    )
    session.add(produto)
    session.commit()
    
    # Registrar entrada
    movimento = EstoqueMovimentacao.registrar_entrada(
        produto_id=produto.id,
        quantidade=25,
        referencia="NF 789",
        valor_unitario=Decimal("4.00")
    )
    
    assert movimento.id is not None
    assert movimento.quantidade == 25
    assert movimento.tipo == "entrada"
    assert produto.estoque_atual == 25
    assert produto.preco_unitario == Decimal("4.00")

def test_registrar_saida(session):
    """Testa o método de classe registrar_saida"""
    # Criar produto
    produto = Produto(
        nome="Sal",
        unidade="kg",
        preco_unitario=Decimal("2.00"),
        estoque_atual=50
    )
    session.add(produto)
    session.commit()
    
    # Registrar saída
    movimento = EstoqueMovimentacao.registrar_saida(
        produto_id=produto.id,
        quantidade=20,
        referencia="Pedido 101"
    )
    
    assert movimento.id is not None
    assert movimento.quantidade == 20
    assert movimento.tipo == "saída"
    assert produto.estoque_atual == 30

def test_registrar_saida_estoque_insuficiente(session):
    """Testa tentativa de saída com estoque insuficiente"""
    # Criar produto
    produto = Produto(
        nome="Farinha",
        unidade="kg",
        preco_unitario=Decimal("3.00"),
        estoque_atual=10
    )
    session.add(produto)
    session.commit()
    
    # Tentar registrar saída maior que estoque
    with pytest.raises(ValueError):
        EstoqueMovimentacao.registrar_saida(
            produto_id=produto.id,
            quantidade=20,
            referencia="Pedido 102"
        )

def test_get_produtos_em_falta(session):
    """Testa a busca de produtos em falta"""
    # Criar produtos
    produto1 = Produto(
        nome="Arroz",
        unidade="kg",
        preco_unitario=Decimal("5.00"),
        estoque_minimo=10,
        estoque_atual=5
    )
    produto2 = Produto(
        nome="Feijão",
        unidade="kg",
        preco_unitario=Decimal("8.00"),
        estoque_minimo=5,
        estoque_atual=10
    )
    session.add_all([produto1, produto2])
    session.commit()
    
    # Buscar produtos em falta
    produtos_falta = EstoqueMovimentacao.get_produtos_em_falta()
    assert len(produtos_falta) == 1
    assert produtos_falta[0].nome == "Arroz"

def test_movimentacao_to_dict(session):
    """Testa a conversão da movimentação para dicionário"""
    # Criar produto
    produto = Produto(
        nome="Teste",
        unidade="kg",
        preco_unitario=Decimal("10.00"),
        estoque_atual=0
    )
    session.add(produto)
    session.commit()
    
    # Criar movimentação
    movimentacao = EstoqueMovimentacao(
        produto_id=produto.id,
        quantidade=5,
        tipo="entrada",
        referencia="Teste",
        valor_unitario=Decimal("10.00")
    )
    session.add(movimentacao)
    session.commit()
    
    mov_dict = movimentacao.to_dict()
    assert mov_dict['quantidade'] == 5
    assert mov_dict['tipo'] == "entrada"
    assert mov_dict['referencia'] == "Teste"
    assert mov_dict['valor_unitario'] == 10.00
    assert mov_dict['valor_total'] == 50.00
    assert mov_dict['produto']['nome'] == "Teste"

def test_movimentacao_constraints(session):
    """Testa as restrições do modelo de movimentação"""
    # Criar produto
    produto = Produto(
        nome="Teste",
        unidade="kg",
        preco_unitario=Decimal("5.00")
    )
    session.add(produto)
    session.commit()
    
    # Testar quantidade negativa
    with pytest.raises(Exception):
        movimentacao = EstoqueMovimentacao(
            produto_id=produto.id,
            quantidade=-10,
            tipo="entrada"
        )
        session.add(movimentacao)
        session.commit()
    
    # Testar tipo inválido
    with pytest.raises(Exception):
        movimentacao = EstoqueMovimentacao(
            produto_id=produto.id,
            quantidade=10,
            tipo="invalido"
        )
        session.add(movimentacao)
        session.commit()
    
    # Testar valor unitário negativo
    with pytest.raises(Exception):
        movimentacao = EstoqueMovimentacao(
            produto_id=produto.id,
            quantidade=10,
            tipo="entrada",
            valor_unitario=Decimal("-5.00")
        )
        session.add(movimentacao)
        session.commit()
