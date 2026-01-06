import pytest
from datetime import datetime
from app.models.modelo_backup import Backup
from app.models.modelo_usuario import Usuario

def test_criar_backup(session):
    """Testa a criação de um backup básico"""
    backup = Backup(
        nome="backup_teste",
        tipo="completo",
        status="concluido",
        tamanho=1024,  # 1KB
        caminho="/backups/backup_teste.zip"
    )
    session.add(backup)
    session.commit()
    
    assert backup.id is not None
    assert backup.nome == "backup_teste"
    assert backup.tipo == "completo"
    assert backup.status == "concluido"
    assert backup.tamanho == 1024
    assert backup.caminho == "/backups/backup_teste.zip"
    assert backup.data_hora is not None
    assert backup.usuario_id is None

def test_backup_com_usuario(session):
    """Testa a criação de um backup com usuário"""
    # Criar usuário
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    # Criar backup
    backup = Backup(
        nome="backup_teste",
        tipo="completo",
        status="concluido",
        tamanho=1024,
        caminho="/backups/backup_teste.zip",
        usuario_id=usuario.id
    )
    session.add(backup)
    session.commit()
    
    assert backup.usuario_id == usuario.id
    assert backup.usuario.nome == "João Silva"

def test_backup_to_dict(session):
    """Testa a conversão do backup para dicionário"""
    backup = Backup(
        nome="backup_teste",
        tipo="completo",
        status="concluido",
        tamanho=1024,
        caminho="/backups/backup_teste.zip"
    )
    session.add(backup)
    session.commit()
    
    backup_dict = backup.to_dict()
    assert backup_dict['nome'] == "backup_teste"
    assert backup_dict['tipo'] == "completo"
    assert backup_dict['status'] == "concluido"
    assert backup_dict['tamanho'] == 1024
    assert backup_dict['caminho'] == "/backups/backup_teste.zip"
    assert 'data_hora' in backup_dict

def test_backup_constraints(session):
    """Testa as restrições do backup"""
    # Teste de tipo inválido
    with pytest.raises(ValueError):
        backup = Backup(
            nome="backup_teste",
            tipo="tipo_invalido",  # Tipo inválido
            status="concluido",
            tamanho=1024,
            caminho="/backups/backup_teste.zip"
        )
        session.add(backup)
        session.commit()
    
    # Teste de status inválido
    with pytest.raises(ValueError):
        backup = Backup(
            nome="backup_teste",
            tipo="completo",
            status="status_invalido",  # Status inválido
            tamanho=1024,
            caminho="/backups/backup_teste.zip"
        )
        session.add(backup)
        session.commit()
    
    # Teste de tamanho negativo
    with pytest.raises(ValueError):
        backup = Backup(
            nome="backup_teste",
            tipo="completo",
            status="concluido",
            tamanho=-1024,  # Tamanho negativo
            caminho="/backups/backup_teste.zip"
        )
        session.add(backup)
        session.commit()

def test_atualizar_status_backup(session):
    """Testa a atualização do status do backup"""
    backup = Backup(
        nome="backup_teste",
        tipo="completo",
        status="em_andamento",
        tamanho=0,
        caminho="/backups/backup_teste.zip"
    )
    session.add(backup)
    session.commit()
    
    backup.status = "concluido"
    backup.tamanho = 1024
    session.commit()
    
    assert backup.status == "concluido"
    assert backup.tamanho == 1024

def test_buscar_backups_por_tipo(session):
    """Testa a busca de backups por tipo"""
    # Criar backups de diferentes tipos
    backup1 = Backup(
        nome="backup_completo",
        tipo="completo",
        status="concluido",
        tamanho=1024,
        caminho="/backups/backup_completo.zip"
    )
    backup2 = Backup(
        nome="backup_incremental",
        tipo="incremental",
        status="concluido",
        tamanho=512,
        caminho="/backups/backup_incremental.zip"
    )
    backup3 = Backup(
        nome="backup_completo_2",
        tipo="completo",
        status="concluido",
        tamanho=2048,
        caminho="/backups/backup_completo_2.zip"
    )
    session.add_all([backup1, backup2, backup3])
    session.commit()
    
    # Buscar backups do tipo "completo"
    backups_completo = Backup.query.filter_by(tipo="completo").all()
    assert len(backups_completo) == 2
    assert backups_completo[0].nome == "backup_completo"
    assert backups_completo[1].nome == "backup_completo_2"

def test_buscar_backups_por_status(session):
    """Testa a busca de backups por status"""
    # Criar backups com diferentes status
    backup1 = Backup(
        nome="backup_concluido",
        tipo="completo",
        status="concluido",
        tamanho=1024,
        caminho="/backups/backup_concluido.zip"
    )
    backup2 = Backup(
        nome="backup_erro",
        tipo="completo",
        status="erro",
        tamanho=0,
        caminho="/backups/backup_erro.zip"
    )
    backup3 = Backup(
        nome="backup_andamento",
        tipo="completo",
        status="em_andamento",
        tamanho=0,
        caminho="/backups/backup_andamento.zip"
    )
    session.add_all([backup1, backup2, backup3])
    session.commit()
    
    # Buscar backups com status "concluido"
    backups_concluidos = Backup.query.filter_by(status="concluido").all()
    assert len(backups_concluidos) == 1
    assert backups_concluidos[0].nome == "backup_concluido"

def test_buscar_backups_por_periodo(session):
    """Testa a busca de backups por período"""
    # Criar backups em diferentes momentos
    backup1 = Backup(
        nome="backup_antigo",
        tipo="completo",
        status="concluido",
        tamanho=1024,
        caminho="/backups/backup_antigo.zip",
        data_hora=datetime(2023, 1, 1, 10, 0)
    )
    backup2 = Backup(
        nome="backup_recente",
        tipo="completo",
        status="concluido",
        tamanho=2048,
        caminho="/backups/backup_recente.zip",
        data_hora=datetime(2023, 1, 2, 10, 0)
    )
    session.add_all([backup1, backup2])
    session.commit()
    
    # Buscar backups entre 2023-01-01 e 2023-01-02
    backups_periodo = Backup.query.filter(
        Backup.data_hora >= datetime(2023, 1, 1),
        Backup.data_hora <= datetime(2023, 1, 2)
    ).all()
    assert len(backups_periodo) == 2
    assert backups_periodo[0].nome == "backup_antigo"
    assert backups_periodo[1].nome == "backup_recente" 