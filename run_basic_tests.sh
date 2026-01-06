#!/bin/bash

# Script para executar apenas os testes bu00e1sicos que su00e3o compatiu00edveis com a estrutura atual do AleroPrice

# Definir cores para saiu00edda
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Criar diretórios necessários
mkdir -p reports/coverage

# Ativar o ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Executar testes bu00e1sicos de unidade
echo -e "\n${BLUE}Executando testes bu00e1sicos de unidade...${NC}"
pytest tests/unit/test_basics.py -v

# Executar testes bu00e1sicos de integrau00e7u00e3o
echo -e "\n${BLUE}Executando testes bu00e1sicos de integrau00e7u00e3o...${NC}"
pytest tests/integration/test_basico_integracao.py -v

# Iniciar o servidor para testes E2E
echo -e "\n${YELLOW}Iniciando o servidor para testes E2E...${NC}"
echo -e "${YELLOW}(Os testes E2E requerem que o servidor esteja rodando em outra janela do terminal)${NC}"
echo -e "${YELLOW}Execute 'python run.py' em um terminal separado antes de prosseguir.${NC}"
echo -e "${YELLOW}Pressione Enter quando o servidor estiver rodando...${NC}"
read

# Executar testes E2E bu00e1sicos
echo -e "\n${BLUE}Executando testes E2E bu00e1sicos...${NC}"
pytest tests/e2e/test_e2e_basico.py -v

echo -e "\n${GREEN}Testes concluiu00eddos. Verifique os resultados acima.${NC}"
echo -e "${YELLOW}Screenshots dos testes E2E estu00e3o disponiu00edveis no diretório 'reports/'${NC}"
