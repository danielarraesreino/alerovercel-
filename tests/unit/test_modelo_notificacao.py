import pytest
from datetime import datetime
from app.models.modelo_notificacao import Notificacao
from app.models.modelo_usuario import Usuario

def test_criar_notificacao(session):
    """Testa a criação de uma notificação básica"""
    notificacao = Notificacao(
        titulo="Estoque Baixo",
        mensagem="O produto X está com estoque abaixo do mínimo",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    session.add(notificacao)
    session.commit()
    
    assert notificacao.id is not None
    assert notificacao.titulo == "Estoque Baixo"
    assert notificacao.mensagem == "O produto X está com estoque abaixo do mínimo"
    assert notificacao.tipo == "alerta"
    assert notificacao.prioridade == "alta"
    assert notificacao.status == "nao_lida"
    assert notificacao.data_hora is not None
    assert notificacao.usuario_id is None

def test_notificacao_com_usuario(session):
    """Testa a criação de uma notificação com usuário"""
    # Criar usuário
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    # Criar notificação
    notificacao = Notificacao(
        titulo="Estoque Baixo",
        mensagem="O produto X está com estoque abaixo do mínimo",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida",
        usuario_id=usuario.id
    )
    session.add(notificacao)
    session.commit()
    
    assert notificacao.usuario_id == usuario.id
    assert notificacao.usuario.nome == "João Silva"

def test_notificacao_to_dict(session):
    """Testa a conversão da notificação para dicionário"""
    notificacao = Notificacao(
        titulo="Estoque Baixo",
        mensagem="O produto X está com estoque abaixo do mínimo",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    session.add(notificacao)
    session.commit()
    
    notificacao_dict = notificacao.to_dict()
    assert notificacao_dict['titulo'] == "Estoque Baixo"
    assert notificacao_dict['mensagem'] == "O produto X está com estoque abaixo do mínimo"
    assert notificacao_dict['tipo'] == "alerta"
    assert notificacao_dict['prioridade'] == "alta"
    assert notificacao_dict['status'] == "nao_lida"
    assert 'data_hora' in notificacao_dict

def test_notificacao_constraints(session):
    """Testa as restrições da notificação"""
    # Teste de tipo inválido
    with pytest.raises(ValueError):
        notificacao = Notificacao(
            titulo="Teste",
            mensagem="Teste",
            tipo="tipo_invalido",  # Tipo inválido
            prioridade="alta",
            status="nao_lida"
        )
        session.add(notificacao)
        session.commit()
    
    # Teste de prioridade inválida
    with pytest.raises(ValueError):
        notificacao = Notificacao(
            titulo="Teste",
            mensagem="Teste",
            tipo="alerta",
            prioridade="prioridade_invalida",  # Prioridade inválida
            status="nao_lida"
        )
        session.add(notificacao)
        session.commit()
    
    # Teste de status inválido
    with pytest.raises(ValueError):
        notificacao = Notificacao(
            titulo="Teste",
            mensagem="Teste",
            tipo="alerta",
            prioridade="alta",
            status="status_invalido"  # Status inválido
        )
        session.add(notificacao)
        session.commit()

def test_marcar_como_lida(session):
    """Testa a marcação de notificação como lida"""
    notificacao = Notificacao(
        titulo="Estoque Baixo",
        mensagem="O produto X está com estoque abaixo do mínimo",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    session.add(notificacao)
    session.commit()
    
    notificacao.status = "lida"
    session.commit()
    
    assert notificacao.status == "lida"

def test_buscar_notificacoes_por_tipo(session):
    """Testa a busca de notificações por tipo"""
    # Criar notificações de diferentes tipos
    notif1 = Notificacao(
        titulo="Alerta 1",
        mensagem="Mensagem de alerta 1",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    notif2 = Notificacao(
        titulo="Info 1",
        mensagem="Mensagem informativa 1",
        tipo="info",
        prioridade="baixa",
        status="nao_lida"
    )
    notif3 = Notificacao(
        titulo="Alerta 2",
        mensagem="Mensagem de alerta 2",
        tipo="alerta",
        prioridade="media",
        status="nao_lida"
    )
    session.add_all([notif1, notif2, notif3])
    session.commit()
    
    # Buscar notificações do tipo "alerta"
    notifs_alerta = Notificacao.query.filter_by(tipo="alerta").all()
    assert len(notifs_alerta) == 2
    assert notifs_alerta[0].titulo == "Alerta 1"
    assert notifs_alerta[1].titulo == "Alerta 2"

def test_buscar_notificacoes_por_prioridade(session):
    """Testa a busca de notificações por prioridade"""
    # Criar notificações com diferentes prioridades
    notif1 = Notificacao(
        titulo="Alta 1",
        mensagem="Notificação de alta prioridade 1",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    notif2 = Notificacao(
        titulo="Media 1",
        mensagem="Notificação de média prioridade",
        tipo="alerta",
        prioridade="media",
        status="nao_lida"
    )
    notif3 = Notificacao(
        titulo="Alta 2",
        mensagem="Notificação de alta prioridade 2",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    session.add_all([notif1, notif2, notif3])
    session.commit()
    
    # Buscar notificações de prioridade "alta"
    notifs_alta = Notificacao.query.filter_by(prioridade="alta").all()
    assert len(notifs_alta) == 2
    assert notifs_alta[0].titulo == "Alta 1"
    assert notifs_alta[1].titulo == "Alta 2"

def test_buscar_notificacoes_por_status(session):
    """Testa a busca de notificações por status"""
    # Criar notificações com diferentes status
    notif1 = Notificacao(
        titulo="Não lida 1",
        mensagem="Notificação não lida 1",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    notif2 = Notificacao(
        titulo="Lida 1",
        mensagem="Notificação lida 1",
        tipo="alerta",
        prioridade="alta",
        status="lida"
    )
    notif3 = Notificacao(
        titulo="Não lida 2",
        mensagem="Notificação não lida 2",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida"
    )
    session.add_all([notif1, notif2, notif3])
    session.commit()
    
    # Buscar notificações não lidas
    notifs_nao_lidas = Notificacao.query.filter_by(status="nao_lida").all()
    assert len(notifs_nao_lidas) == 2
    assert notifs_nao_lidas[0].titulo == "Não lida 1"
    assert notifs_nao_lidas[1].titulo == "Não lida 2"

def test_buscar_notificacoes_por_periodo(session):
    """Testa a busca de notificações por período"""
    # Criar notificações em diferentes momentos
    notif1 = Notificacao(
        titulo="Antiga",
        mensagem="Notificação antiga",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida",
        data_hora=datetime(2023, 1, 1, 10, 0)
    )
    notif2 = Notificacao(
        titulo="Recente",
        mensagem="Notificação recente",
        tipo="alerta",
        prioridade="alta",
        status="nao_lida",
        data_hora=datetime(2023, 1, 2, 10, 0)
    )
    session.add_all([notif1, notif2])
    session.commit()
    
    # Buscar notificações entre 2023-01-01 e 2023-01-02
    notifs_periodo = Notificacao.query.filter(
        Notificacao.data_hora >= datetime(2023, 1, 1),
        Notificacao.data_hora <= datetime(2023, 1, 2)
    ).all()
    assert len(notifs_periodo) == 2
    assert notifs_periodo[0].titulo == "Antiga"
    assert notifs_periodo[1].titulo == "Recente" 