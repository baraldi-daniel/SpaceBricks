import os
import re
import json
import time
import random
import sqlite3
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import psycopg2
from databricks.sdk import WorkspaceClient
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================================
# Configuracao
#   Prioridade: (1) o que o admin salvou na tela ⚙ CONFIG do jogo
#               (2) recursos do app (Edit > App resources): chaves "lakebase" e "llm"
#               (3) variaveis de ambiente / defaults
#   Sem Lakebase o jogo funciona com um banco LOCAL temporario e a tela avisa.
# ======================================================================
APP_NAME = os.getenv("DATABRICKS_APP_NAME", "spacebricks")
DB_SCHEMA = os.getenv("DB_SCHEMA") or re.sub(r"[^a-z0-9_]", "_", APP_NAME.lower())   # 1 schema por app
LAKEBASE_RESOURCE = os.getenv("LAKEBASE_RESOURCE", "")   # valueFrom: lakebase -> projects/<p>/branches/<b>/endpoints/<e>
DEFAULT_PROJECT = os.getenv("LAKEBASE_PROJECT", "")
DEFAULT_BRANCH = os.getenv("LAKEBASE_BRANCH", "production")
LAKEBASE_ENDPOINT = os.getenv("LAKEBASE_ENDPOINT", "primary")
DEFAULT_LLM = os.getenv("LLM_ENDPOINT") or "databricks-claude-sonnet-4-6"   # valueFrom: llm -> nome do serving endpoint
ADMINS = {e.strip().lower() for e in os.getenv("SPACEBRICKS_ADMINS", "").split(",") if e.strip()}
# Banco de reserva quando nao ha Lakebase. ATENCAO: some quando o app reinicia.
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "/tmp/spacebricks.db")

try:
    w = WorkspaceClient()
except Exception as e:  # roda mesmo fora do Databricks (sem credenciais)
    logger.warning(f"WorkspaceClient indisponível: {e}")
    w = None

STATE = {
    "db_mode": "local", "db_project": None, "db_branch": None, "db_error": "nenhum Lakebase configurado",
    "llm_endpoint": None, "llm_ok": None, "llm_error": None, "config_source": "padrão",
}
_lock = threading.Lock()


def _sp_id():
    return (w.config.client_id if w else None) or (str(w.current_user.me().id) if w else "local")


# ---------------- config salva (arquivo no workspace do service principal) ----------------
def _cfg_path():
    return f"/Users/{_sp_id()}/.spacebricks/{APP_NAME}.json"


def load_saved_config():
    if w is None:
        return {}
    try:
        with w.workspace.download(_cfg_path()) as f:
            return json.loads(f.read().decode())
    except Exception:
        return {}


def save_config(cfg: dict):
    if w is None:
        return "sem credenciais"
    try:
        from databricks.sdk.service.workspace import ImportFormat
        path = _cfg_path()
        w.workspace.mkdirs(path.rsplit("/", 1)[0])
        w.workspace.upload(path, json.dumps(cfg).encode(), format=ImportFormat.AUTO, overwrite=True)
        return None
    except Exception as e:
        logger.warning(f"Não consegui salvar a config no workspace: {e}")
        return str(e)


# ---------------- Lakebase (Postgres) ----------------
def _ep_path(project, branch):
    return f"projects/{project}/branches/{branch}/endpoints/{LAKEBASE_ENDPOINT}"


def _lakebase_conn(project=None, branch=None):
    if w is None:
        raise RuntimeError("sem credenciais do Databricks")
    project = project or STATE["db_project"]; branch = branch or STATE["db_branch"] or "production"
    if not project:
        raise RuntimeError("nenhum Lakebase configurado")
    ep_path = _ep_path(project, branch)
    ep = w.postgres.get_endpoint(name=ep_path)
    host = ep.status.hosts.host
    cred = w.postgres.generate_database_credential(endpoint=ep_path)
    return psycopg2.connect(host=host, port=5432, user=_sp_id(), password=cred.token, dbname="databricks_postgres",
                            sslmode="require", options=f"-c search_path={DB_SCHEMA}", connect_timeout=10)


DDL_PG = [
    "CREATE SCHEMA IF NOT EXISTS {schema}",
    """CREATE TABLE IF NOT EXISTS {schema}.players (
        id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
        company TEXT NOT NULL, phone TEXT, registered_at TIMESTAMPTZ DEFAULT NOW(),
        has_real_case BOOLEAN DEFAULT FALSE, real_case_notes TEXT)""",
    """CREATE TABLE IF NOT EXISTS {schema}.scores (
        id SERIAL PRIMARY KEY, player_email TEXT NOT NULL,
        score INTEGER NOT NULL, waves_cleared INTEGER DEFAULT 0,
        ai_difficulty REAL DEFAULT 1.0, played_at TIMESTAMPTZ DEFAULT NOW())""",
    "CREATE INDEX IF NOT EXISTS idx_scores_score ON {schema}.scores(score DESC)",
]


def _explain_db_error(e, project):
    msg = str(e).strip().splitlines()[0][:300]
    low = msg.lower()
    if "password authentication failed" in low or "permission" in low or "not authorized" in low or "forbidden" in low:
        return (f"O app não tem acesso ao Lakebase '{project}'. Adicione-o como recurso do app "
                f"(Compute > Apps > {APP_NAME} > Edit > App resources > Database, permissao 'Can connect and create') "
                f"e reinicie, ou escolha 'Criar novo Lakebase' na tela de configuração. Detalhe: {msg}")
    if "does not exist" in low or "not found" in low:
        return f"Lakebase '{project}' não encontrado neste workspace. Detalhe: {msg}"
    if "schema" in low:
        return f"Sem permissao no schema '{DB_SCHEMA}' (pode pertencer a outro app). Defina DB_SCHEMA diferente. Detalhe: {msg}"
    return msg


def try_lakebase(project, branch):
    """Conecta, cria schema/tabelas e, se der certo, passa a usar este Lakebase."""
    branch = branch or "production"
    try:
        conn = _lakebase_conn(project, branch)
        cur = conn.cursor()
        for ddl in DDL_PG:
            cur.execute(ddl.format(schema=DB_SCHEMA))
        conn.commit(); cur.close(); conn.close()
        with _lock:
            STATE.update(db_mode="lakebase", db_project=project, db_branch=branch, db_error=None)
        logger.info(f"Lakebase pronto: {project}/{branch} (schema {DB_SCHEMA})")
        return None
    except Exception as e:
        err = _explain_db_error(e, project)
        logger.warning(f"Lakebase {project}/{branch} indisponível: {err}")
        return err


def use_local(reason):
    with _lock:
        STATE.update(db_mode="local", db_error=reason)
    conn = _LocalConn(); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
        company TEXT NOT NULL, phone TEXT, registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
        has_real_case BOOLEAN DEFAULT FALSE, real_case_notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT, player_email TEXT NOT NULL,
        score INTEGER NOT NULL, waves_cleared INTEGER DEFAULT 0,
        ai_difficulty REAL DEFAULT 1.0, played_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scores_score ON scores(score DESC)")
    conn.commit(); cur.close(); conn.close()
    logger.warning(f"Usando banco LOCAL temporário ({LOCAL_DB_PATH}): {reason}")


def create_lakebase(project_id):
    """Cria um projeto Lakebase novo (dono = service principal do app) e espera ficar pronto."""
    if w is None:
        return "sem credenciais do Databricks"
    try:
        w.api_client.do("POST", "/api/2.0/postgres/projects", query={"project_id": project_id},
                        body={"spec": {"display_name": f"SpaceBricks ({APP_NAME})", "pg_version": 17}})
    except Exception as e:
        if "already exists" not in str(e).lower():
            return f"Não consegui criar o Lakebase '{project_id}': {str(e)[:300]}"
    for _ in range(60):   # ate ~2 min
        try:
            ep = w.postgres.get_endpoint(name=_ep_path(project_id, "production"))
            if ep.status and ep.status.hosts and ep.status.hosts.host:
                return None
        except Exception:
            pass
        time.sleep(2)
    return f"Lakebase '{project_id}' criado, mas ainda não ficou pronto. Tente de novo em 1 minuto."


def list_lakebase_projects():
    out = []
    if w is None:
        return out
    try:
        for p in w.postgres.list_projects():
            pid = p.name.split("/")[-1]
            disp = getattr(getattr(p, "status", None), "display_name", None) or getattr(getattr(p, "spec", None), "display_name", None) or pid
            out.append({"id": pid, "name": disp})
    except Exception as e:
        logger.warning(f"Não consegui listar Lakebase: {e}")
    return out


# ---------------- LLM ----------------
def list_llm_endpoints():
    out = []
    if w is None:
        return out
    try:
        for ep in w.serving_endpoints.list():
            task = (getattr(ep, "task", None) or "")
            name = ep.name
            if "chat" in task or any(k in name for k in ("claude", "gpt", "llama", "gemini", "gemma", "qwen", "mistral")):
                out.append(name)
    except Exception as e:
        logger.warning(f"Não consegui listar endpoints: {e}")
    out.sort(key=lambda n: (0 if "claude" in n else 1, n))
    return out


def test_llm(name):
    if not name:
        return "nenhum modelo escolhido"
    if w is None:
        return "sem credenciais do Databricks"
    try:
        from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
        w.serving_endpoints.query(name=name, messages=[ChatMessage(role=ChatMessageRole.USER, content="Responda so: ok")], max_tokens=5)
        return None
    except Exception as e:
        msg = str(e).strip().splitlines()[0][:300]
        if "permission" in msg.lower() or "forbidden" in msg.lower() or "not authorized" in msg.lower():
            return (f"O app não tem permissão para usar '{name}'. Adicione-o como recurso do app "
                    f"(Edit > App resources > Serving endpoint, 'Can query'). Detalhe: {msg}")
        return msg


def set_llm(name):
    err = test_llm(name) if name else None
    with _lock:
        STATE.update(llm_endpoint=name or None, llm_ok=(err is None) if name else None, llm_error=err)
    logger.info(f"Narrador: {name or 'sem IA'} -> {'OK' if (name and not err) else (err or 'frases prontas')}")
    return err


# ---------------- SQLite local (reserva) ----------------
class _LocalCursor:
    def __init__(self, cur):
        self._c = cur

    def execute(self, sql, params=()):
        return self._c.execute(sql.replace("%s", "?"), params)

    def fetchone(self):
        return self._c.fetchone()

    def fetchall(self):
        return self._c.fetchall()

    def close(self):
        self._c.close()


class _LocalConn:
    def __init__(self):
        self._c = sqlite3.connect(LOCAL_DB_PATH)

    def cursor(self):
        return _LocalCursor(self._c.cursor())

    def commit(self):
        self._c.commit()

    def close(self):
        self._c.close()


def get_db():
    return _LocalConn() if STATE["db_mode"] == "local" else _lakebase_conn()


def _parse_resource(path):
    m = re.match(r"projects/([^/]+)/branches/([^/]+)", path or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def startup():
    saved = load_saved_config()
    res_project, res_branch = _parse_resource(LAKEBASE_RESOURCE)
    if saved.get("lakebase_project") is not None:
        project, branch, src = saved.get("lakebase_project"), saved.get("lakebase_branch") or "production", "tela de configuração"
    elif res_project:
        project, branch, src = res_project, res_branch, "recurso do app"
    else:
        project, branch, src = DEFAULT_PROJECT, DEFAULT_BRANCH, "padrão"
    STATE["config_source"] = src
    err = try_lakebase(project, branch) if project else "nenhum Lakebase configurado"
    if err:
        use_local(err)
    llm = saved["llm_endpoint"] if "llm_endpoint" in saved else (DEFAULT_LLM or "")
    threading.Thread(target=set_llm, args=(llm,), daemon=True).start()


# ---------------- admin ----------------
_creator = {"v": None, "checked": False}


def is_admin(request: Request):
    email = (request.headers.get("x-forwarded-email") or "").lower()
    if not email:              # rodando local / sem proxy do Databricks Apps
        return True
    if ADMINS:
        return email in ADMINS
    if not _creator["checked"]:
        _creator["checked"] = True
        try:
            _creator["v"] = (w.apps.get(APP_NAME).creator or "").lower() if w else None
        except Exception as e:
            logger.warning(f"Não consegui descobrir o dono do app ({e}); config liberada para todos os usuários")
    return (not _creator["v"]) or email == _creator["v"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        startup()
    except Exception as e:
        logger.error(f"Init error: {e}")
        try:
            use_local(str(e))
        except Exception:
            pass
    yield


app = FastAPI(title="SpaceBricks", lifespan=lifespan)
frontend_dir = Path(__file__).parent.parent / "frontend"


class ConfigUpdate(BaseModel):
    lakebase_project: Optional[str] = None   # "" = banco local temporario
    lakebase_branch: Optional[str] = "production"
    create_new: bool = False
    llm_endpoint: Optional[str] = None       # "" = sem IA (frases prontas)


def _public_state():
    s = dict(STATE)
    s["db_schema"] = DB_SCHEMA
    s["app_name"] = APP_NAME
    s["suggested_project"] = re.sub(r"[^a-z0-9-]", "-", f"{APP_NAME}-db".lower())[:63]
    return s


@app.get("/api/status")
def api_status(request: Request):
    return {"db_mode": STATE["db_mode"], "llm_ok": STATE["llm_ok"], "is_admin": is_admin(request)}


@app.get("/api/config")
def api_get_config(request: Request):
    if not is_admin(request):
        return {"is_admin": False}
    projects = list_lakebase_projects()
    llms = list_llm_endpoints()
    warnings = []
    if not projects:
        warnings.append(f"Nenhum Lakebase visivel para o app. Escolha 'Criar novo Lakebase' ou adicione um recurso Database no app "
                        f"(Compute > Apps > {APP_NAME} > Edit > App resources).")
    if not llms:
        warnings.append("Nenhum modelo de LLM disponivel para o app. Adicione um recurso Serving endpoint no app "
                        "(Edit > App resources) ou jogue com as frases prontas do narrador.")
    if STATE["db_mode"] == "local":
        warnings.append("Sem Lakebase: ranking e cadastros estão num banco TEMPORÁRIO e somem quando o app reiniciar.")
    return {"is_admin": True, "state": _public_state(), "projects": projects, "llms": llms, "warnings": warnings}


@app.post("/api/config")
def api_set_config(cfg: ConfigUpdate, request: Request):
    if not is_admin(request):
        return {"ok": False, "error": "Somente o dono do app pode alterar a configuração."}
    result = {"ok": True, "db": None, "llm": None, "saved": None}
    project = (cfg.lakebase_project or "").strip()
    branch = (cfg.lakebase_branch or "production").strip() or "production"
    if cfg.create_new:
        project = project or _public_state()["suggested_project"]
        err = create_lakebase(project)
        if err:
            result.update(ok=False, db=err)
    if result["db"] is None:
        if project:
            err = try_lakebase(project, branch)
            if err:
                result.update(ok=False, db=err)
            else:
                result["db"] = f"Conectado ao Lakebase '{project}' (schema {DB_SCHEMA})."
        else:
            use_local("banco local escolhido na configuração")
            result["db"] = "Usando banco local TEMPORÁRIO (some ao reiniciar o app)."
    llm = (cfg.llm_endpoint or "").strip()
    err = set_llm(llm)
    result["llm"] = err or (f"Modelo '{llm}' respondendo." if llm else "Narrador com frases prontas (sem IA).")
    if err:
        result["ok"] = False
    if result["ok"] or STATE["db_mode"] == "lakebase":
        save_err = save_config({"lakebase_project": STATE["db_project"] if STATE["db_mode"] == "lakebase" else "",
                                "lakebase_branch": STATE["db_branch"] or "production",
                                "llm_endpoint": STATE["llm_endpoint"] or ""})
        result["saved"] = "Configuração salva (vale após reiniciar o app)." if not save_err else f"Aviso: não consegui salvar a configuração ({save_err[:120]})."
    result["state"] = _public_state()
    return result


@app.get("/")
def serve_index():
    p = frontend_dir / "index.html"
    return FileResponse(str(p), media_type="text/html") if p.exists() else HTMLResponse("<h1>Not found</h1>", 404)


class PlayerRegistration(BaseModel):
    name: str
    email: str
    company: str
    phone: Optional[str] = None

class ScoreSubmission(BaseModel):
    email: str
    score: int
    waves_cleared: int = 0
    ai_difficulty: float = 1.0

class RealCaseSubmission(BaseModel):
    email: str
    notes: str


@app.post("/api/register")
def register_player(player: PlayerRegistration):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO players (name,email,company,phone) VALUES (%s,%s,%s,%s) ON CONFLICT (email) DO UPDATE SET name=EXCLUDED.name, company=EXCLUDED.company",
                    (player.name, player.email, player.company, player.phone))
        conn.commit(); cur.close(); conn.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Register: {e}")
        return {"status": "ok"}


@app.post("/api/score")
def submit_score(sub: ScoreSubmission):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO scores (player_email,score,waves_cleared,ai_difficulty) VALUES (%s,%s,%s,%s)",
                    (sub.email, sub.score, sub.waves_cleared, sub.ai_difficulty))
        conn.commit(); cur.close(); conn.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Score: {e}")
        return {"status": "ok"}


@app.post("/api/real-case")
def submit_real_case(case: RealCaseSubmission):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("UPDATE players SET has_real_case=TRUE, real_case_notes=%s WHERE email=%s", (case.notes, case.email))
        conn.commit(); cur.close(); conn.close()
    except Exception as e:
        logger.error(f"Case: {e}")
    return {"status": "ok", "reward": "premium"}


@app.get("/api/leaderboard")
def get_leaderboard(limit: int = 20):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("""SELECT s.player_email, p.name, p.company, MAX(s.score) as best, MAX(s.waves_cleared) as waves
            FROM scores s LEFT JOIN players p ON s.player_email=p.email
            GROUP BY s.player_email, p.name, p.company ORDER BY best DESC LIMIT %s""", (limit,))
        rows = cur.fetchall(); cur.close(); conn.close()
        return {"leaderboard": [{"rank":i+1,"name":r[1] or r[0],"company":r[2] or "","score":r[3],"waves":r[4]} for i,r in enumerate(rows)]}
    except Exception as e:
        logger.error(f"Leaderboard: {e}")
        return {"leaderboard": []}


@app.get("/api/stats")
def get_stats():
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM players"); tp=cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scores"); tg=cur.fetchone()[0]
        cur.execute("SELECT COALESCE(MAX(score),0) FROM scores"); hs=cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM players WHERE has_real_case=TRUE"); rc=cur.fetchone()[0]
        cur.close(); conn.close()
        return {"total_players":tp,"total_games":tg,"highest_score":hs,"real_cases":rc}
    except Exception as e:
        logger.error(f"Stats: {e}")
        return {"total_players":0,"total_games":0,"highest_score":0,"real_cases":0}


@app.get("/api/percentile")
def get_percentile(score: int):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(CASE WHEN best<=%s THEN 1 END),COUNT(*) FROM (SELECT player_email,MAX(score) as best FROM scores GROUP BY player_email) sub", (score,))
        r=cur.fetchone(); cur.close(); conn.close()
        return {"percentile":round((r[0]/r[1])*100) if r[1]>0 else 100,"total_players":r[1]}
    except Exception as e:
        logger.error(f"Pct: {e}")
        return {"percentile":50,"total_players":0}


@app.post("/api/ai-taunt")
def ai_taunt(data: dict):
    try:
        if not STATE["llm_endpoint"] or STATE["llm_ok"] is False or w is None:
            raise RuntimeError("sem LLM configurado")
        wv=data.get("wave",1); sc=data.get("score",0); lv=data.get("lives",3)
        boss=data.get("boss_name",""); bias=data.get("player_bias","")
        bh=""
        if bias=="esquerda": bh=" A IA detectou que o jogador fica muito na esquerda."
        elif bias=="direita": bh=" A IA detectou que o jogador fica muito na direita."
        elif bias=="centro": bh=" A IA detectou que o jogador fica muito no centro."
        if boss:
            p=f"Você é o narrador de um jogo arcade de dados. Wave {wv}, {sc} pts, {lv} vidas.{bh}\nO boss '{boss}' apareceu! Escreva UMA frase curta (max 12 palavras) em portugues motivando e provocando. Responda APENAS a frase, sem aspas."
        else:
            p=f"Você é o narrador de um jogo arcade de dados. Wave {wv}, {sc} pts, {lv} vidas.{bh}\nEscreva UMA frase curta (max 12 palavras) em portugues como narrador de e-sports. Se tiver info sobre posicao, comente. Responda APENAS a frase, sem aspas."
        from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
        r=w.serving_endpoints.query(name=STATE["llm_endpoint"],messages=[ChatMessage(role=ChatMessageRole.USER,content=p)],max_tokens=60,temperature=0.9)
        return {"taunt":r.choices[0].message.content.strip().strip('"').strip("'")}
    except Exception as e:
        logger.error(f"Taunt: {e}")
        fb=["Seus dados estão uma zona!","Essa wave vai ser pesada!","Os inimigos estão aprendendo!","Nem Spark te salva!","Vou fragmentar seus pipelines!"]
        return {"taunt":random.choice(fb)}


@app.get("/api/debug")
def debug():
    s = _public_state()
    info = {"mode": s["db_mode"], "lakebase_project": s["db_project"], "branch": s["db_branch"], "schema": DB_SCHEMA,
            "llm_endpoint": s["llm_endpoint"], "llm_ok": s["llm_ok"], "config_source": s["config_source"]}
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM players"); info["players"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM scores"); info["scores"] = cur.fetchone()[0]
        cur.close(); conn.close()
        info["status"] = "connected to Lakebase!" if s["db_mode"] == "lakebase" else f"LOCAL temporário: {s['db_error']}"
    except Exception as e:
        info["status"] = f"error: {e}"
    return info


@app.get("/health")
def health():
    return {"status": "healthy"}
