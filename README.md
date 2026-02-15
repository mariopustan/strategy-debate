# Strategy Debate

Automatisierte Multi-KI-Dokumentenoptimierung: Lässt Strategiedokumente in mehreren Runden durch **Claude**, **Perplexity** und **ChatGPT** rotieren.

## Setup

```bash
pip install -r requirements.txt
```

API-Keys als Umgebungsvariablen setzen (oder in `.env`-Datei):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export PERPLEXITY_API_KEY="pplx-..."
```

## Verwendung

```bash
python strategy_debate.py --input mein_dokument.md --rounds 4 --output ergebnis.md
```

### Optionen

| Flag | Standard | Beschreibung |
|------|----------|-------------|
| `--input` | (pflicht) | Eingabedokument (Markdown/Text) |
| `--output` | (pflicht) | Ausgabedatei |
| `--rounds` | 4 | Anzahl Durchläufe |
| `--output-dir` | `debate_output/` | Verzeichnis für Zwischendateien |
| `--resume` | - | Bei Abbruch fortsetzen |
| `--verbose` | - | Ausführliche Ausgabe |
| `--claude-model` | `claude-sonnet-4-20250514` | Claude-Modell |
| `--openai-model` | `gpt-4o` | ChatGPT-Modell |
| `--perplexity-model` | `sonar-pro` | Perplexity-Modell |

## Ablauf

Jede Runde durchläuft drei Stationen:

1. **Claude** – Kritischer Review: logische Lücken, Annahmen, Widersprüche
2. **Perplexity** – Faktencheck: aktuelle Daten, Trends, Fallstricke
3. **ChatGPT** – Synthese: Struktur, Argumentationslinie, Klarheit

Nach allen Runden erstellt Claude eine **finale Synthese** mit einem **Dissens-Register**, das nicht kompromissfähige Positionen ausweist.

## LOCKED-Blöcke

Inhalte, die nicht verändert werden dürfen, so markieren:

```markdown
<!-- LOCKED_START -->
Dieser Text darf nicht inhaltlich verändert werden.
<!-- LOCKED_END -->
```

## Docker

Image bauen und ausführen:

```bash
docker build -t strategy-debate .

docker run --rm \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  -e PERPLEXITY_API_KEY="pplx-..." \
  -v $(pwd)/dokumente:/data \
  strategy-debate \
  --input /data/mein_dokument.md --rounds 4 --output /data/ergebnis.md
```

Die Keys können auch über eine `.env`-Datei übergeben werden:

```bash
docker run --rm --env-file .env -v $(pwd)/dokumente:/data \
  strategy-debate --input /data/mein_dokument.md --rounds 4 --output /data/ergebnis.md
```

## Ausgabe

- `ergebnis.md` – Finales Dokument mit Dissens-Register
- `debate_output/` – Zwischendateien jeder Runde pro System
