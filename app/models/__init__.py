# Importar todos os modelos para uso fácil com "from app.models import X"

from app.models.modelo_fornecedor import Fornecedor
from app.models.modelo_produto import Produto
from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_estoque import EstoqueMovimentacao
from app.models.modelo_prato import Prato, PratoInsumo
from app.models.modelo_custo import CustoIndireto
from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
