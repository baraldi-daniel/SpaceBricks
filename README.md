# SpaceBricks

> **⚠️ Projeto pessoal e não oficial.** Este é um jogo de fã, feito por diversão e para demonstração, sem fins comerciais. **Não é um produto da Databricks e não é afiliado, patrocinado nem endossado pela Databricks.**
>
> Databricks, o logo da Databricks e os nomes de produtos citados (Lakebase, Lakehouse//RT, Unity Catalog, Delta, MLflow, Spark, Genie, Genie Ontology, Omnigent, OpenSharing, AI Gateway, Lakeflow Designer, Spark Declarative Pipelines, CustomerLake, Lakewatch, Databricks Apps, AI/BI, `ai_parse_document`, entre outros) são marcas de seus respectivos donos e aparecem aqui só como referência temática. Os ícones do jogo são desenhos próprios feitos em código, inspirados nesses produtos; nenhum arquivo de imagem oficial é distribuído neste repositório.
>
> A música e os efeitos sonoros são originais, gerados em código (WebAudio). Se algum detentor de marca preferir que algo seja removido, basta abrir uma issue.

Jogo de nave arcade com tema de dados e IA, feito por fã para estandes e eventos. Os jogadores pilotam uma nave e destroem problemas reais de data engineering e IA, enquanto uma rede neural aprende seu estilo de jogo em tempo real.

## O que é

- **Jogo arcade de nave** (shoot 'em up) com temática Databricks
- **IA adaptativa** com rede neural (MLP) que aprende o padrão de movimento do jogador durante a partida
- **Narrador IA** usando Claude Sonnet via Foundation Model API - gera frases contextuais baseadas no comportamento do jogador
- **Ranking ao vivo** armazenado no Lakebase (PostgreSQL gerenciado)
- **Captura de leads**: nome, email, empresa e telefone obrigatórios para jogar
- **Especiais temáticos**: Spark, Delta, Unity Catalog e MLflow com efeitos únicos

## Fluxo do estande

```
Home (ranking + galeria) → Cadastro → Jogo → Brinde
                                              ↓
                                    Caso real? → Brinde Premium
```

1. Visitante vê o ranking e a galeria de inimigos/poderes
2. Preenche cadastro (nome, email, empresa, telefone)
3. Joga contra a IA que aprende em tempo real
4. Ao perder, ganha um **brinde**
5. Opcionalmente descreve um caso real de dados/IA e ganha um **brinde premium**

## Níveis de dificuldade

Escolhidos na tela de cadastro ou no **☰ MENU** durante a partida (a escolha fica salva no navegador):

| Nível | Vidas | Vida dos inimigos | Seu tiro | Tiros inimigos | Mira da IA | Pontos |
|-------|-------|-------------------|----------|----------------|------------|--------|
| ★ Muito fácil | 5 | morrem com 1 tiro (chefões 30%) | muito rápido | máx. 5 na tela | erra muito | x0.5 |
| ★★ Fácil | 4 | 50% | rápido | máx. 9 | erra bastante | x0.75 |
| ★★★ Normal | 3 | 70% | médio | máx. 14 | média | x1 |
| ★★★★ Difícil | 3 | 100% | normal | máx. 22 | precisa | x1.5 |
| ★★★★★ Insano | 2 | 120% | normal | máx. 32 | muito precisa | x2 |

Os inimigos se movem em **formação**: a IA desloca o bloco inteiro na direção prevista do jogador, sem amontoar os inimigos num canto.

## Modo evento x só jogar

Na tela de cadastro há o checkbox **Modo evento** (marcado por padrão; a escolha fica salva no navegador):

- **Marcado**: cadastro completo (nome, e-mail, empresa, telefone), casos de uso reais e brindes, para estandes.
- **Desmarcado**: só um apelido (opcional) e jogar. Nenhuma menção a casos de uso ou brindes.

## Menu durante a partida

Clique em **☰ MENU** no placar (ou aperte **ESC**): continuar, trocar a dificuldade, **reiniciar** do zero ou sair.

## Inimigos (problemas sem Databricks)

| Inimigo | Descrição |
|---------|-----------|
| Data Silo | Dados isolados entre departamentos |
| Sem Guardrails | IA sem limites de segurança |
| Vendor Lock-in | Preso em formatos proprietários |
| Lentidão Crônica | Queries de horas, zero performance |
| Sem Federation | Impossível consultar entre fontes |
| Alucinação IA | Modelos inventando respostas |

## Chefões e mega chefões

| Wave | Chefão | Poder |
|------|--------|-------|
| 5 | Data Swamp | Spawna mini-inimigos |
| 10 | Shadow IT | Teleporta pela tela |
| **12** | **MEGA: Shadow AI** | Cria 2 clones que o curam e embaralham; prompt injection inverte seus controles. Lakewatch/Genie Ontology revelam o verdadeiro |
| 15 | Pipeline Hell | Rajada de 5 tiros |
| **18** | **MEGA: Data Breach** | Blindado por 4 placas (quebre-as primeiro), rouba seus especiais e solta drones de vazamento |
| 20 | Dados Brutos | Joga "lixo" na tela |
| **24** | **MEGA: Cloud Bill** | Cresce, se regenera e se divide em dois na metade da vida; o AI Gateway corta o budget (regeneração) |
| 25 | Total Lock-in | Reduz velocidade da nave |

Depois da wave 25 os chefões voltam em ciclo, cada vez mais fortes.

## Poderes especiais (teclas)

| Tecla | Poder | Efeito | Forte contra |
|-------|-------|--------|-------------|
| S | Spark | Barreira de mísseis pela tela toda | Lentidão Crônica |
| D | Delta | Caixa que agrupa e destrói inimigos | Data Silo, Vendor Lock-in |
| U | Unity Catalog | Escudo por 5 segundos que dispara rajadas de tiros radiais | Sem Federation, Data Silo |
| M | MLflow | Míssil autônomo que caça inimigos por 6s | Sem Guardrails, Alucinação IA |

### Power-ups de tiro

De vez em quando cai uma cápsula do alto da tela (a cada 15–25 s, ou raramente ao destruir um inimigo). Encoste a nave para pegar. Dura 15 s; uma nova substitui a atual.

| Power-up | Tiro |
|----------|------|
| **Lakebase** | Tiro duplo rapidíssimo (transações em alta velocidade) |
| **CustomerLake** | Leque de 5 tiros: atinge todos os segmentos |
| **Lakewatch** | Tiro teleguiado que persegue as ameaças (dano 2) |
| **Databricks Apps** | Bloco pesado que atravessa até 6 inimigos (dano 3) |
| **Lakehouse//RT** | Raio instantâneo (latência zero): acerta na hora o 1º inimigo da coluna |

### Super cápsulas (raras, douradas)

Cai uma a cada 25–35 s (a primeira aos ~20 s) e **todo chefão derrotado solta uma**. Elas saem de um "saco embaralhado": nenhuma repete antes de todas terem aparecido. Duram 12 s; cada uma faz algo que só ela permite:

| Super cápsula | Efeito |
|---------------|--------|
| **Omnigent** | Esquadrão de 4 agentes (estrelas-do-mar) ao seu lado, cada um disparando um tiro diferente ao mesmo tempo |
| **AI Gateway** | Barreira de governança: bloqueia e **devolve** os tiros inimigos + rate limit (429) nos inimigos |
| **Genie Ontology** | Cada inimigo atingido **vira aliado** e passa a atirar nos outros |
| **Lakeflow Designer** | Os blocos voam e montam **3 bunkers** que absorvem os tiros inimigos (os seus passam). Ficam até serem destruídos |
| **Spark Declarative Pipelines** | **Piloto automático** por 10 s: você "declara o resultado" e a nave desvia e mira sozinha |
| **ai_parse_document** | Organiza o caos em **tabelas**: inimigos e tiros inimigos vão para células (colunas A, B, C…) e ficam congelados por 8 s. Acertar um inimigo dá **dano na coluna inteira** e, no fim, os tiros parseados são devolvidos contra os inimigos |
| **OpenSharing** | Nave **espelhada em outra nuvem** por 12 s: copia seus movimentos (espelhados) e seus tiros. É um backup: se a cópia for atingida ela some sem você perder vida; se você for atingido, a cópia assume (failover) e você também não perde vida |

### Vida extra: AI/BI Dashboard

De vez em quando (no máximo a cada ~40 s, só depois que você perdeu alguma vida) cai a cápsula verde **AI/BI Dashboard**: encoste para ganhar **+1 vida** (máximo 9).

### Super especial: GENIE ✦

A barra **GENIE** (canto inferior esquerdo, com a lâmpada) enche conforme você destrói inimigos (~50 inimigos). Quando ficar cheia, aperte **ESPAÇO** (no celular, o botão ✦).

O Genie sai da lâmpada e vira um **agente autônomo** por 15 segundos, flutuando devagar pela tela:
- trava a mira em até 4 inimigos ao mesmo tempo (retículas **LOCK**)
- dispara laser teleguiado (30 tiros/s) e salvas de 8 micro-mísseis
- derruba automaticamente os tiros inimigos que chegam perto de você (+3 s de escudo no lançamento)
- persegue os inimigos pelas waves seguintes e depois volta para a sua nave

Os especiais são coletados matando inimigos (10 kills = 1 especial aleatório, máx 3 de cada).

## IA do jogo

### Rede Neural (in-game)
- MLP com backpropagation: 6 inputs → 8 hidden (leaky ReLU) → 1 output
- Inputs: posição, velocidade, aceleração do jogador + features quadráticas
- Treina online via SGD a cada 3 frames
- Começa competente (heurística base) e melhora visivelmente durante a partida
- Reseta a cada novo jogador

### Narrador IA (entre waves)
- Claude Sonnet 4.6 via Foundation Model API
- Gera frases contextuais baseadas no wave, score, vidas e bias de posição do jogador
- Fallback local se a API não estiver disponível

## Easter eggs

- **Lakehouse Code**: digitar `genie` durante a partida, todos os especiais x2 + barra do GENIE cheia (1 uso por partida)
- **Digitar "lakehouse"**: +3 vidas (1 uso por partida)

## Deploy

### Opção 1: apontar o Databricks Apps para este repositório (sem CLI)

1. No workspace: **Compute → Apps → Create app → Custom app**.
2. Em **Configure Git repository**, informe a URL deste repositório (provider GitHub) e o branch `main`. Repositório privado precisa de uma credencial Git no app.
3. **Deploy → From Git**.

Pronto, o jogo já funciona. Sem Lakebase, o ranking e os cadastros ficam num **banco local temporário**, que **some quando o app reinicia**. Para guardar de vez:

4. Crie um projeto **Lakebase** chamado `spacebricks`.
5. No app: **Edit → App resources → Add resource → Database (Lakebase)**, escolha o projeto `spacebricks`, branch `production`, database `databricks_postgres`, permissão **Can connect and create**. Depois faça o deploy de novo.
6. (Opcional) Para o narrador com IA: **Add resource → Serving endpoint** `databricks-claude-sonnet-4-6`, permissão **Can query**. Sem isso o narrador usa frases prontas.

O app cria o schema `spacebricks` e as tabelas sozinho. Confira em `<URL do app>/api/debug`: `"mode": "lakebase"` (permanente) ou `"mode": "local"` (temporário).

### Opção 2: bundle (2 comandos, cria tudo automaticamente)

Pré-requisitos: [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) >= 0.270 e um workspace com **Databricks Apps** e **Lakebase** habilitados.

```bash
git clone <este-repo> && cd spacebricks
databricks auth login --host https://<seu-workspace>.cloud.databricks.com --profile meu-ws   # só na 1ª vez

databricks bundle deploy --profile meu-ws          # cria Lakebase + App e sobe o código
databricks bundle run spacebricks --profile meu-ws    # inicia o app e mostra a URL
```

Pronto. O bundle (`databricks.yml`) cria tudo sozinho:

- **Projeto Lakebase** `spacebricks` (Postgres 17)
- **Databricks App** `spacebricks`, já com acesso ao banco (`CAN_CONNECT_AND_CREATE`) e ao LLM do narrador (`CAN_QUERY`)
- Permissão `CAN_USE` para o grupo `users`
- O schema `spacebricks` e as tabelas `players` / `scores` são criados automaticamente quando o app sobe

Para atualizar depois de mudar o código: rode os mesmos dois comandos de novo.

Para remover tudo: `databricks bundle destroy --profile meu-ws`

### Personalizar (opcional)

```bash
databricks bundle deploy --profile meu-ws \
  --var app_name=spacebricks-evento-sp \
  --var llm_endpoint=databricks-claude-sonnet-4-5
```

| Variável | Default | Descrição |
|----------|---------|-----------|
| `app_name` | `spacebricks` | Nome do app (minúsculas/hífen, máx. 30) |
| `lakebase_project` | `spacebricks` | Projeto Lakebase criado pelo bundle (se mudar, mude também `LAKEBASE_PROJECT` no `app.yaml`) |
| `llm_endpoint` | `databricks-claude-sonnet-4-6` | Endpoint de LLM do narrador (sem ele o jogo usa frases prontas) |

Teste rápido depois do deploy: abra `<URL do app>/api/debug`, que deve mostrar `"mode": "lakebase"` e `"status": "connected to Lakebase!"`.

## Som

- Música chiptune original (menu, jogo e chefão) e efeitos sonoros, tudo gerado em WebAudio (sem arquivos de áudio)
- Botões **MUSICA** e **EFEITOS** no canto da tela ligam/desligam cada um; a escolha fica salva no navegador
- A música começa no primeiro clique/tecla (política de autoplay dos navegadores)

## Estrutura

```
spacebricks/
├── LICENSE               # MIT (só o código; não cobre marcas)
├── databricks.yml        # Bundle: Lakebase + App + permissões (deploy em 1 comando)
├── app.yaml              # Comando e variáveis de ambiente do App
├── requirements.txt      # Dependências Python
├── README.md             # Este arquivo
├── backend/
│   ├── __init__.py
│   └── main.py           # API FastAPI + Lakebase + Foundation Models
└── frontend/
    └── index.html        # Jogo completo (HTML5 Canvas + JS + WebAudio)
```

## Stack técnica

- **Frontend**: HTML5 Canvas, JavaScript puro, CSS
- **Backend**: FastAPI + Uvicorn
- **Banco**: Lakebase Autoscaling (PostgreSQL gerenciado)
- **IA in-game**: Rede Neural MLP (JavaScript, client-side)
- **IA narrador**: Claude Sonnet 4.6 via Foundation Model API
- **Deploy**: Databricks Apps

## Controles

| Tecla | Ação |
|-------|------|
| ← → ou A/D | Mover nave |
| ↑ | Atirar |
| S/D/U/M | Usar especial |
| ESPAÇO | Super especial GENIE (barra cheia) |
| ESC ou ☰ MENU | Menu: continuar, dificuldade, reiniciar, sair |
| Botões MUSICA / EFEITOS | Liga/desliga música e efeitos |

## Licença

O código está sob a licença MIT (veja [`LICENSE`](LICENSE)). A licença cobre só o código: **não** concede direitos sobre nomes, logos ou marcas da Databricks ou de terceiros.
