import pytest
from decimal import Decimal
from datetime import datetime, date
from app.models.modelo_fornecedor import Fornecedor, ContatoFornecedor
from app.models.modelo_produto import Produto

def test_criar_fornecedor(session):
    """Testa a criação de um fornecedor básico"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234",
        email="contato@fornecedor.com",
        telefone="(11) 99999-9999",
        endereco="Rua Teste, 123",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567"
    )
    session.add(fornecedor)
    session.commit()
    
    assert fornecedor.id is not None
    assert fornecedor.nome == "Fornecedor Teste"
    assert fornecedor.cnpj == "12345678901234"
    assert fornecedor.email == "contato@fornecedor.com"
    assert fornecedor.telefone == "(11) 99999-9999"
    assert fornecedor.endereco == "Rua Teste, 123"
    assert fornecedor.cidade == "São Paulo"
    assert fornecedor.estado == "SP"
    assert fornecedor.cep == "01234-567"
    assert fornecedor.ativo is True

def test_fornecedor_com_contatos(session):
    """Testa a criação de um fornecedor com contatos"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    contato1 = ContatoFornecedor(
        fornecedor_id=fornecedor.id,
        nome="João Silva",
        cargo="Vendedor",
        email="joao@fornecedor.com",
        telefone="(11) 98888-8888"
    )
    contato2 = ContatoFornecedor(
        fornecedor_id=fornecedor.id,
        nome="Maria Santos",
        cargo="Gerente",
        email="maria@fornecedor.com",
        telefone="(11) 97777-7777"
    )
    session.add_all([contato1, contato2])
    session.commit()
    
    assert len(fornecedor.contatos) == 2
    assert fornecedor.contatos[0].nome == "João Silva"
    assert fornecedor.contatos[1].nome == "Maria Santos"
    assert fornecedor.contatos[0].cargo == "Vendedor"
    assert fornecedor.contatos[1].cargo == "Gerente"

def test_fornecedor_com_produtos(session):
    """Testa a criação de um fornecedor com produtos"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    produto1 = Produto(
        nome="Produto 1",
        fornecedor_id=fornecedor.id,
        preco_unitario=Decimal("10.00"),
        estoque_atual=100,
        estoque_minimo=20
    )
    produto2 = Produto(
        nome="Produto 2",
        fornecedor_id=fornecedor.id,
        preco_unitario=Decimal("20.00"),
        estoque_atual=50,
        estoque_minimo=10
    )
    session.add_all([produto1, produto2])
    session.commit()
    
    assert len(fornecedor.produtos) == 2
    assert fornecedor.produtos[0].nome == "Produto 1"
    assert fornecedor.produtos[1].nome == "Produto 2"
    assert fornecedor.produtos[0].preco_unitario == Decimal("10.00")
    assert fornecedor.produtos[1].preco_unitario == Decimal("20.00")

def test_fornecedor_to_dict(session):
    """Testa a conversão do fornecedor para dicionário"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234",
        email="contato@fornecedor.com",
        telefone="(11) 99999-9999",
        endereco="Rua Teste, 123",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567"
    )
    session.add(fornecedor)
    session.commit()
    
    fornecedor_dict = fornecedor.to_dict()
    assert fornecedor_dict['nome'] == "Fornecedor Teste"
    assert fornecedor_dict['cnpj'] == "12345678901234"
    assert fornecedor_dict['email'] == "contato@fornecedor.com"
    assert fornecedor_dict['telefone'] == "(11) 99999-9999"
    assert fornecedor_dict['endereco'] == "Rua Teste, 123"
    assert fornecedor_dict['cidade'] == "São Paulo"
    assert fornecedor_dict['estado'] == "SP"
    assert fornecedor_dict['cep'] == "01234-567"
    assert fornecedor_dict['ativo'] is True

def test_contato_to_dict(session):
    """Testa a conversão do contato para dicionário"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    contato = ContatoFornecedor(
        fornecedor_id=fornecedor.id,
        nome="João Silva",
        cargo="Vendedor",
        email="joao@fornecedor.com",
        telefone="(11) 98888-8888"
    )
    session.add(contato)
    session.commit()
    
    contato_dict = contato.to_dict()
    assert contato_dict['nome'] == "João Silva"
    assert contato_dict['cargo'] == "Vendedor"
    assert contato_dict['email'] == "joao@fornecedor.com"
    assert contato_dict['telefone'] == "(11) 98888-8888"

def test_fornecedor_constraints(session):
    """Testa as restrições do fornecedor"""
    # Teste de CNPJ inválido
    with pytest.raises(ValueError):
        fornecedor = Fornecedor(
            nome="Fornecedor Teste",
            cnpj="123"  # CNPJ inválido
        )
        session.add(fornecedor)
        session.commit()
    
    # Teste de email inválido
    with pytest.raises(ValueError):
        fornecedor = Fornecedor(
            nome="Fornecedor Teste",
            cnpj="12345678901234",
            email="email_invalido"  # Email inválido
        )
        session.add(fornecedor)
        session.commit()
    
    # Teste de telefone inválido
    with pytest.raises(ValueError):
        fornecedor = Fornecedor(
            nome="Fornecedor Teste",
            cnpj="12345678901234",
            telefone="123"  # Telefone inválido
        )
        session.add(fornecedor)
        session.commit()

def test_contato_constraints(session):
    """Testa as restrições do contato"""
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Teste de email inválido
    with pytest.raises(ValueError):
        contato = ContatoFornecedor(
            fornecedor_id=fornecedor.id,
            nome="João Silva",
            email="email_invalido"  # Email inválido
        )
        session.add(contato)
        session.commit()
    
    # Teste de telefone inválido
    with pytest.raises(ValueError):
        contato = ContatoFornecedor(
            fornecedor_id=fornecedor.id,
            nome="João Silva",
            telefone="123"  # Telefone inválido
        )
        session.add(contato)
        session.commit() 