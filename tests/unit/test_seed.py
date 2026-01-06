from app.scripts.seed_vegan import seed_vegan_data
from app.models.modelo_produto import Produto
from app.models.modelo_prato import Prato
from app.models.modelo_cardapio import CardapioItem
from app.models.modelo_previsao import HistoricoVendas

def test_seed_vegan_data_success(app, session):
    """
    Testa se o script de seed roda sem erros e popula o banco corretamente.
    Usa um banco de dados vazio (SQLite in-memory) provido pela fixture.
    """
    # Executa o seed
    msg = seed_vegan_data()
    
    # Verifica mensagem de sucesso
    assert "Dados Veganos Preenchidos com Sucesso" in msg
    
    # Verifica se os dados foram criados
    assert Produto.query.count() > 0
    assert Prato.query.count() == 30
    assert CardapioItem.query.count() == 30
    assert HistoricoVendas.query.count() > 0
    
    # Validação de integridade de um prato específico
    prato = Prato.query.filter_by(nome="Coxinha de Jaca").first()
    assert prato is not None
    assert prato.categoria == "Saladas" or prato.categoria == "Salgados" # Categoria corrigida no seed
    assert prato.preco_venda == 12.00
    
    # Verifica se há items de cardápio associados e disponíveis
    item = CardapioItem.query.filter_by(prato_id=prato.id).first()
    assert item is not None
    assert item.disponivel is True
