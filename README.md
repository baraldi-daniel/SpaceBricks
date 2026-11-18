# SpaceBricks

> **⚠️ Unofficial personal project.** This is a fan-made game, built for fun and for demos, with no commercial purpose. **It is not a Databricks product and is not affiliated with, sponsored by, or endorsed by Databricks.**
>
> Databricks, the Databricks logo and the product names referenced here (Lakebase, Lakehouse//RT, Unity Catalog, Delta, MLflow, Spark, Genie, Genie Ontology, Omnigent, OpenSharing, AI Gateway, Lakeflow Designer, Spark Declarative Pipelines, CustomerLake, Lakewatch, Databricks Apps, AI/BI, `ai_parse_document`, among others) are trademarks of their respective owners and appear only as a thematic reference. The in-game icons are original drawings made in code, inspired by those products; no official image files are distributed in this repository.
>
> The music and sound effects are original and generated in code (WebAudio). If any trademark owner would prefer something to be removed, just open an issue.

An arcade space shooter with a data & AI theme, made by a fan for booths and events. Players fly a ship and destroy real data engineering and AI problems, while a neural network learns their play style in real time.

> The game UI is in **Brazilian Portuguese**. In-game labels are quoted below as they appear on screen.

## What it is

- **Arcade space shooter** (shoot 'em up) with a data & AI theme
- **Adaptive AI**: a neural network (MLP) learns the player's movement pattern during the match
- **AI narrator** using Claude Sonnet via the Foundation Model API, generating contextual one-liners based on how the player is doing
- **Live leaderboard** stored in Lakebase (managed PostgreSQL)
- **Event mode** (optional): lead capture (name, e-mail, company, phone), real use cases and giveaways
- **Themed specials, power-ups, super capsules and mega bosses** (see below)

## Booth flow (event mode)

```
Home (leaderboard + gallery) → Sign-up → Game → Giveaway
                                                  ↓
                                        Real use case? → Premium giveaway
```

1. The visitor sees the leaderboard and the gallery of enemies and powers
2. Fills in the sign-up form (name, e-mail, company, phone)
3. Plays against the AI that learns in real time
4. When the game is over, wins a **giveaway**
5. Optionally describes a real data/AI use case and wins a **premium giveaway**

## Event mode vs. just play

The sign-up screen has a **"Modo evento"** (event mode) checkbox, checked by default. The choice is saved in the browser:

- **Checked**: full sign-up (name, e-mail, company, phone), real use cases and giveaways. Meant for booths.
- **Unchecked**: just an (optional) nickname and play. No mention of use cases or giveaways anywhere.

## Difficulty levels

Chosen on the sign-up screen or in the **☰ MENU** during the match (saved in the browser):

| Level | Lives | Enemy HP | Your fire rate | Enemy bullets | AI aim | Score |
|-------|-------|----------|----------------|---------------|--------|-------|
| ★ Muito fácil (very easy) | 5 | die in 1 hit (bosses 30%) | very fast | max. 5 on screen | misses a lot | x0.5 |
| ★★ Fácil (easy) | 4 | 50% | fast | max. 9 | misses often | x0.75 |
| ★★★ Normal | 3 | 70% | medium | max. 14 | average | x1 |
| ★★★★ Difícil (hard) | 3 | 100% | normal | max. 22 | accurate | x1.5 |
| ★★★★★ Insano (insane) | 2 | 120% | normal | max. 32 | very accurate | x2 |

Enemies move in **formation**: the AI shifts the whole block toward where it predicts the player will be, without piling enemies up in a corner.

## In-game menu

Click **☰ MENU** on the scoreboard (or press **ESC**) to resume, change the difficulty, **restart** from scratch, or quit.

## Enemies (problems without Databricks)

| Enemy (on screen) | Description |
|-------------------|-------------|
| Data Silo | Data isolated between departments |
| Sem Guardrails (no guardrails) | AI with no safety limits |
| Vendor Lock-in | Stuck in proprietary formats |
| Lentidão Crônica (chronic slowness) | Hours-long queries, zero performance |
| Sem Federation (no federation) | Impossible to query across sources |
| Alucinação IA (AI hallucination) | Models making up answers |

## Bosses and mega bosses

| Wave | Boss | Power |
|------|------|-------|
| 5 | Data Swamp | Spawns mini enemies |
| 10 | Shadow IT | Teleports around the screen |
| **12** | **MEGA: Shadow AI** | Creates 2 clones that heal it and shuffle positions; prompt injection inverts your controls. Lakewatch / Genie Ontology reveal the real one |
| 15 | Pipeline Hell | 5-bullet burst |
| **18** | **MEGA: Data Breach** | Shielded by 4 armor plates (break them first), steals your specials and releases leak drones that chase you |
| 20 | Dados Brutos (raw data) | Throws "garbage" on screen |
| **24** | **MEGA: Cloud Bill** | Grows, regenerates and splits in two at half health; AI Gateway cuts its budget (regeneration) |
| 25 | Total Lock-in | Slows your ship down |

After wave 25 the bosses keep coming back in a cycle, stronger each time.

## Special powers (keys)

| Key | Power | Effect | Strong against |
|-----|-------|--------|----------------|
| S | Spark | Barrage of missiles across the whole screen | Lentidão Crônica |
| D | Delta | Box that groups enemies and destroys them | Data Silo, Vendor Lock-in |
| U | Unity Catalog | 5-second shield that fires bursts of radial shots | Sem Federation, Data Silo |
| M | MLflow | Autonomous missile that hunts enemies for 6 s | Sem Guardrails, Alucinação IA |

Specials are earned by destroying enemies (16 kills = 1 random special, max. 3 of each).

### Weapon power-ups

Every now and then a capsule falls from the top of the screen (every 15–25 s, or rarely when an enemy is destroyed). Touch it with your ship to pick it up. It lasts 15 s; a new one replaces the current one.

| Power-up | Shot |
|----------|------|
| **Lakebase** | Super-fast double shot (high-speed transactions) |
| **CustomerLake** | 5-shot fan: hits every segment |
| **Lakewatch** | Homing shot that hunts threats (damage 2) |
| **Databricks Apps** | Heavy block that pierces up to 6 enemies (damage 3) |
| **Lakehouse//RT** | Instant beam (zero latency): immediately hits the first enemy in the column |

### Super capsules (rare, golden)

One falls every 25–35 s (the first one at ~20 s), and **every defeated boss drops one**. They come out of a "shuffled bag": none repeats before all of them have appeared. Each one does something only it can do:

| Super capsule | Effect |
|---------------|--------|
| **Omnigent** | Squad of 4 agents (starfish) beside you, each firing a different weapon at the same time |
| **AI Gateway** | Governance barrier: blocks and **reflects** enemy bullets + rate limit (429) on enemies |
| **Genie Ontology** | Every enemy you hit **becomes an ally** and starts shooting the others |
| **Lakeflow Designer** | Blocks fly into place and build **3 bunkers** that absorb enemy bullets (yours go through). They stay until destroyed |
| **Spark Declarative Pipelines** | **Autopilot** for 10 s: you "declare the outcome" and the ship dodges and aims by itself |
| **ai_parse_document** | Organizes the chaos into **tables**: enemies and enemy bullets move into cells (columns A, B, C…) and freeze for 8 s. Hitting an enemy deals **damage to the whole column**, and at the end the parsed bullets are fired back at the enemies |
| **OpenSharing** | A ship **mirrored in another cloud** for 12 s: it copies your (mirrored) moves and your shots. It's a backup: if the copy is hit it disappears and you lose no life; if you are hit, the copy takes over (failover) and you don't lose a life either |

### Extra life: AI/BI Dashboard

Every now and then (at most every ~40 s, and only after you have lost a life) the green **AI/BI Dashboard** capsule falls: touch it to get **+1 life** (max. 9).

### Super special: GENIE ✦

The **GENIE** bar (bottom-left corner, with the lamp) fills up as you destroy enemies (~50 enemies). When it is full, press **SPACE** (on mobile, the ✦ button).

The Genie leaves the lamp and becomes an **autonomous agent** for 15 seconds, slowly floating across the screen:
- locks on up to 4 enemies at once (**LOCK** reticles)
- fires homing lasers (30 shots/s) and salvos of 8 micro-missiles
- automatically shoots down enemy bullets that get close to you (+3 s shield on launch)
- chases enemies into the next waves and then returns to your ship

## Game AI

### Neural network (in-game)
- MLP with backpropagation: 6 inputs → 8 hidden (leaky ReLU) → 1 output
- Inputs: player position, velocity, acceleration + quadratic features
- Trains online via SGD every 3 frames
- Starts competent (base heuristic) and visibly improves during the match
- Resets for every new player

### AI narrator (between waves)
- Claude Sonnet 4.6 via the Foundation Model API
- Generates contextual lines based on the wave, score, lives and the player's position bias
- Local fallback lines if the API is not available

## Easter eggs

- **Lakehouse Code**: type `genie` during the match → all specials x2 + GENIE bar full (once per match)
- Type **`lakehouse`**: +3 lives (once per match)

## Deploy

### Option 1: point Databricks Apps to this repository (no CLI)

1. In the workspace: **Compute → Apps → Create app → Custom app**.
2. In **Configure Git repository**, enter this repository's URL (provider GitHub) and the `main` branch. A private repository needs a Git credential on the app.
3. **Deploy → From Git**.

That's it, the game already works. If no Lakebase is configured, the app owner sees a warning on the home screen and the leaderboard / sign-ups are stored in a **temporary local database** that is **lost when the app restarts**. To make it persistent, either:

- open **⚙ CONFIG** on the home screen (see below) and pick an existing Lakebase or **create a new one** right there; or
- add the resources on the app page: **Edit → App resources → Add resource → Database (Lakebase)** with permission **Can connect and create** (resource key `lakebase`), and optionally a **Serving endpoint** such as `databricks-claude-sonnet-4-6` with permission **Can query** (resource key `llm`). Then redeploy. The app detects them automatically.

Check `<app URL>/api/debug`: `"mode": "lakebase"` (persistent) or `"mode": "local"` (temporary).

### Option 2: bundle (2 commands, creates everything automatically)

Prerequisites: [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html) >= 0.270 and a workspace with **Databricks Apps** and **Lakebase** enabled.

```bash
git clone <this-repo> && cd spacebricks
databricks auth login --host https://<your-workspace>.cloud.databricks.com --profile my-ws   # first time only

databricks bundle deploy --profile my-ws             # creates Lakebase + App and uploads the code
databricks bundle run spacebricks --profile my-ws    # starts the app and prints the URL
```

The bundle (`databricks.yml`) creates everything:

- **Lakebase project** `spacebricks` (Postgres 17)
- **Databricks App** `spacebricks`, already with access to the database (`CAN_CONNECT_AND_CREATE`) and to the narrator LLM (`CAN_QUERY`)
- `CAN_USE` permission for the `users` group
- The app creates its own schema (named after the app, e.g. `spacebricks`) and the `players` / `scores` tables on startup

To update after changing the code, run the same two commands again.

To remove everything: `databricks bundle destroy --profile my-ws`

#### Customize (optional)

```bash
databricks bundle deploy --profile my-ws \
  --var app_name=spacebricks-event \
  --var llm_endpoint=databricks-claude-sonnet-4-5
```

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | `spacebricks` | App name (lowercase letters, digits and hyphens; max. 30) |
| `lakebase_project` | `spacebricks` | Lakebase project created by the bundle (passed to the app through the `lakebase` resource) |
| `llm_endpoint` | `databricks-claude-sonnet-4-6` | Narrator LLM endpoint (without it the game uses canned lines) |

Quick check after deploying: open `<app URL>/api/debug`, which should show `"mode": "lakebase"` and `"status": "connected to Lakebase!"`.

## ⚙ CONFIG screen (app owner only)

On the home screen the app owner (the app creator, or the e-mails in the `SPACEBRICKS_ADMINS` environment variable) sees a **⚙ CONFIG** button:

- **Lakebase dropdown**: projects visible to the app, **"Criar novo Lakebase"** (create a new one, owned by the app's service principal), "Outro" (type an ID), or the temporary local database
- **LLM dropdown**: chat model endpoints available to the app, or "Sem IA" (canned narrator lines)
- **SALVAR E TESTAR** (save & test) tests the connection and the model, explains how to fix missing permissions, and saves the choice in the workspace so it survives restarts
- Warnings are shown when no Lakebase or model is available

## Sound

- Original chiptune music (menu, game and boss) and sound effects, all generated with WebAudio (no audio files)
- The **MÚSICA** (music) and **EFEITOS** (effects) buttons in the corner turn each one on/off; the choice is saved in the browser
- Music starts on the first click/key press (browser autoplay policy)

## Project structure

```
spacebricks/
├── LICENSE               # MIT (code only; does not cover trademarks)
├── databricks.yml        # Bundle: Lakebase + App + permissions (1-command deploy)
├── app.yaml              # App command and environment variables
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── backend/
│   ├── __init__.py
│   └── main.py           # FastAPI API + Lakebase + Foundation Models + config
└── frontend/
    └── index.html        # The whole game (HTML5 Canvas + JS + WebAudio)
```

## Tech stack

- **Frontend**: HTML5 Canvas, plain JavaScript, CSS
- **Backend**: FastAPI + Uvicorn
- **Database**: Lakebase Autoscaling (managed PostgreSQL), with a temporary SQLite fallback
- **In-game AI**: MLP neural network (JavaScript, client-side)
- **AI narrator**: Claude Sonnet 4.6 via the Foundation Model API
- **Deploy**: Databricks Apps

## Controls

| Key | Action |
|-----|--------|
| ← → or A/D | Move the ship |
| ↑ | Shoot |
| S / D / U / M | Use a special |
| SPACE | GENIE super special (when the bar is full) |
| ESC or ☰ MENU | Menu: resume, difficulty, restart, quit |
| MÚSICA / EFEITOS buttons | Toggle music / sound effects |

## License

The code is licensed under the MIT License (see [`LICENSE`](LICENSE)). The license covers the code only: it does **not** grant any rights to the names, logos or trademarks of Databricks or any third party.
