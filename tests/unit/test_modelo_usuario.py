import pytest
from datetime import datetime
from app.models.modelo_usuario import Usuario

def test_criar_usuario(session):
    """Testa a criação de um usuário básico"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente",
        ativo=True
    )
    session.add(usuario)
    session.commit()
    
    assert usuario.id is not None
    assert usuario.nome == "João Silva"
    assert usuario.email == "joao@email.com"
    assert usuario.cargo == "gerente"
    assert usuario.ativo is True
    assert usuario.data_criacao is not None
    assert usuario.data_atualizacao is not None

def test_verificar_senha(session):
    """Testa a verificação de senha do usuário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    assert usuario.verificar_senha("senha123") is True
    assert usuario.verificar_senha("senha_errada") is False

def test_alterar_senha(session):
    """Testa a alteração de senha do usuário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    usuario.alterar_senha("nova_senha")
    session.commit()
    
    assert usuario.verificar_senha("nova_senha") is True
    assert usuario.verificar_senha("senha123") is False

def test_usuario_to_dict(session):
    """Testa a conversão do usuário para dicionário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente",
        ativo=True
    )
    session.add(usuario)
    session.commit()
    
    usuario_dict = usuario.to_dict()
    assert usuario_dict['nome'] == "João Silva"
    assert usuario_dict['email'] == "joao@email.com"
    assert usuario_dict['cargo'] == "gerente"
    assert usuario_dict['ativo'] is True
    assert 'senha' not in usuario_dict  # Senha não deve ser incluída no dicionário

def test_usuario_constraints(session):
    """Testa as restrições do usuário"""
    # Teste de email inválido
    with pytest.raises(ValueError):
        usuario = Usuario(
            nome="João Silva",
            email="email_invalido",  # Email inválido
            senha="senha123",
            cargo="gerente"
        )
        session.add(usuario)
        session.commit()
    
    # Teste de cargo inválido
    with pytest.raises(ValueError):
        usuario = Usuario(
            nome="João Silva",
            email="joao@email.com",
            senha="senha123",
            cargo="cargo_invalido"  # Cargo inválido
        )
        session.add(usuario)
        session.commit()
    
    # Teste de email duplicado
    usuario1 = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario1)
    session.commit()
    
    with pytest.raises(ValueError):
        usuario2 = Usuario(
            nome="Maria Santos",
            email="joao@email.com",  # Email duplicado
            senha="senha456",
            cargo="atendente"
        )
        session.add(usuario2)
        session.commit()

def test_atualizar_usuario(session):
    """Testa a atualização dos dados do usuário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    data_antes = usuario.data_atualizacao
    
    usuario.nome = "João Silva Santos"
    usuario.cargo = "supervisor"
    session.commit()
    
    assert usuario.nome == "João Silva Santos"
    assert usuario.cargo == "supervisor"
    assert usuario.data_atualizacao > data_antes

def test_desativar_usuario(session):
    """Testa a desativação de um usuário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente",
        ativo=True
    )
    session.add(usuario)
    session.commit()
    
    usuario.ativo = False
    session.commit()
    
    assert usuario.ativo is False
    assert usuario.data_atualizacao is not None

def test_redefinir_senha(session):
    """Testa a redefinição de senha do usuário"""
    usuario = Usuario(
        nome="João Silva",
        email="joao@email.com",
        senha="senha123",
        cargo="gerente"
    )
    session.add(usuario)
    session.commit()
    
    nova_senha = usuario.redefinir_senha()
    session.commit()
    
    assert len(nova_senha) == 8  # Senha temporária de 8 caracteres
    assert usuario.verificar_senha(nova_senha) is True
    assert usuario.verificar_senha("senha123") is False 