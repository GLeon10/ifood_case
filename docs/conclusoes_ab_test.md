## Visão geral do experimento

Este documento resume as principais conclusões da análise do teste A/B de cupom,
com números e referências aos gráficos gerados em `outputs/charts/`. Ele pode
ser usado como base para criação de um relatório em PDF (por exemplo, no Manus AI).

---

## 1. Contexto do teste A/B

O objetivo foi avaliar o impacto de uma campanha de cupom sobre:

- **Retenção / engajamento**: conversão e pedidos por usuário  
- **Receita**: GMV (Gross Merchandise Volume) total e por usuário  
- **Viabilidade financeira**: lucro líquido da campanha considerando custo do cupom e take rate do iFood  

O experimento foi estruturado em dois grupos:

- **Controle**: usuários sem exposição ao cupom  
- **Tratamento**: usuários com exposição ao cupom  

---

## 2. Resultados globais do teste A/B

### 2.1 Tamanho de grupo

- **Controle**: 360.528 usuários  
- **Tratamento**: 445.909 usuários  

### 2.2 Conversão e volume de pedidos

Na janela analisada, consideramos apenas usuários com pelo menos um pedido,
portanto a taxa de conversão aparece como 100% para ambos os grupos.

O impacto do cupom é observado principalmente em **frequência de pedidos** e
**gasto total**:

- **Pedidos por usuário**
  - Controle: **2,80** pedidos por usuário  
  - Tratamento: **3,18** pedidos por usuário  

- **GMV total**
  - Controle: **R$ 48.432.203,49**  
  - Tratamento: **R$ 67.729.986,45**  

- **GMV por usuário**
  - Controle: **R$ 134,34** por usuário  
  - Tratamento: **R$ 151,89** por usuário  

Ou seja, o grupo tratamento gera aproximadamente **R$ 17,55** a mais de GMV por
usuário em relação ao controle.

### 2.3 Ticket médio (Average Order Value)

- Controle: **R$ 47,92** por pedido  
- Tratamento: **R$ 47,81** por pedido  

O ticket médio é praticamente igual entre os grupos, indicando que o cupom
atua principalmente aumentando **quantidade de pedidos**, não o valor médio
de cada pedido.

### 2.4 Gráficos relevantes

- **Comparação de taxa de conversão**  
  Arquivo: `outputs/charts/conversion_rate_comparison.png`

- **Comparação de GMV por usuário**  
  Arquivo: `outputs/charts/gmv_per_user_comparison.png`

- **Distribuição do valor de pedido (ticket)**  
  Arquivo: `outputs/charts/order_value_distribution.png`

Esses gráficos ajudam a visualizar que:

- A conversão (na definição usada) é igual entre os grupos.  
- O GMV por usuário é maior no tratamento.  
- A distribuição de ticket médio é muito semelhante entre controle e tratamento.

---

## 3. Testes estatísticos

### 3.1 Teste t de Welch – valor do pedido

- **p-valor**: 0,4732  
- **Intervalo de confiança 95% para a diferença de ticket médio
  (tratamento – controle)**: de **–0,40** a **+0,19** reais  
- **Conclusão**: não há evidência estatística de que o ticket médio por pedido
  seja diferente entre os grupos.

### 3.2 Teste de proporções – conversão

Como a amostra considera apenas usuários com pelo menos um pedido, a taxa de
conversão é **100% em ambos os grupos**, e o teste de proporções indica **ausência
de diferença significativa** na conversão sob essa definição.

### 3.3 Síntese estatística

- O cupom **não altera significativamente** o ticket médio nem a conversão.  
- O benefício da campanha aparece como **aumento de frequência de pedidos e de
  GMV por usuário**, e não como aumento de ticket médio.

---

## 4. Análise financeira da campanha

### 4.1 Premissas

- **Valor do cupom por usuário elegível**: R$ 10,00  
- **Take rate do iFood (comissão sobre GMV)**: 15%  

### 4.2 GMV e receita incremental

- **GMV incremental total (tratamento vs controle)**:  
  **R$ 7.827.966,56**

- **Receita incremental do iFood**  
  Receita incremental = GMV incremental × take rate  
  ≈ **R$ 1.174.194,98**

### 4.3 Custo da campanha de cupons

- **Número de usuários no grupo tratamento**: 445.909  
- **Custo total de cupons** = 445.909 × R$ 10,00  
  ≈ **R$ 4.459.090,00**

### 4.4 Lucro líquido da campanha

- **Lucro líquido** = Receita incremental – Custo de cupons  
- **Lucro líquido** ≈ **R$ –3.284.895,02**  

### 4.5 Conclusão financeira

Apesar de gerar **GMV incremental relevante**, a campanha de cupom é
**financeiramente inviável nas condições atuais** (R$ 10 de cupom e 15% de
take rate), produzindo um **prejuízo estimado de aproximadamente R$ 3,3M**
para o iFood.

---

## 5. Segmentação RFM e resposta por segmento

Os clientes foram agrupados em cinco segmentos via RFM:

- Champions  
- Loyal  
- Potential  
- At Risk  
- Low Engagement  

O arquivo `outputs/tables/segment_metrics.csv` consolida as principais métricas
por segmento. Abaixo, os destaques por grupo.

### 5.1 Champions

- **Controle**
  - Usuários: 70.931  
  - Pedidos por usuário: 7,42  
  - GMV por usuário: R$ 365,97  
- **Tratamento**
  - Usuários: 105.524  
  - Pedidos por usuário: 7,44  
  - GMV por usuário: R$ 367,56  

**Uplift de GMV por usuário**: ~**R$ 1,58**  

Champions já são altamente engajados; o cupom gera **ganho marginal pequeno**
em GMV por usuário.

### 5.2 Loyal

- **Controle**
  - Usuários: 73.757  
  - Pedidos por usuário: 2,77  
  - GMV por usuário: R$ 124,98  
- **Tratamento**
  - Usuários: 104.914  
  - Pedidos por usuário: 2,86  
  - GMV por usuário: R$ 127,27  

**Uplift de GMV por usuário**: ~**R$ 2,29**  

Clientes Loyal respondem bem ao cupom, com **aumento relevante de GMV e
engajamento**.

### 5.3 At Risk

- **Controle**
  - Usuários: 54.874  
  - Pedidos por usuário: 2,17  
  - GMV por usuário: R$ 101,56  
- **Tratamento**
  - Usuários: 73.862  
  - Pedidos por usuário: 2,30  
  - GMV por usuário: R$ 106,49  

**Uplift de GMV por usuário**: ~**R$ 4,94**  

Este é o segmento com **maior ganho de GMV por usuário**, sugerindo que o
cupom é especialmente eficaz para clientes em risco de churn.

### 5.4 Potential

- **Controle**
  - Usuários: 15.927  
  - Pedidos por usuário: 1,00  
  - GMV por usuário: R$ 90,44  
- **Tratamento**
  - Usuários: 16.082  
  - Pedidos por usuário: 1,00  
  - GMV por usuário: R$ 91,21  

**Uplift de GMV por usuário**: ~**R$ 0,77**  

Há ganho, mas relativamente modesto; o cupom tem efeito limitado nesse grupo.

### 5.5 Low Engagement

- **Controle**
  - Usuários: 145.039  
  - Pedidos por usuário: 1,00  
  - GMV por usuário: R$ 43,04  
- **Tratamento**
  - Usuários: 145.527  
  - Pedidos por usuário: 1,00  
  - GMV por usuário: R$ 43,01  

**Uplift de GMV por usuário**: aproximadamente **zero** (ligeiramente negativo).  

Clientes de baixo engajamento **não respondem de forma significativa ao cupom**,
o que indica baixa eficiência de investimento neste segmento.

### 5.6 Gráficos de segmentos

- **Uplift de GMV por usuário por segmento**  
  Arquivo: `outputs/charts/uplift_by_segment.png`

- **Distribuição de recência, frequência e monetary (RFM)**  
  Arquivo: `outputs/charts/rfm_distribution.png`

Esses gráficos ilustram:

- Quais segmentos geram maior diferença de GMV por usuário entre tratamento e controle.  
- Como os clientes se distribuem em termos de recência, frequência e valor monetário.

---

## 6. Conclusões de negócio e recomendações

1. **Efeito do cupom no comportamento de compra**
   - A campanha aumenta **pedidos por usuário** e **GMV por usuário**, mas não altera
     significativamente o ticket médio nem a conversão (na definição usada).

2. **Viabilidade econômica**
   - Com cupom de **R$ 10** e take rate de **15%**, a campanha gera **prejuízo
     líquido estimado em ~R$ 3,3M**, mesmo com GMV incremental relevante.

3. **Segmentos com melhor resposta**
   - **At Risk** e **Loyal** apresentam os maiores uplifts de GMV por usuário,
     sendo candidatos naturais para **campanhas segmentadas**.  
   - **Champions** já consomem muito; o ganho marginal é pequeno.  
   - **Low Engagement** praticamente não reage ao cupom, sugerindo pouca efetividade.

4. **Próximos passos recomendados**
   - Redesenhar a mecânica do cupom (valor, número de usos, restrições) visando
     **ROAS positivo**.  
   - Focar campanhas em segmentos com **maior uplift (At Risk, Loyal)** em vez
     de ações amplas e não segmentadas.  
   - Rodar novos testes A/B variando **valor do cupom**, **regras de elegibilidade**
     por segmento RFM e **janelas de medição** que incluam também não convertidos.

