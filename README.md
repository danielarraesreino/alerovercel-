# AleroPrice - Sistema de Gestão para Restaurantes

O AleroPrice é um sistema modularizado para gestão de custos, estoque e precificação para restaurantes, desenvolvido com Flask e SQLAlchemy.

## Funcionalidades

- **Gestão de Fornecedores**: Cadastro e consulta de fornecedores
- **Gestão de Produtos/Insumos**: Cadastro, consulta e movimentação de estoque
- **Importação de NFe**: Leitura de arquivos XML de Notas Fiscais Eletrônicas
- **Controle de Estoque**: Registro de entradas/saídas e alertas de estoque mínimo
- **Ficha Técnica de Pratos**: Cálculo de custos diretos por porção
- **Controle de Custos Indiretos**: Rateio de custos fixos e indiretos
- **Precificação Automática**: Sugestão de preços baseados em custos e margem de lucro

## Estrutura do Projeto

```
app/
    __init__.py           # Fábrica de aplicação e registro de Blueprints
    config.py             # Configurações do sistema
    extensions.py         # Instâncias de extensões (SQLAlchemy, etc.)
    models/               # Modelos de dados
        modelo_fornecedor.py
        modelo_produto.py
        modelo_nfe.py
        modelo_estoque.py
        modelo_prato.py
        modelo_custo.py
    routes/               # Blueprints e rotas
        estoque/
        fornecedores/
        nfe/
        pratos/
        produtos/
    utils/                # Funções auxiliares
        nfe_parser.py
        calculos.py
    scripts/              # Scripts de inicialização
        create_db.py
        seed_data.py
requirements.txt
run.py
```

## Modelo de Dados

O sistema utiliza um banco de dados relacional normalizado com as seguintes tabelas principais:

- **Fornecedor**: Informações de fornecedores de insumos
- **Produto**: Produtos/insumos utilizados nos pratos
- **NFNota**: Notas fiscais importadas
- **NFItem**: Itens das notas fiscais
- **EstoqueMovimentacao**: Registro de movimentações de estoque
- **Prato**: Receitas/pratos do cardápio
- **PratoInsumo**: Composição dos pratos (produtos e quantidades)
- **CustoIndireto**: Registro de custos fixos para rateio

## Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório ou extraia os arquivos

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure o banco de dados:
   ```
   python -m app.scripts.create_db
   ```

4. (Opcional) Carregue dados de exemplo:
   ```
   python -m app.scripts.seed_data
   ```

5. Execute a aplicação:
   ```
   python run.py
   ```

## Funcionalidades Principais

### Importação de NFe

O sistema permite importar arquivos XML de Notas Fiscais Eletrônicas, extraindo automaticamente:

- Dados do fornecedor (criando novo se necessário)
- Produtos/insumos (criando novos se necessário)
- Valores fiscais e totais
- Registro automático de entrada no estoque

### Controle de Estoque

- Registro de todas as movimentações (entradas e saídas)
- Cálculo de estoque atual
- Alertas de estoque mínimo
- Relatórios de produtos em falta

### Ficha Técnica de Pratos

- Cadastro detalhado de receitas/pratos
- Registro de insumos com quantidades
- Cálculo automático de custos diretos
- Rateio de custos indiretos
- Sugestão de preço de venda baseado na margem desejada

### Gestão de Desperdício (Novo)

- **Monitoramento**: Registro de desperdícios por categoria, motivo e responsável
- **Metas**: Definição e acompanhamento de metas de redução
- **Relatórios**: Dashboards visuais e relatórios detalhados por período

### Previsão de Demanda (Novo)

- **Análise Histórica**: Utiliza dados passados para identificar padrões
- **Sazonalidade**: Ajustes automáticos para períodos de alta/baixa
- **Planejamento de Compras**: Sugestão de reposição baseada na previsão de vendas

## Cálculos de Custo

### Custo Direto

Calculado como a soma dos custos dos insumos utilizados na receita:

```
custo_direto_total = ∑(quantidade_insumo * preco_unitario_insumo)
custo_direto_por_porcao = custo_direto_total / rendimento
```

### Custo Indireto

Rateio dos custos fixos (aluguel, energia, salários, etc.):

```
custo_indireto_por_porcao = total_custos_indiretos / total_porcoes_produzidas
```

### Preço de Venda Sugerido

Calculado com base nos custos e na margem desejada:

```
preco_venda = (custo_direto_por_porcao + custo_indireto_por_porcao) * (1 + margem/100)
```

## Extensões Futuras

## Extensões Futuras

- Interface para definição de cardápios
- Integração com sistemas de PDV
- Dashboard para análise de lucratividade (Expandido)
- Controle de validade de produtos perecíveis (Melhorias)
