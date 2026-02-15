#!/usr/bin/env python3
"""
REST API für Maure's Strategie Club.

Läuft auf dem Server neben Streamlit und bietet einen HTTP-Endpunkt
für Multi-KI-Debatten. Nutzbar von ChatGPT GPTs, Claude MCP (remote)
oder jedem anderen HTTP-Client.

Start:  uvicorn api_server:app --host 0.0.0.0 --port 8502
"""

import io
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

load_dotenv()

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

API_TOKEN = os.environ.get("MSC_API_TOKEN", "")
security = HTTPBearer(auto_error=False)


def _check_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validate Bearer token if MSC_API_TOKEN is set."""
    if not API_TOKEN:
        return  # No token configured → open access
    if not credentials or credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Ungültiger API-Token")


# ---------------------------------------------------------------------------
# Debate engine (silence console)
# ---------------------------------------------------------------------------

import strategy_debate
from rich.console import Console

strategy_debate.console = Console(file=io.StringIO(), force_terminal=False)

# ---------------------------------------------------------------------------
# Job storage (in-memory)
# ---------------------------------------------------------------------------

_jobs: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class DebateRequest(BaseModel):
    document: str = Field(..., description="Der Dokumenttext (Markdown)")
    rounds: int = Field(3, ge=1, le=6, description="Anzahl Debattenrunden")
    supplementary_text: str = Field("", description="Optionaler Zusatzkontext")
    auto_stop: bool = Field(True, description="Automatisch bei Konvergenz stoppen")
    claude_model: str = Field("claude-sonnet-4-20250514")
    chatgpt_model: str = Field("gpt-4o")
    perplexity_model: str = Field("sonar-pro")


class DebateStartResponse(BaseModel):
    job_id: str
    status: str = "running"
    message: str


class DebateStatusResponse(BaseModel):
    job_id: str
    status: str  # "running", "done", "error"
    progress: str | None = None
    result: str | None = None
    rounds_completed: int | None = None
    stop_reason: str | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Maure's Strategie Club API",
    description="Multi-KI Strategy Debate – Claude × Perplexity × ChatGPT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_debate_job(job_id: str, req: DebateRequest):
    """Background worker for a debate job."""
    job = _jobs[job_id]
    try:
        input_text = req.document
        if req.supplementary_text.strip():
            input_text += f"\n\n---\n\n**Zusätzlicher Kontext:**\n{req.supplementary_text}"

        with tempfile.TemporaryDirectory(prefix="msc_api_") as tmpdir:
            output_dir = Path(tmpdir)

            def on_convergence(should_stop, confidence, reason, round_num):
                job["progress"] = (
                    f"Runde {round_num} abgeschlossen – "
                    f"Konvergenz: {'Ja' if should_stop else 'Nein'} ({confidence}%)"
                )

            text, full_log, rounds_completed, stop_reason = strategy_debate.run_debate(
                input_text=input_text,
                rounds=req.rounds,
                output_dir=output_dir,
                claude_model=req.claude_model,
                openai_model=req.chatgpt_model,
                perplexity_model=req.perplexity_model,
                resume=False,
                verbose=False,
                auto_stop=req.auto_stop,
                on_convergence=on_convergence,
            )

            job["progress"] = "Finale Synthese..."
            result = strategy_debate.final_synthesis(
                text, full_log, req.claude_model, verbose=False
            )

        job["status"] = "done"
        job["result"] = result
        job["rounds_completed"] = rounds_completed
        job["stop_reason"] = stop_reason
        job["progress"] = None

    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)
        job["progress"] = None


@app.post("/api/debate", response_model=DebateStartResponse)
def start_debate(req: DebateRequest, _=Security(_check_token)):
    """Startet eine neue Strategie-Debatte (asynchron).

    Gibt eine job_id zurück. Status und Ergebnis über GET /api/debate/{job_id} abrufbar.
    """
    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {
        "status": "running",
        "progress": "Debatte gestartet...",
        "result": None,
        "rounds_completed": None,
        "stop_reason": None,
        "error": None,
        "created": datetime.now(timezone.utc).isoformat(),
    }

    thread = threading.Thread(target=_run_debate_job, args=(job_id, req), daemon=True)
    thread.start()

    return DebateStartResponse(
        job_id=job_id,
        status="running",
        message=f"Debatte gestartet mit {req.rounds} Runden. Ergebnis abrufbar unter GET /api/debate/{job_id}",
    )


@app.get("/api/debate/{job_id}", response_model=DebateStatusResponse)
def get_debate_status(job_id: str, _=Security(_check_token)):
    """Prüft den Status einer laufenden Debatte oder gibt das Ergebnis zurück."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")

    job = _jobs[job_id]
    return DebateStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress"),
        result=job.get("result"),
        rounds_completed=job.get("rounds_completed"),
        stop_reason=job.get("stop_reason"),
        error=job.get("error"),
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Maure's Strategie Club API"}
