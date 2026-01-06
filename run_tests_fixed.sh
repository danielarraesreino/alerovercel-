#!/bin/bash

# Ativar ambiente virtual
. "$(dirname "$0")/venv/bin/activate"

# Criar diretório para relatórios
mkdir -p reports

# Executar testes unitários
echo "==== Executando testes unitários ===="
pytest tests/unit/ -v --cov=app --cov-report=term --cov-report=html:reports/coverage

# Executar testes de integração
echo "\n==== Executando testes de integração ===="
pytest tests/integration/ -v --cov=app --cov-report=term --cov-append

# Executar testes E2E básicos
echo "\n==== Executando testes E2E básicos ===="
pytest tests/e2e/test_e2e_basico.py -v --cov=app --cov-report=term --cov-append

# Gerar relatório combinado
echo "\n==== Gerando relatório de cobertura combinado ===="
coverage report
coverage html -d reports/full_coverage

echo "\nRelatório completo disponível em: $(pwd)/reports/full_coverage/index.html"

echo "\n==== RESUMO DOS RESULTADOS ===="
echo "Verifique o relatório de cobertura para detalhes sobre o que precisa ser melhorado."
