#!/usr/bin/env python3
"""
Strategy Debate Tool
Automatisierte Multi-KI-Dokumentenoptimierung.

Lässt ein Strategiedokument in mehreren Runden durch Claude, Perplexity
und ChatGPT rotieren. Jedes System kritisiert und verbessert den Text.
Am Ende entsteht ein finales Dokument mit Dissens-Register.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

load_dotenv()

console = Console()

# ---------------------------------------------------------------------------
# System-Prompts
# ---------------------------------------------------------------------------

SYSTEM_CLAUDE = """\
Du bist ein kritischer Strategie-Reviewer. Deine Aufgabe:

1. Analysiere das Dokument auf logische Schwächen, implizite Annahmen, \
Widersprüche und fehlende Stakeholder-Perspektiven.
2. Überarbeite den Text direkt – verbessere ihn, statt nur zu kommentieren.
3. Wenn du mit einer Position eines vorherigen Reviewers nicht einverstanden \
bist, markiere das als DISSENS.

WICHTIG: Inhalte zwischen <!-- LOCKED_START --> und <!-- LOCKED_END --> \
dürfen inhaltlich NICHT verändert werden. Nur minimale Formulierungskosmetik \
ist erlaubt.

Antworte EXAKT in diesem Format:

---DOKUMENT---
(Dein überarbeiteter Text hier)
---KRITIKPUNKTE---
- [GEÄNDERT] Was du geändert hast: Begründung
- [HINZUGEFÜGT] Was du ergänzt hast: Begründung
- [DISSENS] Widerspruch zu vorherigem Reviewer: Deine Position und warum
---ENDE---"""

SYSTEM_PERPLEXITY = """\
Du bist ein Research-Assistent für Strategiedokumente. Deine Aufgabe:

1. Prüfe Faktenaussagen im Dokument auf Korrektheit.
2. Ergänze aktuelle Trends, Marktdaten oder relevante Entwicklungen.
3. Identifiziere typische Fallstricke der beschriebenen Strategie.
4. Ändere den Kern nur, wenn fachlich nötig.
5. Wenn du mit einer Position eines vorherigen Reviewers nicht einverstanden \
bist, markiere das als DISSENS.

WICHTIG: Inhalte zwischen <!-- LOCKED_START --> und <!-- LOCKED_END --> \
dürfen inhaltlich NICHT verändert werden.

Antworte EXAKT in diesem Format:

---DOKUMENT---
(Dein überarbeiteter Text hier)
---KRITIKPUNKTE---
- [GEÄNDERT] Was du geändert hast: Begründung
- [HINZUGEFÜGT] Was du ergänzt hast: Begründung
- [DISSENS] Widerspruch zu vorherigem Reviewer: Deine Position und warum
---ENDE---"""

SYSTEM_CHATGPT = """\
Du bist ein Synthese-Architekt und kritischer Gegenleser für Strategiedokumente. \
Deine Aufgabe ist es, das Dokument AKTIV zu verbessern – nicht nur durchzuwinken.

1. Optimiere Struktur und Aufbau des Dokuments. Wenn die Gliederung nicht \
überzeugt, baue sie um.
2. Schärfe die Argumentationslinie – jeder Abschnitt soll klar zur \
Gesamtargumentation beitragen. Schwache Argumente müssen gestärkt oder \
durch bessere ersetzt werden.
3. Baue klare Überschriften und Entscheidungsoptionen ein.
4. Beseitige Redundanzen und verbessere die Lesbarkeit.
5. Hinterfrage die strategische Umsetzbarkeit: Sind Maßnahmen konkret genug? \
Fehlen Verantwortlichkeiten, Zeithorizonte oder Erfolgskriterien?
6. Wenn du mit einer Position eines vorherigen Reviewers nicht einverstanden \
bist, markiere das als DISSENS.

WICHTIG: Du MUSST substantielle Änderungen vornehmen und mindestens 3 \
Kritikpunkte liefern. "Keine Änderungen nötig" ist KEINE akzeptable Antwort. \
Finde immer Verbesserungspotenzial – es gibt kein perfektes Dokument.

WICHTIG: Inhalte zwischen <!-- LOCKED_START --> und <!-- LOCKED_END --> \
dürfen inhaltlich NICHT verändert werden.

Antworte EXAKT in diesem Format:

---DOKUMENT---
(Dein überarbeiteter Text hier)
---KRITIKPUNKTE---
- [GEÄNDERT] Was du geändert hast: Begründung
- [HINZUGEFÜGT] Was du ergänzt hast: Begründung
- [DISSENS] Widerspruch zu vorherigem Reviewer: Deine Position und warum
---ENDE---"""

SYSTEM_CONVERGENCE = """\
Du bist ein Meta-Reviewer, der beurteilt, ob weitere Optimierungsrunden \
eines Strategiedokuments noch substanziellen Mehrwert bringen.

Du erhältst:
- Das Dokument VOR der letzten Runde
- Das Dokument NACH der letzten Runde
- Die Kritikpunkte der letzten Runde

Bewerte anhand dieser Kriterien:
1. **Änderungsvolumen**: Wurde noch viel am Text verändert oder nur Formulierungen?
2. **Kritik-Schwere**: Sind die Kritikpunkte strukturell oder nur kosmetisch?
3. **Neue Aspekte**: Kommen noch neue inhaltliche Punkte dazu?
4. **Dissens-Stabilität**: Wiederholen sich die DISSENS-Punkte aus früheren Runden?

Antworte EXAKT in diesem Format:

---VERDICT---
STOP oder CONTINUE
---CONFIDENCE---
(Zahl von 0-100, wie sicher du dir bist)
---REASON---
(2-3 Sätze Begründung auf Deutsch)
---ENDE---"""

SYSTEM_SYNTHESIS = """\
Du bist ein Meta-Synthese-Moderator. Du erhältst ein Strategiedokument, \
das in mehreren Runden von drei KI-Systemen (Claude, Perplexity, ChatGPT) \
überarbeitet wurde, sowie den vollständigen Kritik-Verlauf.

Deine Aufgabe:
1. Erstelle ein finales, sauberes Strategiedokument in Markdown.
   - Entferne alle Meta-Kommentare und Reviewer-Notizen.
   - Das Dokument soll so wirken, als wäre es von einem Experten geschrieben.
2. Erstelle am Ende einen Abschnitt "## Dissens-Register".
   - Liste jeden Punkt auf, bei dem die KI-Systeme unterschiedliche, \
nicht kompromissfähige Positionen hatten.
   - Format pro Eintrag:
     **Thema:** [Beschreibung]
     - **Position Claude:** [...]
     - **Position Perplexity:** [...]
     - **Position ChatGPT:** [...]
     - **Empfehlung:** [Empfehlung für die menschliche Entscheidung]
3. Falls keine echten Dissens-Punkte existieren, schreibe: \
"Alle drei Systeme konnten sich auf eine gemeinsame Position einigen."

WICHTIG: Inhalte zwischen <!-- LOCKED_START --> und <!-- LOCKED_END --> \
müssen unverändert im finalen Dokument erscheinen (ohne die Marker selbst)."""

# ---------------------------------------------------------------------------
# API-Clients (lazy init)
# ---------------------------------------------------------------------------

_claude_client = None
_openai_client = None
_perplexity_client = None


def get_claude():
    global _claude_client
    if _claude_client is None:
        from anthropic import Anthropic
        _claude_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _claude_client


def get_openai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai_client


def get_perplexity():
    global _perplexity_client
    if _perplexity_client is None:
        from openai import OpenAI
        _perplexity_client = OpenAI(
            api_key=os.environ["PERPLEXITY_API_KEY"],
            base_url="https://api.perplexity.ai",
        )
    return _perplexity_client


# ---------------------------------------------------------------------------
# API-Aufrufe mit Retry
# ---------------------------------------------------------------------------

def _retry(func, max_retries=3):
    """Führt func() aus mit exponentiellem Backoff bei transienten Fehlern."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            err_str = str(e)
            status = getattr(e, "status_code", None) or getattr(e, "status", None)
            is_transient = status in (429, 500, 502, 503, 529)
            if not is_transient and ("rate" in err_str.lower() or "overloaded" in err_str.lower()):
                is_transient = True
            if is_transient and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                console.print(f"  [yellow]Retry in {wait}s ({e})[/yellow]")
                time.sleep(wait)
            else:
                raise


def call_claude(text: str, critique_log: str, model: str) -> str:
    user_msg = f"Bisheriger Kritik-Verlauf:\n{critique_log}\n\n---\n\nAktuelles Dokument:\n{text}"

    def _call():
        msg = get_claude().messages.create(
            model=model,
            max_tokens=8192,
            system=SYSTEM_CLAUDE,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text

    return _retry(_call)


def call_perplexity(text: str, critique_log: str, model: str) -> str:
    user_msg = f"Bisheriger Kritik-Verlauf:\n{critique_log}\n\n---\n\nAktuelles Dokument:\n{text}"

    def _call():
        resp = get_perplexity().chat.completions.create(
            model=model,
            max_tokens=8192,
            messages=[
                {"role": "system", "content": SYSTEM_PERPLEXITY},
                {"role": "user", "content": user_msg},
            ],
        )
        return resp.choices[0].message.content

    return _retry(_call)


def call_chatgpt(text: str, critique_log: str, model: str) -> str:
    user_msg = f"Bisheriger Kritik-Verlauf:\n{critique_log}\n\n---\n\nAktuelles Dokument:\n{text}"

    def _call():
        resp = get_openai().chat.completions.create(
            model=model,
            max_tokens=8192,
            messages=[
                {"role": "system", "content": SYSTEM_CHATGPT},
                {"role": "user", "content": user_msg},
            ],
        )
        return resp.choices[0].message.content

    return _retry(_call)


def call_convergence_check(doc_before: str, doc_after: str, critique: str,
                           round_num: int, model: str) -> tuple[bool, int, str]:
    """Prüft ob weitere Runden noch Mehrwert bringen.

    Returns: (should_stop, confidence, reason)
    """
    user_msg = (
        f"Runde {round_num} wurde gerade abgeschlossen.\n\n"
        f"=== DOKUMENT VOR DER RUNDE ===\n{doc_before}\n\n"
        f"=== DOKUMENT NACH DER RUNDE ===\n{doc_after}\n\n"
        f"=== KRITIKPUNKTE DIESER RUNDE ===\n{critique}\n"
    )

    def _call():
        msg = get_claude().messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_CONVERGENCE,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text

    raw = _retry(_call)

    # Parse verdict
    import re as _re
    verdict_match = _re.search(r"---VERDICT---\s*\n\s*(STOP|CONTINUE)", raw)
    conf_match = _re.search(r"---CONFIDENCE---\s*\n\s*(\d+)", raw)
    reason_match = _re.search(r"---REASON---\s*\n(.*?)---ENDE---", raw, _re.DOTALL)

    should_stop = verdict_match and verdict_match.group(1).strip() == "STOP"
    confidence = int(conf_match.group(1)) if conf_match else 50
    reason = reason_match.group(1).strip() if reason_match else "Keine Begründung extrahiert."

    return should_stop, confidence, reason


def call_synthesis(text: str, full_log: str, model: str) -> str:
    user_msg = (
        f"Finaler Dokumenttext nach allen Runden:\n\n{text}\n\n"
        f"---\n\nVollständiger Kritik-Verlauf:\n\n{full_log}"
    )

    def _call():
        msg = get_claude().messages.create(
            model=model,
            max_tokens=8192,
            system=SYSTEM_SYNTHESIS,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text

    return _retry(_call)


# ---------------------------------------------------------------------------
# Parsing & Log-Management
# ---------------------------------------------------------------------------

def parse_structured_output(raw: str) -> tuple[str, str]:
    """Trennt die KI-Antwort in (dokument, kritikpunkte)."""
    doc_match = re.search(r"---DOKUMENT---\s*\n(.*?)---KRITIKPUNKTE---", raw, re.DOTALL)
    crit_match = re.search(r"---KRITIKPUNKTE---\s*\n(.*?)---ENDE---", raw, re.DOTALL)

    if doc_match and crit_match:
        return doc_match.group(1).strip(), crit_match.group(1).strip()

    # Fallback: wenn das Format nicht eingehalten wurde, nimm alles als Dokument
    console.print("  [yellow]Warnung: Strukturiertes Format nicht erkannt, nutze Rohausgabe[/yellow]")
    return raw.strip(), "(Keine strukturierten Kritikpunkte extrahiert)"


def compress_critique_log(full_log: str, max_chars: int = 4000) -> str:
    """Kürzt den Kritik-Log auf DISSENS-Punkte + die wichtigsten Änderungen."""
    if len(full_log) <= max_chars:
        return full_log

    lines = full_log.split("\n")
    dissens = [l for l in lines if "[DISSENS]" in l]
    headers = [l for l in lines if l.startswith("[Runde")]
    other = [l for l in lines if l.startswith("- [") and "[DISSENS]" not in l]

    compressed = "\n".join(headers + dissens + other[:10])
    if len(compressed) > max_chars:
        compressed = compressed[:max_chars] + "\n... (gekürzt)"
    return compressed


# ---------------------------------------------------------------------------
# Zwischenspeicherung & Resume
# ---------------------------------------------------------------------------

def save_intermediate(output_dir: Path, round_num: int, system: str, doc: str, critique: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"runde_{round_num}_{system}.md").write_text(doc, encoding="utf-8")
    (output_dir / f"runde_{round_num}_{system}_kritik.md").write_text(critique, encoding="utf-8")


def find_resume_point(output_dir: Path, total_rounds: int) -> tuple[int, str, str]:
    """Findet die letzte erfolgreiche Runde/System und gibt (runde, text, log) zurück."""
    systems = ["claude", "perplexity", "chatgpt"]
    last_doc = ""
    last_log = ""
    last_round = 0
    last_step = 0

    for r in range(1, total_rounds + 1):
        for i, s in enumerate(systems):
            doc_file = output_dir / f"runde_{r}_{s}.md"
            crit_file = output_dir / f"runde_{r}_{s}_kritik.md"
            if doc_file.exists() and crit_file.exists():
                last_doc = doc_file.read_text(encoding="utf-8")
                critique = crit_file.read_text(encoding="utf-8")
                last_log += f"\n[Runde {r} – {s.capitalize()}]\n{critique}\n"
                last_round = r
                last_step = i + 1
            else:
                # Resume ab hier
                resume_round = r
                resume_step = i
                if last_round == 0:
                    return 1, "", ""
                return (resume_round if resume_step > 0 else resume_round,
                        last_doc, last_log)

    # Alles vorhanden
    return total_rounds + 1, last_doc, last_log


# ---------------------------------------------------------------------------
# Hauptloop
# ---------------------------------------------------------------------------

def run_debate(input_text: str, rounds: int, output_dir: Path,
               claude_model: str, openai_model: str, perplexity_model: str,
               resume: bool, verbose: bool,
               auto_stop: bool = True, min_rounds: int = 2,
               convergence_threshold: int = 70,
               on_convergence=None) -> tuple[str, str, int, str | None]:
    """Führt den Round-Robin-Debattenprozess durch.

    Args:
        auto_stop: Automatisch stoppen bei Konvergenz.
        min_rounds: Mindestanzahl Runden bevor Auto-Stop greifen kann.
        convergence_threshold: Confidence-Schwelle (0-100) für Auto-Stop.
        on_convergence: Optionaler Callback (should_stop, confidence, reason, round_num).

    Returns: (text, full_log, rounds_completed, stop_reason)
        stop_reason ist None wenn alle Runden durchlaufen wurden.
    """

    text = input_text
    full_log = ""
    start_round = 1
    start_step = 0  # 0=claude, 1=perplexity, 2=chatgpt

    if resume and output_dir.exists():
        resume_info = find_resume_point(output_dir, rounds)
        start_round_calc, resumed_text, resumed_log = resume_info
        if resumed_text:
            text = resumed_text
            full_log = resumed_log
            start_round = start_round_calc
            console.print(f"[green]Fortgesetzt ab Runde {start_round}[/green]")

    steps = [
        ("Claude", call_claude, claude_model, "bold blue"),
        ("Perplexity", call_perplexity, perplexity_model, "bold cyan"),
        ("ChatGPT", call_chatgpt, openai_model, "bold green"),
    ]

    rounds_completed = 0

    for r in range(start_round, rounds + 1):
        console.print(Panel(f"Runde {r}/{rounds}", style="bold magenta"))

        critique_for_round = compress_critique_log(full_log)
        doc_before_round = text
        round_critiques = ""

        for i, (name, func, model, style) in enumerate(steps):
            if r == start_round and i < start_step:
                continue

            with Progress(
                SpinnerColumn(),
                TextColumn(f"[{style}]{name}[/{style}] arbeitet..."),
                console=console,
            ) as progress:
                progress.add_task("", total=None)
                raw = func(text, critique_for_round, model)

            doc, critique = parse_structured_output(raw)
            text = doc

            full_log += f"\n[Runde {r} – {name}]\n{critique}\n"
            round_critiques += f"[{name}]\n{critique}\n\n"

            save_intermediate(output_dir, r, name.lower(), doc, critique)

            if verbose:
                console.print(f"  [{style}]{name} Kritikpunkte:[/{style}]")
                for line in critique.split("\n")[:5]:
                    console.print(f"    {line}")
                if critique.count("\n") > 5:
                    console.print(f"    ... ({critique.count(chr(10)) - 5} weitere)")

            console.print(f"  [{style}]{name}[/{style}] [green]fertig[/green]")

        rounds_completed = r

        # --- Konvergenz-Check nach jeder abgeschlossenen Runde ---
        if auto_stop and r >= min_rounds and r < rounds:
            console.print(f"  [dim]Konvergenz-Check...[/dim]")

            try:
                should_stop, confidence, reason = call_convergence_check(
                    doc_before_round, text, round_critiques, r, claude_model,
                )

                if on_convergence:
                    on_convergence(should_stop, confidence, reason, r)

                if verbose:
                    verdict = "STOP" if should_stop else "CONTINUE"
                    console.print(
                        f"  [dim]Verdict: {verdict} (Confidence: {confidence}%) "
                        f"– {reason}[/dim]"
                    )

                if should_stop and confidence >= convergence_threshold:
                    console.print(
                        f"\n[bold yellow]Auto-Stop nach Runde {r}: "
                        f"Konvergenz erkannt (Confidence: {confidence}%)[/bold yellow]"
                    )
                    console.print(f"  [yellow]{reason}[/yellow]")
                    return text, full_log, rounds_completed, reason

            except Exception as e:
                # Konvergenz-Check-Fehler stoppen nicht die Debatte
                console.print(f"  [dim yellow]Konvergenz-Check fehlgeschlagen: {e}[/dim yellow]")

    return text, full_log, rounds_completed, None


def final_synthesis(text: str, full_log: str, claude_model: str, verbose: bool) -> str:
    """Erstellt das finale Dokument mit Dissens-Register."""
    console.print(Panel("Finale Synthese", style="bold yellow"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold yellow]Erstelle finales Dokument + Dissens-Register...[/bold yellow]"),
        console=console,
    ) as progress:
        progress.add_task("", total=None)
        result = call_synthesis(text, full_log, claude_model)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def check_api_keys():
    missing = []
    for key in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PERPLEXITY_API_KEY"):
        if not os.environ.get(key):
            missing.append(key)
    if missing:
        console.print(f"[red]Fehlende API-Keys: {', '.join(missing)}[/red]")
        console.print("Setze sie als Umgebungsvariablen oder in einer .env-Datei.")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Strategy Debate – Multi-KI-Dokumentenoptimierung",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Beispiel:\n  python strategy_debate.py --input strategie.md --rounds 4 --output ergebnis.md",
    )
    parser.add_argument("--input", required=True, help="Eingabedokument (Markdown/Text)")
    parser.add_argument("--rounds", type=int, default=4, help="Max. Anzahl Runden (Standard: 4)")
    parser.add_argument("--output", required=True, help="Ausgabedatei für finales Dokument")
    parser.add_argument("--output-dir", default="debate_output", help="Verzeichnis für Zwischendateien")
    parser.add_argument("--resume", action="store_true", help="Fortsetzen ab letzter erfolgreicher Stelle")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Konsolenausgabe")
    parser.add_argument("--no-auto-stop", action="store_true", help="Konvergenz-Erkennung deaktivieren")
    parser.add_argument("--min-rounds", type=int, default=2, help="Mindestrunden vor Auto-Stop (Standard: 2)")
    parser.add_argument("--convergence-threshold", type=int, default=70,
                        help="Confidence-Schwelle für Auto-Stop, 0-100 (Standard: 70)")
    parser.add_argument("--claude-model", default="claude-sonnet-4-20250514", help="Claude-Modell")
    parser.add_argument("--openai-model", default="gpt-4o", help="ChatGPT-Modell")
    parser.add_argument("--perplexity-model", default="sonar-pro", help="Perplexity-Modell")
    return parser.parse_args()


def main():
    args = parse_args()
    check_api_keys()

    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"[red]Datei nicht gefunden: {args.input}[/red]")
        sys.exit(1)

    input_text = input_path.read_text(encoding="utf-8")
    output_dir = Path(args.output_dir)

    auto_stop = not args.no_auto_stop

    console.print(Panel(
        f"[bold]Strategy Debate[/bold]\n"
        f"Input: {args.input}\n"
        f"Max. Runden: {args.rounds}\n"
        f"Auto-Stop: {'Ja (Threshold: {0}%, Min. Runden: {1})'.format(args.convergence_threshold, args.min_rounds) if auto_stop else 'Nein'}\n"
        f"Modelle: Claude={args.claude_model}, ChatGPT={args.openai_model}, Perplexity={args.perplexity_model}",
        title="Konfiguration",
        style="bold white",
    ))

    text, full_log, rounds_completed, stop_reason = run_debate(
        input_text=input_text,
        rounds=args.rounds,
        output_dir=output_dir,
        claude_model=args.claude_model,
        openai_model=args.openai_model,
        perplexity_model=args.perplexity_model,
        resume=args.resume,
        verbose=args.verbose,
        auto_stop=auto_stop,
        min_rounds=args.min_rounds,
        convergence_threshold=args.convergence_threshold,
    )

    result = final_synthesis(text, full_log, args.claude_model, args.verbose)

    Path(args.output).write_text(result, encoding="utf-8")
    console.print(f"\n[bold green]Fertig! Ergebnis: {args.output}[/bold green]")
    if stop_reason:
        console.print(f"[yellow]Konvergenz nach {rounds_completed}/{args.rounds} Runden: {stop_reason}[/yellow]")
    else:
        console.print(f"[dim]Alle {rounds_completed} Runden durchlaufen[/dim]")
    console.print(f"[dim]Zwischendateien: {output_dir}/[/dim]")


if __name__ == "__main__":
    main()
