import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_produto import Produto
from app.models.modelo_fornecedor import Fornecedor
from app.extensions import db

@pytest.fixture
def mock_fornecedor():
    """Mock para um fornecedor"""
    fornecedor = MagicMock()
    fornecedor.id = 1
    fornecedor.razao_social = "Fornecedor Teste"
    fornecedor.cnpj = "12345678901234"
    return fornecedor

@pytest.fixture
def mock_produto():
    """Mock para um produto"""
    produto = MagicMock()
    produto.id = 1
    produto.nome = "Produto Teste"
    produto.unidade_medida = "kg"
    produto.estoque_atual = 10.0
    produto.preco_unitario = 15.0
    return produto

@pytest.fixture
def mock_nf_nota(mock_fornecedor):
    """Mock para uma nota fiscal"""
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="12345",
        serie="1",
        data_emissao=datetime(2023, 5, 15),
        valor_total=Decimal('1000.00'),
        valor_produtos=Decimal('900.00'),
        valor_frete=Decimal('50.00'),
        valor_seguro=Decimal('10.00'),
        valor_desconto=Decimal('20.00'),
        valor_impostos=Decimal('80.00'),
        fornecedor_id=mock_fornecedor.id,
        xml_data="<xml>Teste</xml>"
    )
    nota.fornecedor = mock_fornecedor
    nota.itens = []
    return nota

@pytest.fixture
def mock_nf_item(mock_nf_nota, mock_produto):
    """Mock para um item de nota fiscal"""
    item = NFItem(
        nf_nota_id=mock_nf_nota.id,
        produto_id=mock_produto.id,
        num_item=1,
        quantidade=2.5,
        valor_unitario=Decimal('100.00'),
        valor_total=Decimal('250.00'),
        unidade_medida="kg",
        cfop="5102",
        ncm="12345678",
        percentual_icms=Decimal('18.00'),
        valor_icms=Decimal('45.00'),
        percentual_ipi=Decimal('5.00'),
        valor_ipi=Decimal('12.50')
    )
    item.nota = mock_nf_nota
    item.produto = mock_produto
    mock_nf_nota.itens.append(item)
    return item

def test_nf_nota_criacao(mock_fornecedor):
    """Testa a criação básica de uma nota fiscal"""
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="12345",
        serie="1",
        data_emissao=datetime(2023, 5, 15),
        valor_total=Decimal('1000.00'),
        valor_produtos=Decimal('900.00'),
        valor_frete=Decimal('50.00'),
        valor_seguro=Decimal('10.00'),
        valor_desconto=Decimal('20.00'),
        valor_impostos=Decimal('80.00'),
        fornecedor_id=mock_fornecedor.id,
        xml_data="<xml>Teste</xml>"
    )
    
    assert nota.chave_acesso == "12345678901234567890123456789012345678901234"
    assert nota.numero == "12345"
    assert nota.serie == "1"
    assert nota.data_emissao == datetime(2023, 5, 15)
    assert nota.valor_total == Decimal('1000.00')
    assert nota.valor_produtos == Decimal('900.00')
    assert nota.valor_frete == Decimal('50.00')
    assert nota.valor_seguro == Decimal('10.00')
    assert nota.valor_desconto == Decimal('20.00')
    assert nota.valor_impostos == Decimal('80.00')
    assert nota.fornecedor_id == mock_fornecedor.id
    assert nota.xml_data == "<xml>Teste</xml>"

def test_nf_item_criacao(mock_nf_nota, mock_produto):
    """Testa a criação básica de um item de nota fiscal"""
    item = NFItem(
        nf_nota_id=mock_nf_nota.id,
        produto_id=mock_produto.id,
        num_item=1,
        quantidade=2.5,
        valor_unitario=Decimal('100.00'),
        valor_total=Decimal('250.00'),
        unidade_medida="kg",
        cfop="5102",
        ncm="12345678",
        percentual_icms=Decimal('18.00'),
        valor_icms=Decimal('45.00'),
        percentual_ipi=Decimal('5.00'),
        valor_ipi=Decimal('12.50')
    )
    
    assert item.nf_nota_id == mock_nf_nota.id
    assert item.produto_id == mock_produto.id
    assert item.num_item == 1
    assert item.quantidade == 2.5
    assert item.valor_unitario == Decimal('100.00')
    assert item.valor_total == Decimal('250.00')
    assert item.unidade_medida == "kg"
    assert item.cfop == "5102"
    assert item.ncm == "12345678"
    assert item.percentual_icms == Decimal('18.00')
    assert item.valor_icms == Decimal('45.00')
    assert item.percentual_ipi == Decimal('5.00')
    assert item.valor_ipi == Decimal('12.50')

def test_nf_nota_relacionamentos(mock_nf_nota, mock_nf_item):
    """Testa os relacionamentos da nota fiscal"""
    # Verificar se o item está na lista de itens da nota
    assert mock_nf_item in mock_nf_nota.itens
    
    # Verificar se o relacionamento com fornecedor está funcionando
    assert mock_nf_nota.fornecedor.razao_social == "Fornecedor Teste"

def test_nf_item_relacionamentos(mock_nf_item):
    """Testa os relacionamentos do item de nota fiscal"""
    # Verificar se o relacionamento com a nota está funcionando
    assert mock_nf_item.nota.numero == "12345"
    
    # Verificar se o relacionamento com o produto está funcionando
    assert mock_nf_item.produto.nome == "Produto Teste"

def test_nf_nota_get_data_formatada(mock_nf_nota):
    """Testa o método get_data_formatada"""
    assert mock_nf_nota.get_data_formatada() == "15/05/2023"

def test_nf_nota_valor_liquido(mock_nf_nota):
    """Testa a property valor_liquido"""
    # valor_total (1000) - valor_desconto (20) = 980
    assert mock_nf_nota.valor_liquido == 980.0

def test_nf_item_valor_com_impostos(mock_nf_item):
    """Testa a property valor_com_impostos"""
    # valor_total (250) + valor_ipi (12.50) = 262.50
    assert mock_nf_item.valor_com_impostos == 262.5

def test_nf_nota_repr(mock_nf_nota, mock_fornecedor):
    """Testa a representação em string do modelo NFNota"""
    expected = f"<NFNota 12345/1 - {mock_fornecedor.razao_social}>"
    assert repr(mock_nf_nota) == expected

def test_nf_item_repr(mock_nf_item, mock_produto):
    """Testa a representação em string do modelo NFItem"""
    expected = f"<NFItem {mock_nf_item.num_item}: {mock_produto.nome}, Qtd: {mock_nf_item.quantidade} {mock_nf_item.unidade_medida}>"
    assert repr(mock_nf_item) == expected

def test_nf_nota_atualizar_estoque(mock_nf_nota, mock_nf_item):
    """Testa o método atualizar_estoque"""
    with patch('app.models.modelo_nfe.EstoqueMovimentacao') as mock_estoque:
        # Configurar o mock
        mock_estoque.registrar_entrada.return_value = MagicMock()
        
        # Chamar o método
        mock_nf_nota.atualizar_estoque()
        
        # Verificar se o método registrar_entrada foi chamado corretamente
        mock_estoque.registrar_entrada.assert_called_once_with(
            produto_id=mock_nf_item.produto_id,
            quantidade=mock_nf_item.quantidade,
            valor_unitario=mock_nf_item.valor_unitario,
            referencia=f"NF {mock_nf_nota.numero}",
            ref_id=mock_nf_nota.id,
            observacao=None
        )

def test_criar_nota_fiscal(session):
    """Testa a criação de uma nota fiscal"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234",
        email="fornecedor@teste.com",
        telefone="11999999999"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar nota fiscal
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=date.today(),
        data_entrada=date.today(),
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00"),
        valor_frete=Decimal("50.00"),
        valor_seguro=Decimal("10.00"),
        valor_desconto=Decimal("100.00"),
        valor_outras_despesas=Decimal("20.00"),
        valor_ipi=Decimal("50.00"),
        valor_icms=Decimal("180.00"),
        valor_pis=Decimal("6.50"),
        valor_cofins=Decimal("30.00"),
        observacoes="Nota fiscal de teste"
    )
    session.add(nota)
    session.commit()
    
    assert nota.id is not None
    assert nota.chave_acesso == "12345678901234567890123456789012345678901234"
    assert nota.numero == "123456"
    assert nota.serie == "1"
    assert nota.valor_total == Decimal("1000.00")
    assert nota.valor_frete == Decimal("50.00")
    assert nota.valor_seguro == Decimal("10.00")
    assert nota.valor_desconto == Decimal("100.00")
    assert nota.valor_outras_despesas == Decimal("20.00")
    assert nota.valor_ipi == Decimal("50.00")
    assert nota.valor_icms == Decimal("180.00")
    assert nota.valor_pis == Decimal("6.50")
    assert nota.valor_cofins == Decimal("30.00")
    assert nota.observacoes == "Nota fiscal de teste"
    assert nota.fornecedor_id == fornecedor.id

def test_nota_fiscal_formatar_data(session):
    """Testa a formatação de data da nota fiscal"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar nota fiscal
    data_hoje = date.today()
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=data_hoje,
        data_entrada=data_hoje,
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00")
    )
    session.add(nota)
    session.commit()
    
    assert nota.data_emissao_formatada == data_hoje.strftime("%d/%m/%Y")
    assert nota.data_entrada_formatada == data_hoje.strftime("%d/%m/%Y")

def test_nota_fiscal_to_dict(session):
    """Testa a conversão da nota fiscal para dicionário"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar nota fiscal
    data_hoje = date.today()
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=data_hoje,
        data_entrada=data_hoje,
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00"),
        valor_frete=Decimal("50.00"),
        valor_seguro=Decimal("10.00"),
        valor_desconto=Decimal("100.00"),
        valor_outras_despesas=Decimal("20.00"),
        valor_ipi=Decimal("50.00"),
        valor_icms=Decimal("180.00"),
        valor_pis=Decimal("6.50"),
        valor_cofins=Decimal("30.00")
    )
    session.add(nota)
    session.commit()
    
    nota_dict = nota.to_dict()
    assert nota_dict['numero'] == "123456"
    assert nota_dict['serie'] == "1"
    assert nota_dict['valor_total'] == 1000.00
    assert nota_dict['valor_frete'] == 50.00
    assert nota_dict['valor_seguro'] == 10.00
    assert nota_dict['valor_desconto'] == 100.00
    assert nota_dict['valor_outras_despesas'] == 20.00
    assert nota_dict['valor_ipi'] == 50.00
    assert nota_dict['valor_icms'] == 180.00
    assert nota_dict['valor_pis'] == 6.50
    assert nota_dict['valor_cofins'] == 30.00
    assert nota_dict['fornecedor']['nome'] == "Fornecedor Teste"

def test_criar_item_nota_fiscal(session):
    """Testa a criação de um item de nota fiscal"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar produto
    produto = Produto(
        nome="Produto Teste",
        unidade="UN",
        preco_compra=Decimal("10.00")
    )
    session.add(produto)
    session.commit()
    
    # Criar nota fiscal
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=date.today(),
        data_entrada=date.today(),
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00")
    )
    session.add(nota)
    session.commit()
    
    # Criar item da nota
    item = NFItem(
        nota_id=nota.id,
        produto_id=produto.id,
        quantidade=10,
        valor_unitario=Decimal("10.00"),
        valor_total=Decimal("100.00"),
        aliquota_icms=Decimal("18.00"),
        aliquota_ipi=Decimal("5.00"),
        aliquota_pis=Decimal("0.65"),
        aliquota_cofins=Decimal("3.00"),
        valor_icms=Decimal("18.00"),
        valor_ipi=Decimal("5.00"),
        valor_pis=Decimal("0.65"),
        valor_cofins=Decimal("3.00")
    )
    session.add(item)
    session.commit()
    
    assert item.id is not None
    assert item.nota_id == nota.id
    assert item.produto_id == produto.id
    assert item.quantidade == 10
    assert item.valor_unitario == Decimal("10.00")
    assert item.valor_total == Decimal("100.00")
    assert item.aliquota_icms == Decimal("18.00")
    assert item.aliquota_ipi == Decimal("5.00")
    assert item.aliquota_pis == Decimal("0.65")
    assert item.aliquota_cofins == Decimal("3.00")
    assert item.valor_icms == Decimal("18.00")
    assert item.valor_ipi == Decimal("5.00")
    assert item.valor_pis == Decimal("0.65")
    assert item.valor_cofins == Decimal("3.00")

def test_item_nota_fiscal_calcular_valores(session):
    """Testa o cálculo de valores do item da nota fiscal"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar produto
    produto = Produto(
        nome="Produto Teste",
        unidade="UN",
        preco_compra=Decimal("10.00")
    )
    session.add(produto)
    session.commit()
    
    # Criar nota fiscal
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=date.today(),
        data_entrada=date.today(),
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00")
    )
    session.add(nota)
    session.commit()
    
    # Criar item da nota
    item = NFItem(
        nota_id=nota.id,
        produto_id=produto.id,
        quantidade=10,
        valor_unitario=Decimal("10.00"),
        aliquota_icms=Decimal("18.00"),
        aliquota_ipi=Decimal("5.00"),
        aliquota_pis=Decimal("0.65"),
        aliquota_cofins=Decimal("3.00")
    )
    session.add(item)
    session.commit()
    
    # Calcular valores
    item.calcular_valores()
    
    assert item.valor_total == Decimal("100.00")
    assert item.valor_icms == Decimal("18.00")
    assert item.valor_ipi == Decimal("5.00")
    assert item.valor_pis == Decimal("0.65")
    assert item.valor_cofins == Decimal("3.00")

def test_item_nota_fiscal_to_dict(session):
    """Testa a conversão do item da nota fiscal para dicionário"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar produto
    produto = Produto(
        nome="Produto Teste",
        unidade="UN",
        preco_compra=Decimal("10.00")
    )
    session.add(produto)
    session.commit()
    
    # Criar nota fiscal
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=date.today(),
        data_entrada=date.today(),
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00")
    )
    session.add(nota)
    session.commit()
    
    # Criar item da nota
    item = NFItem(
        nota_id=nota.id,
        produto_id=produto.id,
        quantidade=10,
        valor_unitario=Decimal("10.00"),
        valor_total=Decimal("100.00"),
        aliquota_icms=Decimal("18.00"),
        aliquota_ipi=Decimal("5.00"),
        aliquota_pis=Decimal("0.65"),
        aliquota_cofins=Decimal("3.00"),
        valor_icms=Decimal("18.00"),
        valor_ipi=Decimal("5.00"),
        valor_pis=Decimal("0.65"),
        valor_cofins=Decimal("3.00")
    )
    session.add(item)
    session.commit()
    
    item_dict = item.to_dict()
    assert item_dict['quantidade'] == 10
    assert item_dict['valor_unitario'] == 10.00
    assert item_dict['valor_total'] == 100.00
    assert item_dict['aliquota_icms'] == 18.00
    assert item_dict['aliquota_ipi'] == 5.00
    assert item_dict['aliquota_pis'] == 0.65
    assert item_dict['aliquota_cofins'] == 3.00
    assert item_dict['valor_icms'] == 18.00
    assert item_dict['valor_ipi'] == 5.00
    assert item_dict['valor_pis'] == 0.65
    assert item_dict['valor_cofins'] == 3.00
    assert item_dict['produto']['nome'] == "Produto Teste"

def test_nota_fiscal_atualizar_estoque(session):
    """Testa a atualização de estoque ao registrar uma nota fiscal"""
    # Criar fornecedor
    fornecedor = Fornecedor(
        nome="Fornecedor Teste",
        cnpj="12345678901234"
    )
    session.add(fornecedor)
    session.commit()
    
    # Criar produto
    produto = Produto(
        nome="Produto Teste",
        unidade="UN",
        preco_compra=Decimal("10.00"),
        estoque_atual=0
    )
    session.add(produto)
    session.commit()
    
    # Criar nota fiscal
    nota = NFNota(
        chave_acesso="12345678901234567890123456789012345678901234",
        numero="123456",
        serie="1",
        data_emissao=date.today(),
        data_entrada=date.today(),
        fornecedor_id=fornecedor.id,
        valor_total=Decimal("1000.00")
    )
    session.add(nota)
    session.commit()
    
    # Criar item da nota
    item = NFItem(
        nota_id=nota.id,
        produto_id=produto.id,
        quantidade=10,
        valor_unitario=Decimal("10.00"),
        valor_total=Decimal("100.00")
    )
    session.add(item)
    session.commit()
    
    # Atualizar estoque
    nota.atualizar_estoque()
    session.commit()
    
    # Verificar estoque atualizado
    produto_atualizado = session.query(Produto).get(produto.id)
    assert produto_atualizado.estoque_atual == 10
