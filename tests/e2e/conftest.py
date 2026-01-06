import pytest
import os
from app import create_app, db
from app.models import *
from pytest_playwright.pytest_playwright import Page
import time
from datetime import datetime, timedelta

@pytest.fixture(scope='session')
def app_for_e2e():
    """Fixture que cria uma instu00e2ncia do aplicativo Flask para testes e2e"""
    app = create_app('testing')
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    
    with app.app_context():
        db.create_all()
        
        # Criamos alguns dados de teste para os cenu00e1rios e2e
        _criar_dados_teste(db.session)
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
async def browser_context(browser, app_for_e2e):
    """Inicia o aplicativo Flask e configura o contexto do navegador para testes"""
    # Iniciar o servidor Flask em uma porta especu00edfica
    server = app_for_e2e.test_server()
    server.start()
    
    # Criar o contexto do navegador
    context = await browser.new_context()
    
    yield context
    
    # Limpar recursos apu00f3s o teste
    await context.close()
    server.stop()

@pytest.fixture(scope='function')
async def page(browser_context):
    """Cria uma nova pu00e1gina para cada teste"""
    page = await browser_context.new_page()
    yield page
    await page.close()

def _criar_dados_teste(session):
    """Cria dados de teste para os cenu00e1rios e2e"""
    # Criar produtos para teste
    produtos = [
        Produto(
            nome="Arroz",
            descricao="Arroz branco tipo 1",
            unidade="kg",
            preco_custo=5.0,
            preco_venda=8.0,
            codigo_barras="7891234567890",
            estoque_minimo=10,
            estoque_atual=50
        ),
        Produto(
            nome="Feiju00e3o",
            descricao="Feiju00e3o carioca",
            unidade="kg",
            preco_custo=7.0,
            preco_venda=12.0,
            codigo_barras="7891234567891",
            estoque_minimo=8,
            estoque_atual=30
        ),
        Produto(
            nome="u00d3leo",
            descricao="u00d3leo de soja",
            unidade="un",
            preco_custo=3.5,
            preco_venda=7.0,
            codigo_barras="7891234567892",
            estoque_minimo=12,
            estoque_atual=25
        )
    ]
    
    for produto in produtos:
        session.add(produto)
    
    # Criar categorias de desperdu00edcio
    categorias = [
        CategoriaDesperdicio(nome="Vencido", descricao="Alimentos vencidos", cor="#FF0000"),
        CategoriaDesperdicio(nome="Sobra", descricao="Sobras de produu00e7u00e3o", cor="#FFA500"),
        CategoriaDesperdicio(nome="Dano", descricao="Alimentos danificados", cor="#FFFF00")
    ]
    
    for categoria in categorias:
        session.add(categoria)
    
    session.commit()
    
    # Criar histu00f3rico de vendas
    produto_ids = [p.id for p in produtos]
    for produto_id in produto_ids:
        for i in range(30):  # 30 dias de histu00f3rico
            venda = HistoricoVendas(
                data_venda=datetime.now().date() - timedelta(days=i),
                produto_id=produto_id,
                quantidade=10 + (i % 5),
                valor=(10 + (i % 5)) * produtos[produto_id-1].preco_venda
            )
            session.add(venda)
    
    # Criar alguns registros de desperdu00edcio
    categoria_ids = [c.id for c in categorias]
    for produto_id in produto_ids:
        for categoria_id in categoria_ids:
            for i in range(5):  # 5 registros por combinau00e7u00e3o
                registro = RegistroDesperdicio(
                    categoria_id=categoria_id,
                    produto_id=produto_id,
                    quantidade=1.5 + (i % 3),
                    unidade=produtos[produto_id-1].unidade,
                    valor=(1.5 + (i % 3)) * produtos[produto_id-1].preco_custo,
                    data_registro=datetime.now().date() - timedelta(days=i*2),
                    observacao=f"Registro de teste {i+1}"
                )
                session.add(registro)
    
    # Criar fatores de sazonalidade
    fatores = [
        FatorSazonalidade(tipo="dia_semana", valor=1.2, descricao="Segunda-feira"),
        FatorSazonalidade(tipo="dia_semana", valor=0.9, descricao="Teru00e7a-feira"),
        FatorSazonalidade(tipo="mes", valor=1.3, descricao="Dezembro")
    ]
    
    for fator in fatores:
        session.add(fator)
    
    # Criar uma meta de reduu00e7u00e3o de desperdu00edcio
    meta = MetaDesperdicio(
        categoria_id=categoria_ids[0],
        valor_inicial=500.0,
        valor_meta=400.0,
        percentual_reducao=20.0,
        data_inicio=datetime.now().date(),
        data_fim=datetime.now().date() + timedelta(days=30),
        descricao="Meta para reduu00e7u00e3o de alimentos vencidos"
    )
    session.add(meta)
    
    session.commit()
