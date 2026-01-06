from flask import url_for

def test_home_page(client):
    """Testa se a página inicial carrega"""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"AleroPrice" in response.data

def test_pratos_index(client):
    """Testa se a lista de pratos carrega"""
    response = client.get('/pratos/', follow_redirects=True)
    assert response.status_code == 200
    # Verifica se o template base está lá (header/footer)
    assert b"<html" in response.data

def test_dashboard_index(client):
    """Testa se o dashboard carrega"""
    response = client.get('/dashboard/', follow_redirects=True)
    assert response.status_code == 200

def test_seed_vegan_route(client):
    """Testa se a rota de seeding existe (não executa o seed inteiro aqui para ser rápido)"""
    # Apenas verifica se a rota não dá 404
    # Note: Chamar essa rota dispara o seed, o que pode ser lento. 
    # Em teste de unidade, o DB é :memory:, então é seguro rodar.
    response = client.get('/seed-vegan', follow_redirects=True)
    assert response.status_code == 200
    assert b"Dados Veganos Preenchidos com Sucesso" in response.data
