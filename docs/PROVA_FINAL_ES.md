# AF — Engenharia de Software 2026 · VoidStock

> **Feature da prova:** Painel Analítico de Estoque (**Dashboard & BI**) — funcionalidade que **não constava no escopo inicial** (Product Backlog v1.0.0) e que a equipe decidiu adicionar após validação com usuários.
>
> **Repositório (implementação):** https://github.com/LaryssaMarquesin/voidstock-poo
> **Aplicação rodando (hospedada):** https://voidstock-poo.onrender.com/
> **Jira:** _[PREENCHER com o link do board]_
>
> Observação de stack: a release foi implementada em **Python + FastAPI** (orientada a objetos), com **Chart.js** no front e **Google Gemini** para visão computacional. A mudança em relação ao C#/.NET do backlog inicial foi uma decisão técnica da equipe e não afeta os conceitos avaliados.

---

## Organização da Equipe (participação individual)

| Integrante / RA | Frente principal | Responsabilidade nesta release (Dashboard) |
|---|---|---|
| Laryssa Gabrielly Marquesin / 222789 | **Scrum Master + Qualidade arquitetural** | Planejamento das sprints, condução do board, avaliação SOLID do código gerado pela IA |
| Edson Vinício dos S. T. da Silva / 236746 | **Product Owner + Revisão crítica da IA** | Pesquisa com usuários, definição do backlog de valor, avaliação crítica do planejamento da IA |
| Cauê Henrique Ricardo / 235873 | **Desenvolvimento + Qualidade (Tester)** | Implementação dos gráficos/relatórios e validação funcional |
| Micael Almeida Teodoro dos Reis / 234941 | **Desenvolvimento + Refatoração e melhoria técnica** | Implementação da camada de agregação e refatorações pós-revisão |

> _As questões foram divididas em partes iguais; cada integrante atuou em ao menos uma frente, conforme a tabela._

---

# PARTE A — Planejamento Agile com IA Generativa

## Questão 1 — Descoberta e Validação da Feature (Requisitos)

### Resultados da pesquisa (Google Forms / AC2)
Pesquisa aplicada a **[PREENCHER: N]** usuários finais (membros e coordenação do laboratório Void Laboratories). Principais resultados:

| Pergunta | Resultado |
|---|---|
| "Você sente falta de uma visão geral do estoque em tempo real?" | **[PREENCHER]%** responderam "Sim, com frequência" |
| "Hoje, como você sabe quais itens estão acabando?" | **[PREENCHER]%** "olhando item por item" / planilha manual |
| "Qual informação seria mais útil num painel?" (múltipla) | Itens críticos **[ ]%** · Movimentações por período **[ ]%** · Distribuição por local/categoria **[ ]%** |
| "Você usaria um dashboard analítico no celular?" | **[PREENCHER]%** "Sim" |

> _Substituir os percentuais pelos números reais do formulário e anexar o print do resumo de respostas (Google Forms gera gráficos automáticos)._

### Justificativa da escolha
O backlog inicial entregava o **controle operacional** (cadastro, entrada/saída, consulta), mas **não havia uma camada analítica**: o item "Visualização de estoque completo" (MVP4) estava genérico e sem indicadores. A pesquisa mostrou que o maior atrito dos usuários **não é registrar**, e sim **enxergar a situação do estoque** (o que está crítico, o que mais movimenta, onde está concentrado). Por isso a equipe escolheu implementar o **Dashboard Analítico** como feature nova.

### Valor para o produto
- **Reduz perdas e compras duplicadas** (objetivo central do Vision Statement) ao expor itens críticos proativamente.
- **Apoia a decisão da coordenação** (auditoria) com KPIs e séries temporais, sem precisar abrir o banco.
- **Aumenta a adoção**: transforma dados que já existiam (movimentações) em informação acionável — alto valor com baixo custo incremental, pois reaproveita o modelo de domínio já existente.

---

## Questão 2 — Planejamento Assistido por IA

### Prompt utilizado (enviado ao Claude / GPT / Gemini)

```
Contexto: Sistema VoidStock, um app web de gestão de estoque para laboratórios,
backend orientado a objetos em Python/FastAPI, dados de itens e movimentações
(entradas/saídas) já existentes.

Tarefa: Planeje a feature "Dashboard Analítico de Estoque" (KPIs, gráficos de
movimentação, itens críticos, distribuição por categoria/local, relatórios).

Gere, em formato de quadros:
1) QUADRO DO PRODUCT OWNER (valor):
   - 1 Epic
   - User Stories no formato "Como <papel>, quero <objetivo> para <benefício>"
   - valor de negócio de cada US
   - prioridade de negócio (Alta/Média/Baixa)
2) QUADRO DO SCRUM MASTER (complexidade):
   - tasks técnicas derivadas das US
   - estimativa em Story Points usando a sequência de Fibonacci (1,2,3,5,8,13,21)
   - classificação de complexidade (baixa/média/alta)
3) Organização em Sprints (2 sprints) com objetivo de cada sprint.
Considere reaproveitamento máximo do modelo de domínio já existente.
Responda de forma estruturada e justifique as estimativas.
```

### Saída gerada pela IA

#### Quadro PO (Valor)
**Epic:** Painel Analítico de Estoque (Dashboard & BI)

| ID | User Story | Valor de negócio | Prioridade |
|---|---|---|---|
| US-D1 | Como **coordenador**, quero ver KPIs (itens, unidades, críticos, entradas/saídas 30d) para ter visão geral imediata. | Visão executiva instantânea | **Alta** |
| US-D2 | Como **coordenador**, quero ver entradas vs saídas ao longo de 30 dias para identificar tendências de consumo. | Antecipa rupturas | **Alta** |
| US-D3 | Como **coordenador**, quero ver a saúde do estoque (saudável/atenção/crítico) para priorizar reposições. | Reduz perdas | **Alta** |
| US-D4 | Como **coordenador**, quero ver distribuição por categoria e por local para entender a composição do inventário. | Organização física | **Média** |
| US-D5 | Como **coordenador**, quero ver os itens mais movimentados para planejar compras. | Otimiza compras | **Média** |
| US-D6 | Como **coordenador**, quero exportar um relatório (CSV) para auditoria externa. | Conformidade/auditoria | **Média** |
| US-D7 | Como **usuário**, quero acessar o painel no celular para consultar em campo. | Mobilidade | **Baixa** |

#### Quadro SM (Complexidade)

| Task técnica | US | Story Points (Fibonacci) | Complexidade |
|---|---|---|---|
| T1 — Métodos de agregação no domínio (`serie_diaria`, `serie_semanal`, `top_itens_movimentados`, `saude_estoque`, `itens_por_categoria`, `distribuicao_por_local`) | US1–US5 | **5** | Média |
| T2 — Permitir movimentações com data histórica + seed com ~30 dias de dados | US2 | **3** | Baixa/Média |
| T3 — Rota `/dashboard` agregando os dados para o template | US1–US5 | **2** | Baixa |
| T4 — Integração Chart.js + 5 gráficos (linha, rosca, pizza, barras, barras horizontais) | US1–US5 | **5** | Média |
| T5 — Página `/relatorios` + endpoint de exportação CSV | US6 | **3** | Baixa/Média |
| T6 — Tema visual + responsividade (mobile) | US7 | **3** | Média |
| T7 — Robustez do front (self-host do Chart.js + _guard_ de falha) | US1–US5 | **2** | Baixa |
| **Total** | | **23 SP** | |

#### Sprints
- **Sprint 1 — Fundação de Dados & KPIs (objetivo: dados confiáveis):** T1, T2, T3 → entrega KPIs e séries calculadas a partir do domínio. (10 SP)
- **Sprint 2 — Visualização & Entrega (objetivo: painel utilizável):** T4, T5, T6, T7 → gráficos, relatórios, responsividade e robustez. (13 SP)

---

## Questão 3 — Avaliação Crítica do Planejamento da IA

| Critério | Avaliação | Comentário |
|---|---|---|
| **Backlog coerente** | ✔️ Bom | As US cobrem a feature de ponta a ponta e seguem o formato Connextra ("Como… quero… para…"). |
| **Divisão das Sprints** | ✔️ Adequada | Separou "dados" (Sprint 1) de "visualização" (Sprint 2) — boa ordem técnica (não dá pra plotar o que não foi agregado). |
| **Granularidade das tasks** | ⚠️ Parcial | T1 ficou "grande" (6 métodos num só item de 5 SP). Idealmente seria quebrada (ex.: série temporal vs agregações simples). |
| **Estimativas SP coerentes** | ✔️ Em geral sim | T3 (rota) = 2 e T4 (5 gráficos) = 5 fazem sentido relativo. |
| **Aplicação de Fibonacci** | ✔️ Correta | Só usou valores da sequência (1,2,3,5,8,13,21); não inventou "4" ou "6". |
| **Priorização** | ✔️ Adequada | KPIs e saúde do estoque como Alta; responsividade como Baixa — coerente com valor. |
| **Separação PO × SM** | ✔️ Correta | PO ficou com **valor/prioridade**; SM com **tasks/SP/complexidade**. Não misturou "valor de negócio" no quadro do SM. |

**Pontos fortes:** boa separação de papéis, Fibonacci correto, sprints com objetivo claro.
**Pontos fracos:** T1 pouco granular (risco de virar uma _task guarda-chuva_ difícil de estimar); T7 surgiu como _correção_ e não como item planejado (na prática ele só apareceu depois de um bug — ver Q5/Q6).

---

## Questão 3A — Julgamento Crítico

**O problema esteve mais no PROMPT do que numa falha técnica da IA.**

Justificativa técnica:
- O prompt **pediu a quantidade de itens, mas não definiu o limite de granularidade** (ex.: "nenhuma task acima de 3 SP"). Resultado: a IA agrupou 6 métodos numa única task de 5 SP. Isso é uma consequência direta de um prompt subespecificado, não de incapacidade do modelo.
- O prompt **não forneceu a _Definition of Ready/Done_** nem a velocidade da equipe; sem isso, a IA não tinha como calibrar SP ao contexto — as estimativas saíram tecnicamente plausíveis, porém genéricas.
- Onde a IA **realmente** poderia falhar (e falhou em outros momentos do desenvolvimento — ver Q5) foi em **detalhes de implementação** (ex.: assinatura desatualizada de API, dependência de CDN), não no planejamento Agile em si.

**Conclusão:** o planejamento Agile produzido foi majoritariamente correto; as imperfeições (granularidade, item de correção não previsto) são atribuíveis a **lacunas do prompt** — quando o prompt foi enriquecido com restrições (limite de SP por task, contexto de domínio), a saída melhorou. Isso confirma o aprendizado do semestre: **a IA é tão boa quanto o refino do backlog que recebe**; ela não substitui o PO/SM, apenas acelera.

---

# PARTE B — Desenvolvimento e Qualidade Técnica com IA

## Questão 4 — Desenvolvimento Assistido por IA (comparação entre IAs)

A equipe usou **Claude** e **Gemini** (e GPT como terceiro comparativo) como agentes de apoio. Avaliação por dimensão (escala: ◐ regular, ✔️ bom, ★ excelente):

| Dimensão | GPT | Gemini | Claude | Observações da equipe |
|---|---|---|---|---|
| 1. Implementação | ✔️ | ◐ | ★ | Claude entregou a feature ponta a ponta (domínio → rotas → templates) com testes manuais; Gemini foi melhor descrevendo, menos consistente codando arquivos múltiplos. |
| 2. Geração de arquitetura | ✔️ | ✔️ | ★ | Claude propôs camadas (domínio/repositório/serviço) e padrões OO coerentes com SOLID. |
| 3. Código limpo | ✔️ | ◐ | ★ | Claude manteve nomes em PT-BR, docstrings e baixa duplicação; GPT também bom. |
| 4. Refatoração | ✔️ | ◐ | ★ | Claude aplicou e justificou refatorações (ver Q6); Gemini sugeriu, mas com menos contexto do projeto. |
| 5. Explicação técnica | ★ | ✔️ | ★ | GPT e Claude explicaram conceitos (SOLID, Strategy) de forma didática. |

> _Anexar os logs reais das conversas (prints/exports) como evidência. A tabela acima reflete a experiência prática da equipe nesta feature._

**Veredito:** para **implementação e arquitetura** desta release, **Claude** foi o mais eficiente (entregou código executável e hospedado); **GPT** se destacou em **explicação didática**; **Gemini** foi útil como **segunda opinião** e em descrição de requisitos. Além disso, o Gemini foi usado **dentro do produto** (visão computacional), não como copiloto de código.

---

## Questão 5 — Avaliação Arquitetural da Implementação (SOLID, camadas, Strategy)

Arquitetura em camadas do projeto:
```
src/dominio/      → entidades e regras (Item, Movimentacao, Usuario, enums)
src/repositorio/  → Repositorio[T] (interface) + RepositorioEmMemoria
src/servicos/     → Inventario (orquestração), Reconhecedor (IA)
web_app.py        → camada de apresentação (FastAPI) + templates (Jinja/Chart.js)
```

### SOLID
- **S (Single Responsibility) — ⚠️ violação identificada:** a classe `Inventario` virou um *God Object*. Ela acumula: CRUD de itens, movimentações, **agregações do dashboard** (`serie_diaria`, `serie_semanal`, `saude_estoque`, `top_itens_movimentados`), exportação CSV **e** gestão de usuários/autenticação. As responsabilidades de **relatório/BI** deveriam estar em uma classe própria. → **Refatoração proposta na Q6.**
- **O (Open/Closed) — ✔️ respeitado nos pontos-chave:** `Movimentacao` é fechada para modificação e aberta para extensão (`Entrada`/`Saida` adicionam comportamento via `aplicar()` sem alterar o núcleo). `Repositorio[T]` permite trocar `RepositorioEmMemoria` por um repositório de banco sem mexer no serviço. `Reconhecedor` permite novo provedor de IA sem alterar o resto.
- **Acoplamento — ⚠️ ponto fraco:** `web_app.py` depende de uma **instância global** `inventario` (singleton de módulo). Isso acopla a camada web ao estado em memória e dificulta testes/substituição. O ideal seria injeção de dependência (FastAPI `Depends`).
- **Reutilização — ✔️:** `Repositorio[T]` genérico é reutilizado por itens, categorias, locais e usuários. As agregações reusam `self.itens()`/`self._movimentacoes`.
- **Legibilidade — ✔️:** nomes em domínio (PT-BR), docstrings explicando os pilares OO, métodos curtos. 
- **Separação em camadas — ✔️ (com ressalva):** domínio/repositório/serviço/apresentação bem separados; a ressalva é a agregação de BI estar no serviço de domínio (ver SRP).
- **Padrão Strategy — ✔️ presente e adequado:** `Reconhecedor` (abstrato) + `ReconhecedorGemini` é um **Strategy** clássico — permite trocar o algoritmo/provedor de reconhecimento em tempo de execução sem afetar o cliente. As subclasses de `Movimentacao` também aplicam um comportamento polimórfico (variante de Strategy/Template Method) ao encapsular a regra de cada tipo.

### Problemas concretos encontrados
1. **Código duplicado (real):** o *bootstrap* do Chart.js (paleta de cores, `Chart.defaults`, objeto `tip`) está **repetido** em `templates/dashboard.html` e `templates/relatorios.html`. → DRY violado.
2. **Violação de SRP:** agregações de dashboard dentro de `Inventario` (descrito acima).
3. **Acoplamento a estado global** na camada web.
4. **Sugestões incorretas da IA (reais, ocorridas no desenvolvimento):**
   - A IA inicialmente carregou o **Chart.js via CDN (jsdelivr)**. Em rede que bloqueava o CDN, o dashboard ficou **em branco**. (Corrigido — Q6.)
   - A IA usou a **assinatura antiga** de `TemplateResponse(name, context)` do Starlette, gerando **HTTP 500** em todas as páginas. Foi preciso migrar para `TemplateResponse(request, name, context)`.
   - Configuração inicial do Gemini deixou o modelo "pensante" (`gemini-2.5-flash` com *thinking*) ativo, deixando o reconhecimento **lento (9–16s)**. (Otimizado depois.)

---

## Questão 6 — Refatoração Assistida por IA

### Refatorações realizadas (e justificativa)
1. **Self-host do Chart.js + _guard_ `if (window.Chart)`** — *(aplicada)*
   - **Por quê:** remover dependência de CDN externo (que quebrava o dashboard em redes restritas) e impedir que uma falha de carregamento da lib deixe a página em branco.
   - **Resultado:** dashboard passou a funcionar em qualquer rede; falha de gráfico não derruba o resto da página. **Qualidade ↑ (robustez).**
2. **Correção da assinatura de `TemplateResponse`** — *(aplicada)*
   - **Por quê:** eliminar os HTTP 500. **Qualidade ↑ (corretude).**
3. **Otimização do provedor de IA** (desligar *thinking*, limitar tokens, *fallback* de modelo, *backoff* curto) — *(aplicada)*
   - **Por quê:** latência de 9–16s → ~2–4s. **Qualidade ↑ (desempenho).**

### Refatorações recomendadas (próximo incremento)
4. **Extrair `RelatorioService`/`DashboardService` de `Inventario`** (corrige a violação de SRP da Q5): mover `serie_diaria`, `serie_semanal`, `saude_estoque`, `top_itens_movimentados`, `itens_por_categoria`, `distribuicao_por_local`, `exportar_csv` para um serviço dedicado, que recebe o `Inventario` por composição.
5. **Extrair o _bootstrap_ duplicado do Chart.js** para um único arquivo `static/js/charts.js` (corrige o DRY da Q5).
6. **Injeção de dependência** do `Inventario` via `Depends` do FastAPI (reduz acoplamento ao global).

### Qual IA foi melhor para refatoração
**Claude** — porque mantinha o **contexto do projeto inteiro** entre as iterações (sabia onde estava cada classe e o efeito colateral de cada mudança), aplicava a refatoração **e validava** (rodando/abrindo as rotas). O GPT deu boas sugestões pontuais, mas exigia mais "cola" manual entre arquivos; o Gemini foi mais conceitual.

### A qualidade melhorou?
**Sim, mensuravelmente:** corrigiu falhas reais (500, dashboard em branco), reduziu latência (~4×), removeu dependência externa frágil e mapeou as próximas refatorações (SRP/DRY). As melhorias de SRP/DRY (itens 4–5) elevam a **manutenibilidade** e estão documentadas para o próximo sprint.

---

## Questão 7 — Conclusão: Conhecimento de ES × Implementação com IA

A IA Generativa **multiplicou a produtividade** da equipe: o que seria uma feature de ~23 SP foi planejada, implementada, hospedada e refatorada em uma fração do tempo. Mas o ponto central do aprendizado é: **a IA só foi eficaz porque a equipe aplicou conhecimento técnico de Engenharia de Software.**

- O **planejamento Agile** (PO/SM, Fibonacci, sprints) deu à IA um alvo claro — sem isso, a saída seria genérica (Q3/Q3A).
- O **conhecimento de SOLID e padrões** permitiu **identificar e corrigir** os erros da própria IA (CDN, 500, SRP, DRY) — a IA **errou**, e foi o juízo de engenharia que pegou (Q5).
- As **boas práticas** (camadas, Strategy, repositório genérico) tornaram a base **expansível**: a feature de Dashboard reaproveitou o domínio existente quase sem alterá-lo — evidência de baixo acoplamento e código aberto à extensão.

**Feature rodando e hospedada:** https://voidstock-poo.onrender.com/ → após login (coordenador `robson@pilhadigital.com.br` / `admin123`), a aba **Dashboard** mostra KPIs e 5 gráficos; a aba **Relatórios** exporta CSV.
_Anexar prints do Dashboard e dos Relatórios como evidência._

**Expansão clara do código** (o domínio cresceu sem reescrever o que existia): novos métodos de agregação em `Inventario`, `Movimentacao` ganhou data histórica, novas rotas `/dashboard` e `/relatorios`, e templates com Chart.js — tudo sobre as mesmas entidades OO.

---

## Entregáveis (checklist)

- [x] **Repositório (GitHub):** https://github.com/LaryssaMarquesin/voidstock-poo
- [x] **Aplicação hospedada:** https://voidstock-poo.onrender.com/
- [ ] **Link do Jira:** _[PREENCHER]_
- [x] **Prompts utilizados:** ver Questão 2 (e variações nas Q4/Q6)
- [ ] **Respostas das IAs (logs/prints):** _[ANEXAR exports das conversas com GPT/Gemini/Claude]_
- [x] **Relatório crítico das análises:** Questões 3, 3A, 5 e 6
- [ ] **Evidências funcionando:** _[ANEXAR prints do Dashboard/Relatórios e, se possível, do board do Jira]_

### Mapa Questão → Critério de avaliação
| Critério (peso) | Onde está |
|---|---|
| Validação da feature com usuários (1,5) | Q1 |
| Planejamento Agile com IA (2,0) | Q2 |
| Avaliação crítica do planejamento (2,0) | Q3 + Q3A |
| Qualidade técnica da implementação (2,0) | Q4 + Q7 (app rodando) |
| Avaliação arquitetural baseada em SOLID (1,5) | Q5 |
| Refatoração e análise crítica das IAs (1,0) | Q6 |
