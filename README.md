ifood_case – Análise de Teste A/B de Cupom

Visão geral
-----------

Este projeto é uma pipeline analítica completa, em nível de produção, para um teste A/B
avaliando uma campanha de cupom no contexto do iFood. A solução faz ingestão dos dados
brutos, constrói uma tabela fato analítica, calcula métricas RFM em nível de cliente,
executa a análise do teste A/B (incluindo testes estatísticos e avaliação financeira),
cria segmentos de usuários e gera visualizações e tabelas com os principais insights
de negócio.

Estrutura do projeto
--------------------

- `data/raw/` – arquivos brutos baixados (pedidos em JSON, consumidores, restaurantes, referência do teste A/B)
- `data/processed/` – datasets analíticos processados como `fact_orders` e `customer_metrics`
- `src/` – código-fonte Python
  - `ingestion.py` – download de arquivos, extração e carregamento em streaming
  - `processing.py` – limpeza de dados e preparação da tabela `fact_orders`
  - `feature_engineering.py` – métricas RFM em nível de cliente
  - `ab_test.py` – métricas do teste A/B, testes estatísticos e análise financeira
  - `segmentation.py` – segmentação RFM e desempenho do teste por segmento
  - `visualization.py` – gráficos das principais métricas e segmentos
  - `pipeline.py` – script de orquestração ponta a ponta
- `notebooks/analysis.ipynb` – análise exploratória e narrativa de negócio
- `outputs/charts/` – gráficos PNG gerados
- `outputs/tables/` – arquivos CSV (métricas do teste, métricas por segmento, resumo estatístico e financeiro)

Fontes de dados
---------------

- Pedidos: `https://data-architect-test-source.s3-sa-east-1.amazonaws.com/order.json.gz`
- Consumidores: `https://data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz`
- Restaurantes: `https://data-architect-test-source.s3-sa-east-1.amazonaws.com/restaurant.csv.gz`
- Referência do teste A/B: `https://data-architect-test-source.s3-sa-east-1.amazonaws.com/ab_test_ref.tar.gz`

Como executar
-------------

1. **Criar e ativar um ambiente virtual (recomendado)**  
   Use a ferramenta de sua preferência (`venv`, `conda`, etc.).

2. **Instalar dependências**

   ```bash
   pip install -r requirements.txt
   ```

3. **Rodar a pipeline ponta a ponta**

   A partir da raiz do projeto:

   ```bash
   python -m src.pipeline
   ```

   Isso irá:

   - baixar e extrair dados brutos em `data/raw/`
   - construir `fact_orders.csv` e `customer_metrics.csv` em `data/processed/`
   - calcular métricas do teste A/B, testes estatísticos e viabilidade financeira do cupom
   - salvar tabelas-resumo em `outputs/tables/`
   - gerar gráficos em `outputs/charts/`

4. **Abrir o notebook de análise**

   Inicie o Jupyter e abra `notebooks/analysis.ipynb` para seguir a narrativa da análise:

   ```bash
   jupyter notebook
   ```

Resumo da análise (alto nível)
------------------------------

A análise foca em:

- medir **conversão, pedidos por usuário, GMV e ticket médio (AOV)** entre grupo controle e tratamento
- verificar se as diferenças observadas são **estatisticamente significativas**
- calcular **GMV incremental, receita incremental, custo de cupom e lucro líquido** da campanha
- construir **segmentos RFM** (Champions, Loyal, Potential, At Risk, Low Engagement)
- identificar quais segmentos apresentam **maior uplift** e são mais atrativos para campanhas futuras

Os resultados detalhados podem ser vistos no notebook e nos arquivos CSV/PNG gerados.
