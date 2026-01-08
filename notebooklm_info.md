# AleroPrice: Manual Técnico Completo (Contexto para IA)

Este documento exaustivo descreve a arquitetura, modelos de dados, lógica de negócios e decisões de design do sistema AleroPrice. Ele foi projetado para servir como "memória técnica" para modelos de linguagem (como NotebookLM) auxiliarem no desenvolvimento futuro.

---

## 1. Visão Geral da Arquitetura

*   **Stack Principal:** Python 3.9+, Flask, SQLAlchemy ORM.
*   **Banco de Dados:**
    *   **Desenvolvimento:** SQLite.
    *   **Produção (Vercel):** PostgreSQL (Neon/Supabase/etc).
*   **Frontend:** Server-Side Rendering (Jinja2) com Bootstrap 5 e Chart.js.
*   **Deployment:** Vercel (Serverless Functions).
    *   *Nota Crítica:* O ambiente serverless limita o tempo de execução e conexões. O código foi otimizado para evitar N+1 queries e timeouts (ver seção "Otimizações").

---

## 2. Modelagem de Dados (`app/models`)

O sistema gira em torno da gestão de custos gastronômicos (Engenharia de Cardápio).

### 2.1 Núcleo de Produtos e Fichas Técnicas
*   **`Produto` (`modelo_produto.py`)**: A matéria-prima básica.
    *   Campos Chave: `nome`, `unidade` (kg, lt, un), `preco_atual`, `estoque_atual`.
    *   *Lógica:* Preço atual é atualizado automaticamente na importação de NFEs.
*   **`Prato` (`modelo_prato.py`)**: A receita ou ficha técnica.
    *   Campos Chave: `rendimento` (qtd que a receita produz), `porcoes_rendimento` (divisão para venda).
    *   **Propriedades Calculadas (CRÍTICO):**
        *   `custo_direto_total`: Soma de `insumo.custo_total`.
        *   `custo_total_por_porcao`: (Custo Direto / Porções) + Custo Indireto.
*   **`PratoInsumo` (`modelo_prato.py`)**: Tabela de ligação N:M entre Prato e Produto.
    *   Define a quantidade de matéria-prima usada na receita.

### 2.2 Gestão de Estoque e Notas Fiscais
*   **`NFNota` (`modelo_nfe.py`)**: Cabeçalho da Nota Fiscal Eletrônica.
    *   Armazena `chave_acesso`, `fornecedor_id`, `valor_total`.
*   **`NFItem` (`modelo_nfe.py`)**: Itens individuais de uma nota.
    *   Vinculado a um `Produto`. Ao ser importado, atualiza o preço e estoque do produto.
*   **`MovimentoEstoque` (`modelo_estoque.py`)**: Log de auditoria de todas as entradas e saídas.

### 2.3 Financeiro e Inteligência
*   **`HistoricoVendas` (`modelo_previsao.py`)**: Registro de vendas diárias.
    *   Importado de sistemas PDV ou inputado manualmente. Essencial para o cálculo de lucratividade real.
*   **`CustoIndireto` (`modelo_custo.py`)**: Custos fixos (Aluguel, Luz) e Investimentos.
    *   *Funcionalidade de Rateio:* Permite distribuir esses custos entre os pratos vendidos para calcular o lucro líquido real.
*   **`RegistroDesperdicio` (`modelo_desperdicio.py`)**: Controle de perdas.

---

## 3. Lógica de Negócios Crítica (`app/routes`)

### 3.1 Motor de Importação de NFE (`nfe/views.py`)
O sistema possui um parser XML robusto ("anti-frágil") projetado para suportar variações no padrão nacional.

*   **Algoritmo de Busca Recursiva:**
    *   Não confia na estrutura padrão `nfeProc > NFe > infNFe`.
    *   Usa uma função recursiva (`buscar_chave`) que varre a árvore XML inteira até achar a tag `infNFe`, ignorando envelopes ou estruturas aninhadas incorretas de ERPs de terceiros.
*   **Tratamento de Namespaces:**
    *   Limpa automaticamente namespaces (ex: `ns1:`, `http://...`) usando `namespaces={URI: None}` no `xmltodict`. Isso previne erros de "Chave não encontrada".
*   **Automação:**
    *   Cria fornecedores desconhecidos automaticamente.
    *   Cria produtos desconhecidos automaticamente (baseado no código e nome).

### 3.2 Dashboard de Lucratividade (`dashboard/views.py`)
O painel principal foi reescrito para alta performance em ambientes serverless.

*   **Problema Resolvido:** O ORM do SQLAlchemy causava "N+1 Queries" ao iterar vendas e calcular custo de prato por prato, gerando timeouts (Erro 500).
*   **Solução Híbrida (SQL + Python):**
    1.  **Carregamento em Massa:** Carrega *todos* os Pratos e Insumos em uma única query otimizada (`joinedload`).
    2.  **Agregação SQL:** O banco apenas soma as quantidades vendidas agrupadas por mês/item.
    3.  **Cônciliação em Memória:** O Python cruza o "Mapa de Custos" (passo 1) com o "Resumo de Vendas" (passo 2).
    *   *Resultado:* Redução de ~2000 queries para ~4 queries por load de página.
*   **Compatibilidade Multi-Banco:**
    *   Detecta dinamicamente se está rodando em **PostgreSQL** (Vercel) ou **SQLite** (Local).
    *   Usa `to_char(data, 'YYYY-MM')` para Postgres.
    *   Usa `strftime('%Y-%m', data)` para SQLite.

### 3.3 Rateio de Custos (`custos/views.py`)
Módulo para distribuição de custos fixos.
*   Calcula o "Custo Indireto por Prato" dividindo (Total Custos Fixos / Total Vendas Estimadas ou Realizadas).
*   Persiste esse valor no modelo `Prato` para que o preço de venda sugerido cubra não apenas os insumos, mas também a operação.

---

## 4. Pontos de Atenção para Expansão

Se você (IA) for sugerir novas features, considere:

1.  **Limites da Vercel:**
    *   Evite processamentos longos (>10s) na thread principal. Para tarefas pesadas (ex: reprocessar todo estoque de 5 anos), use *Background Tasks* ou processe em chunks via frontend.

2.  **Integridade de Dados:**
    *   O preço do insumo mexe diretamente na margem do prato. Qualquer feature de "Histórico de Preços" deve considerar versionamento de ficha técnica se quiser precisão histórica absoluta (hoje o sistema usa o custo *atual* para cálculos históricos, o que é uma aproximação aceita).

3.  **Frontend Server-Side:**
    *   O sistema usa Jinja2. Não sugira componentes React/Vue complexos a menos que proponha uma reescrita da camada de view para uma API REST/GraphQL. Mantenha-se no padrão "Thin Client, Smart Server".

4.  **Testes:**
    *   Use `python3 debug_xml.py` para testar parsers isoladamente.
    *   Sempre valide queries complexas contra os dois dialetos (SQLite/Postgres).

---

## 5. Comandos Úteis

*   **Rodar Local:** `python3 run.py`
*   **Resetar Banco (Nuclear):** Acessar rota `/reset-db` (apenas dev).
*   **Seed de Dados:** Acessar rota `/seed-vegan`.
