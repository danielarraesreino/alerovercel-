import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

# Dados de teste
FORNECEDORES = [
    {"cnpj": "12345678000101", "razao_social": "Fornecedor Um", "nome_fantasia": "Fantasia Um", "endereco": "Rua 1", "cidade": "Cidade 1", "estado": "SP", "cep": "01001000", "telefone": "111111111", "email": "um@teste.com", "inscricao_estadual": "123456"},
    {"cnpj": "98765432000199", "razao_social": "Fornecedor Dois", "nome_fantasia": "Fantasia Dois", "endereco": "Rua 2", "cidade": "Cidade 2", "estado": "RJ", "cep": "20020000", "telefone": "222222222", "email": "dois@teste.com", "inscricao_estadual": "654321"}
]
PRODUTOS = [
    {"nome": "Produto Um", "codigo": "P001", "descricao": "Desc 1", "unidade_medida": "kg", "preco_unitario": "10.50", "estoque_minimo": "5", "estoque_atual": "10", "categoria": "Alimento", "marca": "Marca 1"},
    {"nome": "Produto Dois", "codigo": "P002", "descricao": "Desc 2", "unidade_medida": "l", "preco_unitario": "20.00", "estoque_minimo": "2", "estoque_atual": "5", "categoria": "Bebida", "marca": "Marca 2"}
]
# Adicione dados de PRATOS, CARDAPIOS, etc. conforme necessário

def wait_and_click(driver, by, value):
    WebDriverWait(driver, TIMEOUT).until(EC.element_to_be_clickable((by, value))).click()

def wait_and_send_keys(driver, by, value, keys):
    el = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((by, value)))
    el.clear()
    el.send_keys(keys)

def criar_fornecedores(driver):
    for f in FORNECEDORES:
        driver.get(f"{BASE_URL}/fornecedores/criar")
        wait_and_send_keys(driver, By.NAME, "cnpj", f["cnpj"])
        wait_and_send_keys(driver, By.NAME, "razao_social", f["razao_social"])
        wait_and_send_keys(driver, By.NAME, "nome_fantasia", f["nome_fantasia"])
        wait_and_send_keys(driver, By.NAME, "endereco", f["endereco"])
        wait_and_send_keys(driver, By.NAME, "cidade", f["cidade"])
        wait_and_send_keys(driver, By.NAME, "estado", f["estado"])
        wait_and_send_keys(driver, By.NAME, "cep", f["cep"])
        wait_and_send_keys(driver, By.NAME, "telefone", f["telefone"])
        wait_and_send_keys(driver, By.NAME, "email", f["email"])
        wait_and_send_keys(driver, By.NAME, "inscricao_estadual", f["inscricao_estadual"])
        wait_and_click(driver, By.XPATH, "//button[@type='submit']")
        time.sleep(1)

def criar_produtos(driver):
    for i, p in enumerate(PRODUTOS):
        driver.get(f"{BASE_URL}/produtos/criar")
        wait_and_send_keys(driver, By.NAME, "nome", p["nome"])
        wait_and_send_keys(driver, By.NAME, "codigo", p["codigo"])
        wait_and_send_keys(driver, By.NAME, "descricao", p["descricao"])
        wait_and_send_keys(driver, By.NAME, "unidade_medida", p["unidade_medida"])
        wait_and_send_keys(driver, By.NAME, "preco_unitario", p["preco_unitario"])
        wait_and_send_keys(driver, By.NAME, "estoque_minimo", p["estoque_minimo"])
        wait_and_send_keys(driver, By.NAME, "estoque_atual", p["estoque_atual"])
        wait_and_send_keys(driver, By.NAME, "categoria", p["categoria"])
        wait_and_send_keys(driver, By.NAME, "marca", p["marca"])
        # Seleciona o fornecedor correspondente
        fornecedor_nome = FORNECEDORES[i]["razao_social"]
        fornecedor_select = WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.NAME, "fornecedor_id")))
        for option in fornecedor_select.find_elements(By.TAG_NAME, 'option'):
            if fornecedor_nome in option.text:
                option.click()
                break
        wait_and_click(driver, By.XPATH, "//button[@type='submit']")
        time.sleep(1)

def main():
    driver = webdriver.Firefox()
    driver.maximize_window()
    try:
        criar_fornecedores(driver)
        criar_produtos(driver)
        # Adicione chamadas para criar_pratos(driver), criar_cardapios(driver), etc.
        print("Testes concluídos com sucesso!")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
