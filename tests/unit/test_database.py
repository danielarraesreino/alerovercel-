import pytest
import sqlalchemy as sa
from app import db
from app.models.modelo_produto import Produto
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
import datetime

def test_conexao_banco_dados(app):
    """Testa se a conexu00e3o com o banco de dados estu00e1 funcionando"""
    with app.app_context():
        # Verificar se podemos executar uma consulta simples
        result = db.session.execute(sa.text("SELECT 1")).scalar()
        assert result == 1

def test_migracao_schema(app):
    """Testa se o esquema do banco de dados corresponde aos modelos definidos"""
    with app.app_context():
        # Verificar se as tabelas principais existem
        inspector = sa.inspect(db.engine)
        tabelas = inspector.get_table_names()
        
        # Verificar se as tabelas principais foram criadas
        assert 'produto' in tabelas
        assert 'historico_vendas' in tabelas
        assert 'previsao_demanda' in tabelas
        assert 'fator_sazonalidade' in tabelas
        assert 'categoria_desperdicio' in tabelas
        assert 'registro_desperdicio' in tabelas
        assert 'meta_desperdicio' in tabelas

def test_integridade_referencial(session):
    """Testa a integridade referencial entre tabelas"""
    # Criar um produto de teste
    produto = Produto(
        nome="Produto para Teste de Integridade",
        descricao="Produto para testar integridade referencial",
        unidade="un",
        preco_custo=10.0,
        preco_venda=15.0,
        codigo_barras="9999999999999",
        estoque_minimo=5,
        estoque_atual=10
    )
    session.add(produto)
    session.commit()
    
    # Criar um registro de histu00f3rico para este produto
    venda = HistoricoVendas(
        data_venda=datetime.datetime.now().date(),
        produto_id=produto.id,
        quantidade=5,
        valor=75.0
    )
    session.add(venda)
    session.commit()
    
    # Criar uma categoria de desperdu00edcio
    categoria = CategoriaDesperdicio(
        nome="Categoria para Teste de Integridade",
        descricao="Categoria para testar integridade referencial",
        cor="#AABBCC"
    )
    session.add(categoria)
    session.commit()
    
    # Criar um registro de desperdu00edcio
    registro = RegistroDesperdicio(
        categoria_id=categoria.id,
        produto_id=produto.id,
        quantidade=2.0,
        unidade="un",
        valor=20.0,
        data_registro=datetime.datetime.now().date(),
        observacao="Registro para teste de integridade referencial"
    )
    session.add(registro)
    session.commit()
    
    # Verificar as relau00e7u00f5es
    # Verificar relau00e7u00e3o produto -> venda
    venda_db = session.query(HistoricoVendas).filter_by(id=venda.id).first()
    assert venda_db is not None
    assert venda_db.produto_id == produto.id
    
    # Verificar relau00e7u00e3o produto -> registro_desperdicio
    registro_db = session.query(RegistroDesperdicio).filter_by(id=registro.id).first()
    assert registro_db is not None
    assert registro_db.produto_id == produto.id
    
    # Verificar relau00e7u00e3o categoria -> registro_desperdicio
    assert registro_db.categoria_id == categoria.id

def test_cascata_exclusao(session):
    """Testa a exclusu00e3o em cascata entre tabelas relacionadas"""
    # Criar um produto de teste
    produto = Produto(
        nome="Produto para Teste de Cascata",
        descricao="Produto para testar exclusu00e3o em cascata",
        unidade="kg",
        preco_custo=8.0,
        preco_venda=12.0,
        codigo_barras="8888888888888",
        estoque_minimo=3,
        estoque_atual=8
    )
    session.add(produto)
    session.commit()
    
    # Criar um registro de histu00f3rico para este produto
    venda = HistoricoVendas(
        data_venda=datetime.datetime.now().date(),
        produto_id=produto.id,
        quantidade=4,
        valor=48.0
    )
    session.add(venda)
    session.commit()
    
    # Verificar se o registro foi criado
    assert session.query(HistoricoVendas).filter_by(produto_id=produto.id).count() == 1
    
    # Excluir o produto e verificar se o registro de histu00f3rico tambu00e9m u00e9 exclu00eddo
    session.delete(produto)
    session.commit()
    
    # Verificar se o registro de histu00f3rico foi exclu00eddo
    assert session.query(HistoricoVendas).filter_by(produto_id=produto.id).count() == 0

def test_constraints_unicidade(session):
    """Testa as restrições de unicidade no banco de dados"""
    # Criar uma categoria de desperdu00edcio com nome u00fanico
    categoria = CategoriaDesperdicio(
        nome="Categoria Única",
        descricao="Categoria para testar unicidade",
        cor="#112233"
    )
    session.add(categoria)
    session.commit()
    
    # Tentar criar outra categoria com o mesmo nome
    categoria_duplicada = CategoriaDesperdicio(
        nome="Categoria Única",  # Mesmo nome
        descricao="Outra descrição",
        cor="#445566"
    )
    session.add(categoria_duplicada)
    
    # Deve lançar exceção ao tentar commitar
    with pytest.raises(Exception):
        session.commit()
    
    # Fazer rollback para limpar a sessão
    session.rollback()

def test_indices_desempenho(app):
    """Testa a existência de índices importantes para desempenho"""
    with app.app_context():
        inspector = sa.inspect(db.engine)
        
        # Verificar índices na tabela historico_vendas
        indices_vendas = inspector.get_indexes('historico_vendas')
        nomes_indices_vendas = [indice['name'] for indice in indices_vendas]
        
        # Deve haver índices para data_venda e produto_id
        assert any('data_venda' in nome for nome in nomes_indices_vendas) or \
               any('produto_id' in nome for nome in nomes_indices_vendas)
        
        # Verificar índices na tabela registro_desperdicio
        indices_desperdicio = inspector.get_indexes('registro_desperdicio')
        nomes_indices_desperdicio = [indice['name'] for indice in indices_desperdicio]
        
        # Deve haver índices para data_registro, categoria_id e produto_id
        assert any('data_registro' in nome for nome in nomes_indices_desperdicio) or \
               any('categoria_id' in nome for nome in nomes_indices_desperdicio) or \
               any('produto_id' in nome for nome in nomes_indices_desperdicio)
