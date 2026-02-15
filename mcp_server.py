#!/usr/bin/env python3
"""
MCP Server für Maure's Strategie Club.

Ermöglicht es, direkt aus Claude Desktop heraus eine
Multi-KI-Strategie-Debatte zu starten.

Setup:
    pip install "mcp[cli]" anthropic openai python-dotenv rich

    Dann in Claude Desktop unter Settings → Developer → Edit Config:
    {
      "mcpServers": {
        "strategie-club": {
          "command": "python3",
          "args": ["/PFAD/ZU/mcp_server.py"],
          "env": {
            "ANTHROPIC_API_KEY": "sk-...",
            "OPENAI_API_KEY": "sk-...",
            "PERPLEXITY_API_KEY": "pplx-..."
          }
        }
      }
    }
"""

import io
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Lazy import + silence rich console output (would interfere with MCP stdio)
_debate_module = None


def _get_debate():
    global _debate_module
    if _debate_module is None:
        import strategy_debate
        from rich.console import Console

        strategy_debate.console = Console(file=io.StringIO(), force_terminal=False)
        _debate_module = strategy_debate
    return _debate_module


mcp = FastMCP(
    "Maure's Strategie Club",
    description="Multi-KI Strategy Debate Tool – lässt Dokumente durch Claude, Perplexity und ChatGPT rotieren.",
)


@mcp.tool()
def debate(
    document: str,
    rounds: int = 3,
    supplementary_text: str = "",
    auto_stop: bool = True,
    claude_model: str = "claude-sonnet-4-20250514",
    chatgpt_model: str = "gpt-4o",
    perplexity_model: str = "sonar-pro",
) -> str:
    """Startet eine Multi-KI-Strategie-Debatte.

    Das Dokument wird in mehreren Runden von Claude (Strategie-Review),
    Perplexity (Faktencheck) und ChatGPT (Synthese + Rhetorik) überarbeitet.
    Am Ende entsteht ein finales Dokument mit Dissens-Register.

    Args:
        document: Der Text des Strategiedokuments (Markdown).
        rounds: Anzahl der Debattenrunden (1-6, Standard: 3).
        supplementary_text: Optionaler Zusatztext/Kontext zum Dokument.
        auto_stop: Automatisch stoppen wenn Konvergenz erkannt wird.
        claude_model: Claude-Modell-ID.
        chatgpt_model: ChatGPT-Modell-ID.
        perplexity_model: Perplexity-Modell-ID.

    Returns:
        Das finale, überarbeitete Dokument inklusive Dissens-Register.
    """
    sd = _get_debate()

    # Validate
    rounds = max(1, min(6, rounds))

    # Combine document with supplementary text
    input_text = document
    if supplementary_text.strip():
        input_text += f"\n\n---\n\n**Zusätzlicher Kontext:**\n{supplementary_text}"

    # Use a temp dir for intermediate files
    with tempfile.TemporaryDirectory(prefix="msc_debate_") as tmpdir:
        output_dir = Path(tmpdir)

        text, full_log, rounds_completed, stop_reason = sd.run_debate(
            input_text=input_text,
            rounds=rounds,
            output_dir=output_dir,
            claude_model=claude_model,
            openai_model=chatgpt_model,
            perplexity_model=perplexity_model,
            resume=False,
            verbose=False,
            auto_stop=auto_stop,
        )

        result = sd.final_synthesis(text, full_log, claude_model, verbose=False)

    # Add metadata header
    meta = f"<!-- MSC Debate: {rounds_completed} Runden"
    if stop_reason:
        meta += f" (Auto-Stop: {stop_reason})"
    meta += " -->\n\n"

    return meta + result


@mcp.tool()
def debate_quick(document: str) -> str:
    """Schnelle Strategie-Debatte mit 2 Runden.

    Kurzversion für schnelles Feedback. Nutzt die Standard-Modelle
    und aktiviert Auto-Stop.

    Args:
        document: Der Text des Strategiedokuments.

    Returns:
        Das überarbeitete Dokument mit Dissens-Register.
    """
    return debate(document=document, rounds=2, auto_stop=True)


if __name__ == "__main__":
    mcp.run()
