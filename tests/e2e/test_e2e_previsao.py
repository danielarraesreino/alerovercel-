import pytest
from playwright.async_api import expect
import re
import time
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_navegacao_modulo_previsao(page):
    """Testa a navegau00e7u00e3o bu00e1sica pelo mu00f3dulo de previsu00e3o de demanda"""
    # 1. Acessar a pu00e1gina inicial
    await page.goto('http://localhost:5000/previsao/')
    await expect(page).to_have_title(re.compile(r'AleroPrice.*Previsu00e3o'))
    
    # 2. Verificar elementos principais do dashboard
    await expect(page.locator('h1:has-text("Dashboard de Previsu00e3o")')).to_be_visible()
    
    # 3. Navegar para a pu00e1gina de histu00f3rico de vendas
    await page.click('a:has-text("Histu00f3rico de Vendas")')
    await expect(page).to_have_url(re.compile(r'.*historico'))
    await expect(page.locator('h1:has-text("Histu00f3rico de Vendas")')).to_be_visible()
    
    # 4. Navegar para a pu00e1gina de previsu00f5es
    await page.click('a:has-text("Previsu00f5es")')
    await expect(page).to_have_url(re.compile(r'.*previsoes'))
    await expect(page.locator('h1:has-text("Previsu00f5es Geradas")')).to_be_visible()
    
    # 5. Navegar para a pu00e1gina de fatores de sazonalidade
    await page.click('a:has-text("Fatores de Sazonalidade")')
    await expect(page).to_have_url(re.compile(r'.*fatores-sazonalidade'))
    await expect(page.locator('h1:has-text("Fatores de Sazonalidade")')).to_be_visible()

@pytest.mark.asyncio
async def test_registrar_venda(page):
    """Testa o registro de uma nova venda"""
    # 1. Acessar a pu00e1gina de registro de venda
    await page.goto('http://localhost:5000/previsao/registrar-venda')
    await expect(page.locator('h1:has-text("Registrar Venda")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    await page.select_option('select[name="produto_id"]', '1')  # Selecionar o primeiro produto
    await page.fill('input[name="data_venda"]', datetime.now().strftime('%Y-%m-%d'))
    await page.fill('input[name="quantidade"]', '25')
    await page.fill('input[name="valor"]', '200')
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*historico'))
    await expect(page.locator('div.alert-success')).to_be_visible()

@pytest.mark.asyncio
async def test_fluxo_completo_previsao(page):
    """Testa o fluxo completo de gerau00e7u00e3o e visualizau00e7u00e3o de previsu00e3o"""
    # 1. Acessar a pu00e1gina de gerau00e7u00e3o de previsu00e3o
    await page.goto('http://localhost:5000/previsao/gerar-previsao')
    await expect(page.locator('h1:has-text("Gerar Previsu00e3o")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    await page.select_option('select[name="produto_id"]', '1')  # Selecionar o primeiro produto
    
    data_inicio = datetime.now().date()
    data_fim = data_inicio + timedelta(days=7)
    
    await page.fill('input[name="data_inicio"]', data_inicio.strftime('%Y-%m-%d'))
    await page.fill('input[name="data_fim"]', data_fim.strftime('%Y-%m-%d'))
    await page.select_option('select[name="metodo"]', 'mu00e9dia_mu00f3vel')
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*previsoes'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 5. Clicar na previsu00e3o gerada para visualizar detalhes
    await page.click('a:has-text("Visualizar")')
    await expect(page.locator('h1:has-text("Detalhes da Previsu00e3o")')).to_be_visible()
    
    # 6. Verificar se o gru00e1fico de previsu00e3o estu00e1 presente
    await expect(page.locator('canvas')).to_be_visible()

@pytest.mark.asyncio
async def test_criar_fator_sazonalidade(page):
    """Testa a criau00e7u00e3o de um fator de sazonalidade"""
    # 1. Acessar a pu00e1gina de criau00e7u00e3o de fator de sazonalidade
    await page.goto('http://localhost:5000/previsao/criar-fator-sazonalidade')
    await expect(page.locator('h1:has-text("Criar Fator de Sazonalidade")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    await page.select_option('select[name="tipo"]', 'dia_semana')
    await page.fill('input[name="valor"]', '1.5')
    await page.fill('input[name="descricao"]', 'Su00e1bado')
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*fatores-sazonalidade'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 5. Verificar se o novo fator aparece na lista
    await expect(page.locator('td:has-text("Su00e1bado")')).to_be_visible()

@pytest.mark.asyncio
async def test_exportar_historico(page):
    """Testa a exportau00e7u00e3o de histu00f3rico de vendas"""
    # 1. Acessar a pu00e1gina de exportau00e7u00e3o de histu00f3rico
    await page.goto('http://localhost:5000/previsao/exportar-historico')
    await expect(page.locator('h1:has-text("Exportar Histu00f3rico de Vendas")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    data_inicio = datetime.now().date() - timedelta(days=30)
    data_fim = datetime.now().date()
    
    await page.fill('input[name="data_inicio"]', data_inicio.strftime('%Y-%m-%d'))
    await page.fill('input[name="data_fim"]', data_fim.strftime('%Y-%m-%d'))
    await page.select_option('select[name="formato"]', 'csv')
    
    # 3. Iniciar o download clicando no botu00e3o
    with page.expect_download() as download_info:
        await page.click('button[type="submit"]')
    
    # 4. Verificar se o download foi iniciado
    download = await download_info.value
    assert download.suggested_filename.endswith('.csv')
