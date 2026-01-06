import pytest
from datetime import datetime
from app.models.modelo_log import Log
from app.models.modelo_usuario import Usuario

def test_criar_log(session):
    """Testa a criação de um log básico"""
    log = Log(
        tipo="info",
        mensagem="Teste de log",
        modulo="teste",
        nivel="info"
    )
    session.add(log)
    session.commit()
    
    assert log.id is not None
    assert log.tipo == "info"
    assert log.mensagem == "Teste de log"
    assert log.modulo == "teste"
    assert log.nivel == "info"
    assert log.data_hora is not None
    assert log.ip is None
    assert log.usuario_id is None

def test_log_com_usuario(session):
    """Testa a criação de um log com usuário"""
    # Criar usuário
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    # Criar log
    log = Log(
        tipo="info",
        mensagem="Teste de log com usuário",
        modulo="teste",
        nivel="info",
        usuario_id=usuario.id,
        ip="127.0.0.1"
    )
    session.add(log)
    session.commit()
    
    assert log.usuario_id == usuario.id
    assert log.usuario.nome == "João Silva"
    assert log.ip == "127.0.0.1"

def test_log_to_dict(session):
    """Testa a conversão do log para dicionário"""
    log = Log(
        tipo="info",
        mensagem="Teste de log",
        modulo="teste",
        nivel="info",
        ip="127.0.0.1"
    )
    session.add(log)
    session.commit()
    
    log_dict = log.to_dict()
    assert log_dict['tipo'] == "info"
    assert log_dict['mensagem'] == "Teste de log"
    assert log_dict['modulo'] == "teste"
    assert log_dict['nivel'] == "info"
    assert log_dict['ip'] == "127.0.0.1"
    assert 'data_hora' in log_dict

def test_log_constraints(session):
    """Testa as restrições do log"""
    # Teste de tipo inválido
    with pytest.raises(ValueError):
        log = Log(
            tipo="tipo_invalido",  # Tipo inválido
            mensagem="Teste",
            modulo="teste",
            nivel="info"
        )
        session.add(log)
        session.commit()
    
    # Teste de nível inválido
    with pytest.raises(ValueError):
        log = Log(
            tipo="info",
            mensagem="Teste",
            modulo="teste",
            nivel="nivel_invalido"  # Nível inválido
        )
        session.add(log)
        session.commit()

def test_buscar_logs_por_tipo(session):
    """Testa a busca de logs por tipo"""
    # Criar logs de diferentes tipos
    log1 = Log(
        tipo="info",
        mensagem="Log de informação",
        modulo="teste",
        nivel="info"
    )
    log2 = Log(
        tipo="erro",
        mensagem="Log de erro",
        modulo="teste",
        nivel="error"
    )
    log3 = Log(
        tipo="info",
        mensagem="Outro log de informação",
        modulo="teste",
        nivel="info"
    )
    session.add_all([log1, log2, log3])
    session.commit()
    
    # Buscar logs do tipo "info"
    logs_info = Log.query.filter_by(tipo="info").all()
    assert len(logs_info) == 2
    assert logs_info[0].mensagem == "Log de informação"
    assert logs_info[1].mensagem == "Outro log de informação"

def test_buscar_logs_por_nivel(session):
    """Testa a busca de logs por nível"""
    # Criar logs de diferentes níveis
    log1 = Log(
        tipo="info",
        mensagem="Log de informação",
        modulo="teste",
        nivel="info"
    )
    log2 = Log(
        tipo="erro",
        mensagem="Log de erro",
        modulo="teste",
        nivel="error"
    )
    log3 = Log(
        tipo="aviso",
        mensagem="Log de aviso",
        modulo="teste",
        nivel="warning"
    )
    session.add_all([log1, log2, log3])
    session.commit()
    
    # Buscar logs do nível "error"
    logs_error = Log.query.filter_by(nivel="error").all()
    assert len(logs_error) == 1
    assert logs_error[0].mensagem == "Log de erro"

def test_buscar_logs_por_modulo(session):
    """Testa a busca de logs por módulo"""
    # Criar logs de diferentes módulos
    log1 = Log(
        tipo="info",
        mensagem="Log do módulo A",
        modulo="modulo_a",
        nivel="info"
    )
    log2 = Log(
        tipo="info",
        mensagem="Log do módulo B",
        modulo="modulo_b",
        nivel="info"
    )
    log3 = Log(
        tipo="info",
        mensagem="Outro log do módulo A",
        modulo="modulo_a",
        nivel="info"
    )
    session.add_all([log1, log2, log3])
    session.commit()
    
    # Buscar logs do módulo "modulo_a"
    logs_modulo_a = Log.query.filter_by(modulo="modulo_a").all()
    assert len(logs_modulo_a) == 2
    assert logs_modulo_a[0].mensagem == "Log do módulo A"
    assert logs_modulo_a[1].mensagem == "Outro log do módulo A"

def test_buscar_logs_por_periodo(session):
    """Testa a busca de logs por período"""
    # Criar logs em diferentes momentos
    log1 = Log(
        tipo="info",
        mensagem="Log antigo",
        modulo="teste",
        nivel="info",
        data_hora=datetime(2023, 1, 1, 10, 0)
    )
    log2 = Log(
        tipo="info",
        mensagem="Log recente",
        modulo="teste",
        nivel="info",
        data_hora=datetime(2023, 1, 2, 10, 0)
    )
    session.add_all([log1, log2])
    session.commit()
    
    # Buscar logs entre 2023-01-01 e 2023-01-02
    logs_periodo = Log.query.filter(
        Log.data_hora >= datetime(2023, 1, 1),
        Log.data_hora <= datetime(2023, 1, 2)
    ).all()
    assert len(logs_periodo) == 2
    assert logs_periodo[0].mensagem == "Log antigo"
    assert logs_periodo[1].mensagem == "Log recente" 