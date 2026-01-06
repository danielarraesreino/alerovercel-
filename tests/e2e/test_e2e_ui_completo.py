import pytest
import re
from playwright.sync_api import expect
from datetime import datetime, timedelta

# Teste para verificar toda a navegação principal (100% cobertura da UI)

@pytest.mark.ui
def test_navegacao_completa(page):
    """Testa a navegação completa por todas as seções principais da aplicação"""
    # Acessar a página inicial
    page.goto("http://localhost:5000/")
    expect(page).to_have_title(re.compile("AleroPrice"))
    
    # Verificar elementos principais do dashboard
    expect(page.locator(".dashboard-header")).to_be_visible()
    expect(page.locator("text=Dashboard")).to_be_visible()
    
    # Navegar para todas as seções principais e verificar se carregam corretamente
    sections = [
        ("/desperdicio/", "Monitoramento de Desperdício"),
        ("/previsao/", "Previsão de Demanda"),
        ("/produtos/", "Gestão de Produtos"),
        ("/cardapios/", "Cardápios"),
        ("/estoque/", "Controle de Estoque"),
        ("/fornecedores/", "Fornecedores"),
        ("/pratos/", "Pratos"),
        ("/nfe/", "Notas Fiscais")
    ]
    
    for url, title in sections:
        # Navegar para a seção
        page.goto(f"http://localhost:5000{url}")
        
        # Verificar se a página carregou corretamente
        expect(page).to_have_url(re.compile(url))
        expect(page.locator(f"text={title}")).to_be_visible()
        
        # Verificar se há uma tabela, lista ou outro elemento principal
        # Assumindo que cada página principal tem ou uma tabela ou um gráfico ou cards
        count = page.locator("table, .chart-container, .card").count()
        assert count > 0, f"Não encontrou elementos principais na página {url}"
        
        # Verificar se há botões de ação (como "Adicionar", "Novo", etc)
        action_button = page.locator("a.btn-primary, button.btn-primary")
        if action_button.count() > 0:
            # Clicar no botão e verificar se leva a um formulário
            action_button.first.click()
            
            # Verificar se há formulário
            form_count = page.locator("form").count()
            assert form_count > 0, f"Não encontrou formulário após clicar no botão de ação na página {url}"
            
            # Voltar para a página principal da seção
            page.goto(f"http://localhost:5000{url}")

@pytest.mark.ui
def test_crud_desperdicio_completo(page):
    """Testa o fluxo completo de CRUD para desperdício"""
    # Acessar módulo de desperdício
    page.goto("http://localhost:5000/desperdicio/")
    
    # 1. CRIAR: Acessar página de criar categoria
    page.click("text=Nova Categoria")
    
    # Preencher formulário
    page.fill("input[name=nome]", f"Categoria Teste E2E {datetime.now().strftime('%H%M%S')}")
    page.fill("textarea[name=descricao]", "Descrição criada por teste automatizado")
    page.fill("input[name=cor]", "#00FF00")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar se voltou para a lista com mensagem de sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # 2. LISTAR: Verificar se a categoria foi adicionada à lista
    expect(page.locator("table")).to_contain_text("Categoria Teste E2E")
    
    # 3. EDITAR: Encontrar e editar a categoria criada
    page.click("text=Editar >> nth=0")
    
    # Modificar descrição
    page.fill("textarea[name=descricao]", "Descrição atualizada por teste automatizado")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso na edição
    expect(page.locator(".alert-success")).to_be_visible()
    
    # 4. VISUALIZAR: Acessar detalhes da categoria
    page.click("text=Detalhes >> nth=0")
    
    # Verificar se está mostrando a descrição atualizada
    expect(page.locator(".card-body")).to_contain_text("Descrição atualizada por teste automatizado")
    
    # Voltar para a lista
    page.click("text=Voltar")
    
    # 5. EXCLUIR: Apagar a categoria de teste
    page.click("text=Excluir >> nth=0")
    
    # Confirmar exclusão (assumindo um modal de confirmação)
    page.click("button:has-text('Confirmar')")
    
    # Verificar exclusão bem-sucedida
    expect(page.locator(".alert-success")).to_be_visible()

@pytest.mark.ui
def test_crud_previsao_completo(page):
    """Testa o fluxo completo de CRUD para previsão de demanda"""
    # Acessar módulo de previsão
    page.goto("http://localhost:5000/previsao/")
    
    # 1. REGISTRAR VENDA: Acessar página de registro de venda
    page.click("text=Registrar Venda")
    
    # Preencher formulário (os campos exatos dependerão da implementação real)
    # Suponho que tenha um select para o item do cardápio
    page.select_option("select[name=cardapio_item_id]", value="1")  # Primeiro item
    page.fill("input[name=quantidade]", "5")
    page.fill("input[name=valor_unitario]", "25.50")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # 2. GERAR PREVISÃO: Acessar página de geração de previsão
    page.goto("http://localhost:5000/previsao/gerar")
    
    # Preencher formulário
    page.select_option("select[name=cardapio_item_id]", value="1")  # Primeiro item
    page.select_option("select[name=metodo]", value="media_movel")
    
    # Data inicial (atual)
    data_atual = datetime.now().strftime('%Y-%m-%d')
    page.fill("input[name=data_inicio]", data_atual)
    
    # Data final (7 dias depois)
    data_final = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    page.fill("input[name=data_fim]", data_final)
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # 3. VISUALIZAR PREVISÃO: Acessar lista de previsões
    page.goto("http://localhost:5000/previsao/listar")
    
    # Verificar se a previsão aparece na lista
    expect(page.locator("table")).to_contain_text("média móvel")
    
    # 4. VISUALIZAR DETALHES: Clicar em detalhes da previsão
    page.click("text=Detalhes >> nth=0")
    
    # Verificar se mostra os detalhes e um gráfico
    expect(page.locator(".chart-container")).to_be_visible()
    
    # 5. CRIAR FATOR SAZONAL: Acessar página de fatores sazonais
    page.goto("http://localhost:5000/previsao/fatores")
    page.click("text=Novo Fator")
    
    # Preencher formulário
    page.select_option("select[name=cardapio_item_id]", value="1")  # Primeiro item
    page.select_option("select[name=dia_semana]", value="5")  # Sábado
    page.fill("input[name=fator]", "1.2")
    page.fill("textarea[name=descricao]", "Aumento de 20% aos sábados")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()

@pytest.mark.ui
def test_formularios_produtos(page):
    """Testa todos os formulários de gestão de produtos"""
    # Acessar módulo de produtos
    page.goto("http://localhost:5000/produtos/")
    
    # Criar novo produto
    page.click("text=Novo Produto")
    
    # Preencher formulário
    page.fill("input[name=nome]", f"Produto Teste E2E {datetime.now().strftime('%H%M%S')}")
    page.fill("textarea[name=descricao]", "Produto criado por teste automatizado")
    page.select_option("select[name=unidade_medida]", value="kg")
    page.fill("input[name=preco_unitario]", "12.75")
    page.fill("input[name=estoque_atual]", "50")
    page.fill("input[name=estoque_minimo]", "10")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # Verificar listagem
    expect(page.locator("table")).to_contain_text("Produto Teste E2E")

@pytest.mark.ui
def test_fluxo_completo_cardapio(page):
    """Testa o fluxo completo de criação e gerenciamento de cardápio"""
    # Acessar módulo de cardápios
    page.goto("http://localhost:5000/cardapios/")
    
    # Criar novo cardápio
    page.click("text=Novo Cardápio")
    
    # Preencher formulário
    nome_cardapio = f"Cardápio Teste E2E {datetime.now().strftime('%H%M%S')}"
    page.fill("input[name=nome]", nome_cardapio)
    page.fill("textarea[name=descricao]", "Cardápio criado por teste automatizado")
    
    # Data inicial (atual)
    data_atual = datetime.now().strftime('%Y-%m-%d')
    page.fill("input[name=data_inicio]", data_atual)
    
    # Data final (30 dias depois)
    data_final = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    page.fill("input[name=data_fim]", data_final)
    
    page.select_option("select[name=tipo]", value="semanal")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # Adicionar seção ao cardápio (assumindo que após criar o cardápio redireciona para edição)
    page.click("text=Adicionar Seção")
    page.fill("input[name=nome]", "Seção de Teste")
    page.fill("textarea[name=descricao]", "Seção criada por teste automatizado")
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # Adicionar item à seção
    page.click("text=Adicionar Item")
    page.select_option("select[name=prato_id]", index=0)  # Seleciona o primeiro prato
    page.fill("input[name=preco_venda]", "25.90")
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # Verificar se o cardápio está na lista
    page.goto("http://localhost:5000/cardapios/")
    expect(page.locator("table")).to_contain_text(nome_cardapio)

@pytest.mark.ui
def test_fluxo_completo_estoque(page):
    """Testa o fluxo completo de operações de estoque"""
    # Acessar módulo de estoque
    page.goto("http://localhost:5000/estoque/")
    
    # Registrar movimentação de estoque
    page.click("text=Nova Movimentação")
    
    # Preencher formulário
    page.select_option("select[name=produto_id]", index=0)  # Seleciona o primeiro produto
    page.select_option("select[name=tipo]", value="entrada")
    page.fill("input[name=quantidade]", "10")
    page.fill("input[name=valor_unitario]", "15.75")
    page.fill("textarea[name=observacao]", "Movimentação criada por teste automatizado")
    
    # Enviar formulário
    page.click("button[type=submit]")
    
    # Verificar sucesso
    expect(page.locator(".alert-success")).to_be_visible()
    
    # Verificar se a movimentação aparece no histórico
    expect(page.locator("table")).to_contain_text("Movimentação criada por teste automatizado")

@pytest.mark.ui
def test_responsividade_todas_paginas(page):
    """Testa a responsividade em todas as páginas principais da aplicação"""
    # Lista de URLs para testar
    urls = [
        "/",                     # Dashboard
        "/desperdicio/",         # Módulo de desperdício
        "/previsao/",            # Módulo de previsão
        "/produtos/",            # Módulo de produtos
        "/cardapios/",           # Módulo de cardápios
        "/estoque/",             # Módulo de estoque
        "/fornecedores/",        # Módulo de fornecedores
        "/pratos/",              # Módulo de pratos
        "/nfe/"                  # Módulo de notas fiscais
    ]
    
    # Tamanhos de tela para testar
    viewport_sizes = [
        {"width": 1920, "height": 1080},  # Desktop grande
        {"width": 1366, "height": 768},   # Desktop comum
        {"width": 768, "height": 1024},   # Tablet retrato
        {"width": 414, "height": 896}     # Smartphone
    ]
    
    for url in urls:
        for size in viewport_sizes:
            # Configurar tamanho da viewport
            page.set_viewport_size({"width": size["width"], "height": size["height"]})
            
            # Acessar a URL
            page.goto(f"http://localhost:5000{url}")
            
            # Verificar se a página carregou sem erros
            expect(page).to_have_url(re.compile(url))
            
            # Verificar se o conteúdo principal está visível
            content = page.locator(".container, .container-fluid")
            expect(content).to_be_visible()
            
            # No modo mobile, verificar se o menu hamburguer está presente e funciona
            if size["width"] <= 768:
                hamburger = page.locator(".navbar-toggler")
                if hamburger.count() > 0:
                    expect(hamburger).to_be_visible()
                    hamburger.click()
                    
                    # Verificar se o menu se expande
                    expanded_menu = page.locator(".navbar-collapse.show")
                    expect(expanded_menu).to_be_visible()
