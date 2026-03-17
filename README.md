
# 🍔 iFood Case – Análise de Teste A/B de Cupom

## 📌 Visão geral

Este projeto implementa uma pipeline analítica completa, em nível de produção, para avaliar um teste A/B de uma campanha de cupons no contexto do iFood.

A solução cobre todo o fluxo de dados:

* ingestão de dados brutos
* transformação e modelagem analítica
* cálculo de métricas de cliente (RFM)
* análise estatística do teste A/B
* avaliação de impacto financeiro
* segmentação de usuários
* geração de outputs analíticos (tabelas e gráficos)

---

## ⚠️ Observação importante sobre o repositório

Este repositório **não inclui dados brutos, datasets processados nem outputs gerados**, pois esses arquivos estão listados no `.gitignore` para evitar versionamento de grandes volumes de dados.

Itens não versionados:

* `data/raw/` – dados brutos
* `data/processed/` – tabelas analíticas geradas
* `outputs/charts/` – gráficos
* `outputs/tables/` – resultados do teste

👉 Ou seja: **o repositório contém apenas o código e a estrutura do projeto**, sendo necessário executar a pipeline para reproduzir os resultados.

---

## 🗂️ Estrutura do projeto

```
.
├── data/
│   ├── raw/                # (ignorado) dados brutos
│   └── processed/          # (ignorado) dados processados
├── src/
│   ├── ingestion.py        # ingestão e download dos dados
│   ├── processing.py       # limpeza e criação da fact_orders
│   ├── feature_engineering.py  # métricas RFM
│   ├── ab_test.py          # análise estatística e financeira
│   ├── segmentation.py     # segmentação de clientes
│   ├── visualization.py    # geração de gráficos
│   └── pipeline.py         # orquestração ponta a ponta
├── notebooks/
│   └── analysis.ipynb      # análise exploratória e narrativa
├── outputs/
│   ├── charts/             # (ignorado) gráficos gerados
│   └── tables/             # (ignorado) tabelas de saída
└── README.md
```

---

## 📊 Fontes de dados

Os dados são baixados automaticamente pela pipeline a partir das seguintes fontes:

* Pedidos
  [https://data-architect-test-source.s3-sa-east-1.amazonaws.com/order.json.gz](https://data-architect-test-source.s3-sa-east-1.amazonaws.com/order.json.gz)

* Consumidores
  [https://data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz](https://data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz)

* Restaurantes
  [https://data-architect-test-source.s3-sa-east-1.amazonaws.com/restaurant.csv.gz](https://data-architect-test-source.s3-sa-east-1.amazonaws.com/restaurant.csv.gz)

* Referência do teste A/B
  [https://data-architect-test-source.s3-sa-east-1.amazonaws.com/ab_test_ref.tar.gz](https://data-architect-test-source.s3-sa-east-1.amazonaws.com/ab_test_ref.tar.gz)

---

## 🚀 Como executar

### 1. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a pipeline

```bash
python -m src.pipeline
```

A execução irá:

* baixar e extrair os dados
* gerar datasets analíticos (`fact_orders`, `customer_metrics`)
* calcular métricas do teste A/B
* executar testes estatísticos
* calcular impacto financeiro da campanha
* gerar tabelas e gráficos

---

## 📈 Escopo da análise

A análise cobre:

### Métricas principais

* Taxa de conversão
* Pedidos por usuário
* GMV (Gross Merchandise Value)
* Ticket médio (AOV)

### Estatística

* Testes de significância entre controle vs tratamento
* Validação de uplift

### Financeiro

* GMV incremental
* Receita incremental
* Custo de cupons
* Lucro líquido da campanha

### Segmentação

* RFM (Recency, Frequency, Monetary)

* Segmentos:

  * Champions
  * Loyal
  * Potential
  * At Risk
  * Low Engagement

* Avaliação de desempenho por segmento

---

## 📊 Outputs gerados

Após execução da pipeline:

* `outputs/tables/`

  * métricas do teste A/B
  * resultados estatísticos
  * análise financeira
  * desempenho por segmento

* `outputs/charts/`

  * gráficos comparativos
  * visualizações de segmentos

---

## 📓 Notebook de análise

Para uma visão mais interpretativa e orientada a negócio:

```bash
jupyter notebook
```

Abra:

```
notebooks/analysis.ipynb
```

---

## 💡 Observação final

Este projeto foi estruturado seguindo boas práticas de engenharia de dados e analytics engineering, com foco em:

* reprodutibilidade
* modularização
* clareza analítica
* separação entre código e dados

