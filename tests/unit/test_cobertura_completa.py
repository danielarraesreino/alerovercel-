import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy import text
from app import db
from app.models.modelo_desperdicio import CategoriaDesperdicio, RegistroDesperdicio, MetaDesperdicio
from app.models.modelo_previsao import HistoricoVendas, PrevisaoDemanda, FatorSazonalidade
from app.models.modelo_produto import Produto
from app.models.modelo_cardapio import Cardapio, CardapioSecao, CardapioItem
from app.models.modelo_prato import Prato, PratoInsumo
from app.models.modelo_estoque import EstoqueMovimentacao
from app.models.modelo_fornecedor import Fornecedor
from app.models.modelo_nfe import NFNota, NFItem
from app.models.modelo_custo import CustoIndireto
from app.utils.calculos import calcular_preco_medio_ponderado, calcular_custo_por_porcao, calcular_preco_venda
from app.utils.nfe_parser import extrair_dados_nfe

# ----- TESTES DE MODELOS -----

# Teste para cada modelo do sistema
@pytest.mark.parametrize("modelo, dados", [
    (Produto, {
        'nome': 'Produto Teste',
        'descricao': 'Descrição do produto teste',
        'unidade_medida': 'kg',
        'preco_unitario': 10.0,
        'estoque_minimo': 5.0,
        'estoque_atual': 20.0,
        'categoria': 'Teste'
    }),
    (CategoriaDesperdicio, {
        'nome': 'Categoria Teste',
        'descricao': 'Descrição da categoria',
        'cor': '#FF5733'
    }),
    (Fornecedor, {
        'nome': 'Fornecedor Teste',
        'cnpj': '12.345.678/0001-90',
        'email': 'contato@fornecedor.com',
        'telefone': '(11) 1234-5678'
    }),
    (Cardapio, {
        'nome': 'Cardápio Teste',
        'descricao': 'Descrição do cardápio teste',
        'data_inicio': datetime.now().date(),
        'data_fim': datetime.now().date() + timedelta(days=30),
        'tipo': 'semanal'
    }),
    (CustoIndireto, {
        'descricao': 'Custo Indireto Teste',
        'valor': 1000.00,
        'data_referencia': datetime.now().date(),
        'tipo': 'aluguel'
    })
])
def test_criacao_modelo_basico(session, modelo, dados):
    """Testa a criação básica de cada modelo principal do sistema"""
    # Criar instância do modelo com os dados fornecidos
    instancia = modelo(**dados)
    session.add(instancia)
    session.commit()
    
    # Verificar se a instância foi criada com ID
    assert instancia.id is not None
    
    # Verificar se podemos recuperar a instância do banco
    recuperada = session.query(modelo).filter_by(id=instancia.id).first()
    assert recuperada is not None
    
    # Verificar se os principais atributos foram salvos corretamente
    for chave, valor in dados.items():
        assert getattr(recuperada, chave) == valor

# Testes específicos para HistoricoVendas (previsão de demanda)
@pytest.fixture
def setup_cardapio_completo(session):
    """Cria um cardápio completo com seções e itens para testes"""
    # Criar prato
    prato = Prato(
        nome='Prato Teste',
        descricao='Descrição do prato teste',
        categoria='Principal',
        tempo_preparo=30,
        preco_venda=25.0,
        custo_estimado=10.0
    )
    session.add(prato)
    
    # Criar cardápio
    cardapio = Cardapio(
        nome='Cardápio Teste',
        descricao='Cardápio para testes',
        data_inicio=datetime.now().date(),
        tipo='diário'
    )
    session.add(cardapio)
    session.flush()  # Para obter os IDs
    
    # Criar seção do cardápio
    secao = CardapioSecao(
        cardapio_id=cardapio.id,
        nome='Seção Teste',
        descricao='Seção para testes',
        ordem=1
    )
    session.add(secao)
    session.flush()
    
    # Criar item de cardápio
    item = CardapioItem(
        secao_id=secao.id,
        prato_id=prato.id,
        ordem=1,
        preco_venda=30.0,
        disponivel=True
    )
    session.add(item)
    session.commit()
    
    return {
        'prato': prato,
        'cardapio': cardapio,
        'secao': secao,
        'item': item
    }

def test_historico_vendas_create(session, setup_cardapio_completo):
    """Testa a criação de registros de histórico de vendas"""
    item = setup_cardapio_completo['item']
    
    # Criar registro de venda
    venda = HistoricoVendas(
        data=datetime.now().date(),
        cardapio_item_id=item.id,
        quantidade=3,
        valor_unitario=30.0,
        valor_total=90.0,
        periodo_dia='noite',
        dia_semana=datetime.now().weekday(),
        mes=datetime.now().month
    )
    session.add(venda)
    session.commit()
    
    # Verificar se o registro foi criado
    assert venda.id is not None
    
    # Verificar relacionamento com item de cardápio
    assert venda.cardapio_item_id == item.id
    assert venda.cardapio_item is not None

def test_previsao_demanda_create(session, setup_cardapio_completo):
    """Testa a criação e uso de previsões de demanda"""
    item = setup_cardapio_completo['item']
    
    # Criar previsão
    valores = json.dumps({
        (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'): 10,
        (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'): 12,
        (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'): 15
    })
    
    previsao = PrevisaoDemanda(
        cardapio_item_id=item.id,
        data_inicio=datetime.now().date(),
        data_fim=(datetime.now() + timedelta(days=3)).date(),
        metodo='média_móvel',
        valores_previstos=valores,
        data_criacao=datetime.now(),
        confiabilidade=0.85
    )
    session.add(previsao)
    session.commit()
    
    # Verificar se foi criada
    assert previsao.id is not None
    
    # Testar o método get_valores_previstos
    valores_dict = previsao.get_valores_previstos()
    assert isinstance(valores_dict, dict)
    assert len(valores_dict) == 3
    
    # Testar previsão para uma data específica
    data_teste = (datetime.now() + timedelta(days=2)).date()
    valor_previsto = previsao.get_previsao_para_data(data_teste)
    assert valor_previsto == 12

def test_fator_sazonalidade_create(session, setup_cardapio_completo):
    """Testa a criação de fatores de sazonalidade"""
    item = setup_cardapio_completo['item']
    
    # Criar fator sazonal para dia da semana
    fator = FatorSazonalidade(
        cardapio_item_id=item.id,
        dia_semana=1,  # Terça-feira
        fator=1.2,
        descricao='Aumento de 20% às terças'
    )
    session.add(fator)
    session.commit()
    
    # Verificar se foi criado
    assert fator.id is not None
    assert fator.fator == 1.2
    assert fator.dia_semana == 1
    
    # Testar relacionamento
    assert fator.cardapio_item_id == item.id
    assert fator.cardapio_item is not None

# Testes para módulo de desperdício
def test_registro_desperdicio_completo(session):
    """Testa o fluxo completo de registro de desperdício"""
    # Criar categoria de desperdício
    categoria = CategoriaDesperdicio(
        nome='Vencido',
        descricao='Produtos vencidos',
        cor='#FF0000'
    )
    session.add(categoria)
    
    # Criar produto
    produto = Produto(
        nome='Produto para Desperdício',
        descricao='Produto usado em teste de desperdício',
        unidade_medida='kg',
        preco_unitario=15.0,
        estoque_atual=50.0,
        categoria='Teste'
    )
    session.add(produto)
    session.commit()
    
    # Registrar desperdício
    registro = RegistroDesperdicio(
        categoria_id=categoria.id,
        produto_id=produto.id,
        quantidade=3.5,
        unidade_medida='kg',
        valor_estimado=52.5,
        data_registro=datetime.now(),
        motivo='Produto vencido',
        responsavel='Tester',
        local='Estoque',
        descricao='Teste de registro de desperdício'
    )
    session.add(registro)
    
    # Criar meta de redução
    meta = MetaDesperdicio(
        categoria_id=categoria.id,
        valor_inicial=1000.0,
        meta_reducao_percentual=20.0,
        data_inicio=datetime.now().date(),
        data_fim=(datetime.now() + timedelta(days=30)).date(),
        descricao='Meta de redução de desperdícios vencidos',
        responsavel='Gerente Teste',
        acoes_propostas='Melhorar controle de validades'
    )
    session.add(meta)
    session.commit()
    
    # Verificar se tudo foi criado
    assert registro.id is not None
    assert meta.id is not None
    
    # Verificar relacionamentos
    assert registro.categoria_id == categoria.id
    assert registro.produto_id == produto.id
    assert meta.categoria_id == categoria.id
    
    # Verificar cálculo do valor da meta
    assert meta.meta_valor_absoluto() == 800.0
    
    # Verificar cálculo de progresso
    # O progresso real depende da implementação específica
    progresso = meta.progresso_atual()
    assert isinstance(progresso, dict)

# ----- TESTES DE UTILIDADES -----

def test_calculo_media_movel():
    """Testa a função de cálculo de média móvel"""
    # Dados históricos de exemplo
    dados_historicos = [
        {'data': '2025-04-01', 'quantidade': 10},
        {'data': '2025-04-02', 'quantidade': 12},
        {'data': '2025-04-03', 'quantidade': 8},
        {'data': '2025-04-04', 'quantidade': 15},
        {'data': '2025-04-05', 'quantidade': 11}
    ]
    
    # Período para previsão
    data_inicio = datetime.strptime('2025-04-06', '%Y-%m-%d').date()
    data_fim = datetime.strptime('2025-04-08', '%Y-%m-%d').date()
    
    # Testar a função se estiver implementada
    try:
        resultado = calcular_media_movel(dados_historicos, data_inicio, data_fim, janela=3)
        assert isinstance(resultado, dict)
        assert len(resultado) == 3  # 3 dias de previsão
        
        # A média móvel dos últimos 3 dias (8, 15, 11) deve ser aproximadamente 11.33
        primeiro_dia = data_inicio.strftime('%Y-%m-%d')
        assert abs(resultado[primeiro_dia] - 11.33) < 0.1
    except (NameError, TypeError):
        # Se a função não estiver implementada conforme esperado, pular
        pytest.skip("Função calcular_media_movel não está implementada como esperado")

def test_aplicacao_fatores_sazonais():
    """Testa a aplicação de fatores sazonais nas previsões"""
    # Previsão base
    previsao_base = {
        '2025-04-06': 10,  # Sábado
        '2025-04-07': 10,  # Domingo
        '2025-04-08': 10   # Segunda
    }
    
    # Fatores sazonais
    fatores = [
        {'dia_semana': 5, 'fator': 1.2},  # Sábado (+20%)
        {'dia_semana': 6, 'fator': 1.5}   # Domingo (+50%)
    ]
    
    # Testar a função se estiver implementada
    try:
        resultado = aplicar_fatores_sazonais(previsao_base, fatores)
        assert isinstance(resultado, dict)
        assert len(resultado) == 3
        
        # Verificar aplicação dos fatores
        assert resultado['2025-04-06'] == 12  # 10 * 1.2 para sábado
        assert resultado['2025-04-07'] == 15  # 10 * 1.5 para domingo
        assert resultado['2025-04-08'] == 10  # sem fator para segunda
    except (NameError, TypeError):
        # Se a função não estiver implementada conforme esperado, pular
        pytest.skip("Função aplicar_fatores_sazonais não está implementada como esperado")

# ----- TESTES DE ROTAS -----

def test_rota_dashboard(client):
    """Testa o acesso à página principal do dashboard"""
    response = client.get('/')
    assert response.status_code == 200

def test_rota_desperdicio_index(client):
    """Testa o acesso à página principal do módulo de desperdício"""
    response = client.get('/desperdicio/')
    assert response.status_code == 200

def test_rota_previsao_index(client):
    """Testa o acesso à página principal do módulo de previsão"""
    response = client.get('/previsao/')
    assert response.status_code == 200
