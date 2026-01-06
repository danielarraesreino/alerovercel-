import pytest
from decimal import Decimal
from datetime import datetime
from app.models.modelo_configuracao import Configuracao

def test_criar_configuracao(session):
    """Testa a criação de uma configuração básica"""
    config = Configuracao(
        chave="margem_padrao",
        valor="30",
        tipo="decimal",
        descricao="Margem de lucro padrão em percentual",
        categoria="precos"
    )
    session.add(config)
    session.commit()
    
    assert config.id is not None
    assert config.chave == "margem_padrao"
    assert config.valor == "30"
    assert config.tipo == "decimal"
    assert config.descricao == "Margem de lucro padrão em percentual"
    assert config.categoria == "precos"
    assert config.ativo is True

def test_get_valor_decimal(session):
    """Testa a obtenção do valor como decimal"""
    config = Configuracao(
        chave="margem_padrao",
        valor="30.5",
        tipo="decimal",
        descricao="Margem de lucro padrão em percentual",
        categoria="precos"
    )
    session.add(config)
    session.commit()
    
    assert config.get_valor_decimal() == Decimal("30.5")

def test_get_valor_inteiro(session):
    """Testa a obtenção do valor como inteiro"""
    config = Configuracao(
        chave="estoque_minimo",
        valor="10",
        tipo="inteiro",
        descricao="Estoque mínimo padrão",
        categoria="estoque"
    )
    session.add(config)
    session.commit()
    
    assert config.get_valor_inteiro() == 10

def test_get_valor_booleano(session):
    """Testa a obtenção do valor como booleano"""
    config = Configuracao(
        chave="notificar_estoque_baixo",
        valor="true",
        tipo="booleano",
        descricao="Notificar quando estoque estiver baixo",
        categoria="notificacoes"
    )
    session.add(config)
    session.commit()
    
    assert config.get_valor_booleano() is True

def test_get_valor_texto(session):
    """Testa a obtenção do valor como texto"""
    config = Configuracao(
        chave="nome_restaurante",
        valor="Restaurante Teste",
        tipo="texto",
        descricao="Nome do restaurante",
        categoria="geral"
    )
    session.add(config)
    session.commit()
    
    assert config.get_valor_texto() == "Restaurante Teste"

def test_configuracao_to_dict(session):
    """Testa a conversão da configuração para dicionário"""
    config = Configuracao(
        chave="margem_padrao",
        valor="30.5",
        tipo="decimal",
        descricao="Margem de lucro padrão em percentual",
        categoria="precos"
    )
    session.add(config)
    session.commit()
    
    config_dict = config.to_dict()
    assert config_dict['chave'] == "margem_padrao"
    assert config_dict['valor'] == "30.5"
    assert config_dict['tipo'] == "decimal"
    assert config_dict['descricao'] == "Margem de lucro padrão em percentual"
    assert config_dict['categoria'] == "precos"
    assert config_dict['ativo'] is True

def test_configuracao_constraints(session):
    """Testa as restrições da configuração"""
    # Teste de chave duplicada
    config1 = Configuracao(
        chave="margem_padrao",
        valor="30",
        tipo="decimal",
        descricao="Margem de lucro padrão",
        categoria="precos"
    )
    session.add(config1)
    session.commit()
    
    with pytest.raises(ValueError):
        config2 = Configuracao(
            chave="margem_padrao",  # Chave duplicada
            valor="40",
            tipo="decimal",
            descricao="Outra margem",
            categoria="precos"
        )
        session.add(config2)
        session.commit()
    
    # Teste de tipo inválido
    with pytest.raises(ValueError):
        config = Configuracao(
            chave="teste",
            valor="valor",
            tipo="tipo_invalido",  # Tipo inválido
            descricao="Teste",
            categoria="teste"
        )
        session.add(config)
        session.commit()

def test_atualizar_configuracao(session):
    """Testa a atualização de uma configuração"""
    config = Configuracao(
        chave="margem_padrao",
        valor="30",
        tipo="decimal",
        descricao="Margem de lucro padrão",
        categoria="precos"
    )
    session.add(config)
    session.commit()
    
    config.valor = "35"
    config.descricao = "Nova margem de lucro padrão"
    session.commit()
    
    assert config.valor == "35"
    assert config.descricao == "Nova margem de lucro padrão"

def test_desativar_configuracao(session):
    """Testa a desativação de uma configuração"""
    config = Configuracao(
        chave="margem_padrao",
        valor="30",
        tipo="decimal",
        descricao="Margem de lucro padrão",
        categoria="precos",
        ativo=True
    )
    session.add(config)
    session.commit()
    
    config.ativo = False
    session.commit()
    
    assert config.ativo is False

def test_get_configuracoes_por_categoria(session):
    """Testa a obtenção de configurações por categoria"""
    # Criar configurações de diferentes categorias
    config1 = Configuracao(
        chave="margem_padrao",
        valor="30",
        tipo="decimal",
        descricao="Margem de lucro padrão",
        categoria="precos"
    )
    config2 = Configuracao(
        chave="estoque_minimo",
        valor="10",
        tipo="inteiro",
        descricao="Estoque mínimo",
        categoria="estoque"
    )
    config3 = Configuracao(
        chave="margem_maxima",
        valor="50",
        tipo="decimal",
        descricao="Margem máxima",
        categoria="precos"
    )
    session.add_all([config1, config2, config3])
    session.commit()
    
    # Buscar configurações da categoria "precos"
    configs_precos = Configuracao.query.filter_by(categoria="precos").all()
    assert len(configs_precos) == 2
    assert configs_precos[0].chave == "margem_padrao"
    assert configs_precos[1].chave == "margem_maxima" 