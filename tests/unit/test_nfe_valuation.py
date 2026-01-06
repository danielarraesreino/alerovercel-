
import pytest
from unittest.mock import MagicMock, patch
from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_produto import Produto

def test_atualizar_estoque_preco_medio_ponderado():
    """
    Testa se a atualização de estoque calcula corretamente o preço médio ponderado.
    Cenário:
    - Estoque atual: 10 unidades a R$ 10,00 (Valor total: R$ 100,00)
    - Nova compra: 10 unidades a R$ 20,00 (Valor total: R$ 200,00)
    - Resultado esperado: 20 unidades a R$ 15,00
    """
    # Mock da aplicação
    from app import create_app
    app = create_app()

    with app.app_context():
        # Mock dos objetos - Agora dentro do contexto da aplicação!
        produto = MagicMock(spec=Produto)
        produto.estoque_atual = 10.0
        produto.preco_unitario = 10.0
        produto.id = 1

        item = MagicMock(spec=NFItem)
        item.produto = produto
        item.produto_id = 1
        item.quantidade = 10.0
        item.valor_unitario = 20.0
        item.id = 100

        # Mock da nota para evitar instrumentação do SQLAlchemy
        nota = MagicMock(spec=NFNota)
        nota.numero = "123"
        nota.serie = "1"
        nota.itens = [item]

        # Mock da sessão do banco de dados para evitar erros de commit/add
        with patch('app.models.modelo_nfe.db.session') as mock_session:
            with patch('app.models.modelo_estoque.EstoqueMovimentacao') as MockMovimento:
                 # Executa a função chamando DIRETAMENTE a classe, passando o mock como self
                NFNota.atualizar_estoque(nota)

                # Verificações
                # 1. Preço médio deve ser 15.0
                assert produto.preco_unitario == 15.0
                
                # 2. Estoque deve ser atualizado para 20.0
                assert produto.estoque_atual == 20.0
                
                # 3. Movimentação deve ter sido criada
                MockMovimento.assert_called()
                mock_session.add.assert_called()
                mock_session.commit.assert_called()
