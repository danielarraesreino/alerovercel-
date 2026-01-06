# Testes do AleroPrice

Este diretório contém todos os testes automatizados do sistema AleroPrice, organizados em três categorias principais:

- **Testes de Unidade**: Verificam o funcionamento individual de componentes isolados do sistema
- **Testes de Integração**: Verificam como diferentes componentes funcionam juntos
- **Testes End-to-End (E2E)**: Simulam a interação de um usuário real com a aplicação

## Estrutura de Diretórios

```
tests/
├── unit/               # Testes de unidade
│   ├── test_modelo_previsao.py        # Testes dos modelos de previsão
│   ├── test_modelo_desperdicio.py     # Testes dos modelos de desperdício
│   ├── test_rotas_previsao.py         # Testes das rotas de previsão
│   ├── test_rotas_desperdicio.py      # Testes das rotas de desperdício
│   └── test_database.py               # Testes específicos do banco de dados
├── integration/        # Testes de integração
│   ├── test_integracao_previsao.py    # Testes de integração do módulo de previsão
│   └── test_integracao_desperdicio.py # Testes de integração do módulo de desperdício
├── e2e/                # Testes end-to-end
│   ├── conftest.py                    # Configuração para testes e2e
│   ├── test_e2e_previsao.py           # Testes e2e do módulo de previsão
│   └── test_e2e_desperdicio.py        # Testes e2e do módulo de desperdício
└── conftest.py         # Configuração geral dos testes
```

## Requisitos

Todos os requisitos para executar os testes estão listados no arquivo `requirements.txt` na raiz do projeto. As principais dependências são:

- pytest: Framework de testes
- pytest-flask: Para testar aplicações Flask
- pytest-cov: Para gerar relatórios de cobertura de código
- pytest-playwright: Para testes de frontend
- pytest-html: Para gerar relatórios HTML
- pytest-sqlalchemy: Para testes de banco de dados

## Executando os Testes

O projeto inclui um script `run_tests.py` na raiz que facilita a execução de todos os testes ou de tipos específicos de teste.

### Executar todos os testes

```bash
./run_tests.py
```

### Executar apenas testes de unidade

```bash
./run_tests.py --unit
```

### Executar apenas testes de integração

```bash
./run_tests.py --integration
```

### Executar apenas testes de banco de dados

```bash
./run_tests.py --database
```

### Executar apenas testes end-to-end

```bash
./run_tests.py --e2e
```

### Gerar relatórios HTML

Adicione a flag `--html` para gerar relatórios HTML dos resultados dos testes:

```bash
./run_tests.py --html
```

Os relatórios serão salvos no diretório `reports/`.

### Gerar relatórios de cobertura de código

Adicione a flag `--coverage` para gerar relatórios de cobertura de código:

```bash
./run_tests.py --coverage
```

Os relatórios de cobertura serão salvos no diretório `reports/coverage/`.

## Banco de Dados de Teste

Os testes utilizam um banco de dados SQLite em memória para garantir que os testes sejam isolados e não afetem o banco de dados de desenvolvimento ou produção.

## Testes de Frontend com Playwright

Os testes E2E utilizam Playwright para simular a interação de um usuário real com a aplicação através de um navegador automatizado. Estes testes verificam:

- Navegação entre páginas
- Preenchimento e envio de formulários
- Visualização de dados
- Interações com componentes da interface
- Downloads de arquivos

## Boas Práticas

1. **Isolamento**: Cada teste deve ser independente e não depender do estado deixado por outros testes.
2. **Clareza**: Os testes devem ter nomes descritivos que expliquem o que está sendo testado.
3. **Organização**: Mantenha os testes organizados por funcionalidade e tipo.
4. **Cobertura**: Busque manter uma alta cobertura de código, especialmente em áreas críticas.
5. **Fixtures**: Use fixtures para configurar o ambiente de teste e compartilhar código entre testes.
