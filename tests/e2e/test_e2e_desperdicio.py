import pytest
from playwright.async_api import expect
import re
import time
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_navegacao_modulo_desperdicio(page):
    """Testa a navegau00e7u00e3o bu00e1sica pelo mu00f3dulo de monitoramento de desperdu00edcio"""
    # 1. Acessar a pu00e1gina inicial
    await page.goto('http://localhost:5000/desperdicio/')
    await expect(page).to_have_title(re.compile(r'AleroPrice.*Desperdu00edcio'))
    
    # 2. Verificar elementos principais do dashboard
    await expect(page.locator('h1:has-text("Dashboard de Desperdu00edcio")')).to_be_visible()
    
    # 3. Navegar para a pu00e1gina de categorias
    await page.click('a:has-text("Categorias")')
    await expect(page).to_have_url(re.compile(r'.*categorias'))
    await expect(page.locator('h1:has-text("Categorias de Desperdu00edcio")')).to_be_visible()
    
    # 4. Navegar para a pu00e1gina de registros
    await page.click('a:has-text("Registros")')
    await expect(page).to_have_url(re.compile(r'.*registros'))
    await expect(page.locator('h1:has-text("Registros de Desperdu00edcio")')).to_be_visible()
    
    # 5. Navegar para a pu00e1gina de metas
    await page.click('a:has-text("Metas")')
    await expect(page).to_have_url(re.compile(r'.*metas'))
    await expect(page.locator('h1:has-text("Metas de Reduu00e7u00e3o")')).to_be_visible()
    
    # 6. Navegar para a pu00e1gina de relatu00f3rios
    await page.click('a:has-text("Relatu00f3rios")')
    await expect(page).to_have_url(re.compile(r'.*relatorios'))
    await expect(page.locator('h1:has-text("Relatu00f3rios de Desperdu00edcio")')).to_be_visible()

@pytest.mark.asyncio
async def test_criar_categoria_desperdicio(page):
    """Testa a criau00e7u00e3o de uma nova categoria de desperdu00edcio"""
    # 1. Acessar a pu00e1gina de criau00e7u00e3o de categoria
    await page.goto('http://localhost:5000/desperdicio/criar-categoria')
    await expect(page.locator('h1:has-text("Criar Categoria de Desperdu00edcio")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    nome_categoria = f"Categoria Teste {datetime.now().strftime('%H%M%S')}"
    await page.fill('input[name="nome"]', nome_categoria)
    await page.fill('input[name="descricao"]', "Descriu00e7u00e3o da categoria de teste")
    await page.fill('input[name="cor"]', "#3366CC")
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*categorias'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 5. Verificar se a nova categoria aparece na lista
    await expect(page.locator(f'td:has-text("{nome_categoria}")')).to_be_visible()

@pytest.mark.asyncio
async def test_editar_categoria_desperdicio(page):
    """Testa a ediu00e7u00e3o de uma categoria de desperdu00edcio existente"""
    # 1. Acessar a pu00e1gina de categorias
    await page.goto('http://localhost:5000/desperdicio/categorias')
    
    # 2. Clicar no botu00e3o de editar da primeira categoria
    await page.click('a:has-text("Editar"):nth-of-type(1)')
    await expect(page.locator('h1:has-text("Editar Categoria de Desperdu00edcio")')).to_be_visible()
    
    # 3. Modificar o formulu00e1rio
    novo_nome = f"Categoria Editada {datetime.now().strftime('%H%M%S')}"
    await page.fill('input[name="nome"]', novo_nome)
    await page.fill('input[name="descricao"]', "Descriu00e7u00e3o atualizada pelo teste")
    await page.fill('input[name="cor"]', "#FF9900")
    
    # 4. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 5. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*categorias'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 6. Verificar se a categoria editada aparece na lista
    await expect(page.locator(f'td:has-text("{novo_nome}")')).to_be_visible()

@pytest.mark.asyncio
async def test_registrar_desperdicio(page):
    """Testa o registro de um novo desperdu00edcio"""
    # 1. Acessar a pu00e1gina de registro de desperdu00edcio
    await page.goto('http://localhost:5000/desperdicio/registrar')
    await expect(page.locator('h1:has-text("Registrar Desperdu00edcio")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    await page.select_option('select[name="categoria_id"]', '1')  # Selecionar a primeira categoria
    await page.select_option('select[name="produto_id"]', '1')  # Selecionar o primeiro produto
    await page.fill('input[name="quantidade"]', '3.5')
    await page.select_option('select[name="unidade"]', 'kg')
    await page.fill('input[name="valor"]', '35.00')
    await page.fill('input[name="data_registro"]', datetime.now().strftime('%Y-%m-%d'))
    await page.fill('textarea[name="observacao"]', "Observau00e7u00e3o do registro de teste")
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*registros'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 5. Verificar se o novo registro aparece na lista
    await expect(page.locator('td:has-text("Observa")')).to_be_visible()

@pytest.mark.asyncio
async def test_criar_meta_desperdicio(page):
    """Testa a criau00e7u00e3o de uma meta de reduu00e7u00e3o de desperdu00edcio"""
    # 1. Acessar a pu00e1gina de criau00e7u00e3o de meta
    await page.goto('http://localhost:5000/desperdicio/criar-meta')
    await expect(page.locator('h1:has-text("Criar Meta de Reduu00e7u00e3o")')).to_be_visible()
    
    # 2. Preencher o formulu00e1rio
    await page.select_option('select[name="categoria_id"]', '1')  # Selecionar a primeira categoria
    await page.fill('input[name="valor_inicial"]', '1000')
    await page.fill('input[name="percentual_reducao"]', '20')
    
    data_inicio = datetime.now().date()
    data_fim = data_inicio + timedelta(days=60)
    
    await page.fill('input[name="data_inicio"]', data_inicio.strftime('%Y-%m-%d'))
    await page.fill('input[name="data_fim"]', data_fim.strftime('%Y-%m-%d'))
    await page.fill('textarea[name="descricao"]', "Meta de teste criada via e2e")
    
    # 3. Enviar o formulu00e1rio
    await page.click('button[type="submit"]')
    
    # 4. Verificar redirecionamento e mensagem de sucesso
    await expect(page).to_have_url(re.compile(r'.*metas'))
    await expect(page.locator('div.alert-success')).to_be_visible()
    
    # 5. Verificar se a nova meta aparece na lista
    await expect(page.locator('td:has-text("Meta de teste criada via e2e")')).to_be_visible()

@pytest.mark.asyncio
async def test_visualizar_registro_desperdicio(page):
    """Testa a visualizau00e7u00e3o detalhada de um registro de desperdu00edcio"""
    # 1. Acessar a pu00e1gina de registros
    await page.goto('http://localhost:5000/desperdicio/registros')
    
    # 2. Clicar no botu00e3o de visualizar do primeiro registro
    await page.click('a:has-text("Visualizar"):nth-of-type(1)')
    
    # 3. Verificar se estu00e1 na pu00e1gina de detalhes do registro
    await expect(page.locator('h1:has-text("Detalhes do Registro")')).to_be_visible()
    
    # 4. Verificar se os detalhes do registro estu00e3o presentes
    await expect(page.locator('h3:has-text("Informau00e7u00f5es Gerais")')).to_be_visible()
    await expect(page.locator('h3:has-text("Produto")')).to_be_visible()
    await expect(page.locator('h3:has-text("Categoria")')).to_be_visible()

@pytest.mark.asyncio
async def test_exportar_registros_desperdicio(page):
    """Testa a exportau00e7u00e3o de registros de desperdu00edcio"""
    # 1. Acessar a pu00e1gina de exportau00e7u00e3o de registros
    await page.goto('http://localhost:5000/desperdicio/exportar-registros')
    await expect(page.locator('h1:has-text("Exportar Registros de Desperdu00edcio")')).to_be_visible()
    
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
