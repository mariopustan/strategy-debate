#!/usr/bin/env python3
"""
Maure's Strategie Club – Web-Oberfläche
Streamlit-App für die Multi-KI-Dokumentenoptimierung.
"""

import os
import re
import time
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Maure's Strategie Club",
    page_icon="🏛️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600&display=swap');

    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        padding-top: 1rem;
    }
    .sub-header {
        font-family: 'Inter', sans-serif;
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-top: -0.5rem;
        margin-bottom: 2rem;
    }
    .step-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-claude { background: #dbeafe; color: #1e40af; }
    .badge-perplexity { background: #cffafe; color: #0e7490; }
    .badge-chatgpt { background: #dcfce7; color: #166534; }
    .badge-synthesis { background: #fef3c7; color: #92400e; }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1a1a2e, #0f3460, #e94560);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown('<div class="main-header">Maure\'s Strategie Club</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Drei KI-Systeme. Mehrere Runden. Ein Strategiedokument.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API-Key Check
# ---------------------------------------------------------------------------

missing_keys = [k for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PERPLEXITY_API_KEY") if not os.environ.get(k)]
if missing_keys:
    st.error(f"Fehlende API-Keys: {', '.join(missing_keys)}. Bitte als Umgebungsvariablen oder in .env setzen.")
    st.stop()

# ---------------------------------------------------------------------------
# Import debate engine (lazy, nach Key-Check)
# ---------------------------------------------------------------------------

from strategy_debate import (
    call_claude, call_perplexity, call_chatgpt, call_synthesis,
    parse_structured_output, compress_critique_log, save_intermediate,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Einstellungen")
    rounds = st.slider("Anzahl Runden", min_value=1, max_value=8, value=4)
    st.markdown("---")
    st.markdown("### Modelle")
    claude_model = st.text_input("Claude", value="claude-sonnet-4-20250514")
    openai_model = st.text_input("ChatGPT", value="gpt-4o")
    perplexity_model = st.text_input("Perplexity", value="sonar-pro")
    st.markdown("---")
    st.markdown(
        "<small style='color:#999'>Maure's Strategie Club v1.0<br>"
        "Claude + Perplexity + ChatGPT</small>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Input: Prompt oder Dokument
# ---------------------------------------------------------------------------

tab_prompt, tab_upload = st.tabs(["Idee / Prompt eingeben", "Dokument hochladen"])

input_text = None

with tab_prompt:
    prompt_text = st.text_area(
        "Beschreibe deine Strategie-Idee oder stelle eine Frage:",
        height=250,
        placeholder="z.B.: Entwickle eine Go-to-Market-Strategie für ein SaaS-Produkt im Bereich Compliance-Management für den deutschen Mittelstand...",
    )
    if prompt_text.strip():
        input_text = prompt_text.strip()

with tab_upload:
    uploaded_file = st.file_uploader(
        "Markdown- oder Textdatei hochladen",
        type=["md", "txt", "markdown"],
    )
    if uploaded_file is not None:
        input_text = uploaded_file.read().decode("utf-8")
        st.markdown("**Vorschau:**")
        with st.expander("Dokument anzeigen", expanded=False):
            st.markdown(input_text)

# ---------------------------------------------------------------------------
# Start
# ---------------------------------------------------------------------------

if st.button("Debatte starten", type="primary", disabled=input_text is None, use_container_width=True):

    session_id = uuid.uuid4().hex[:8]
    output_dir = Path(f"/tmp/debate_{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    text = input_text
    full_log = ""

    # Progress
    total_steps = rounds * 3 + 1  # +1 for synthesis
    progress_bar = st.progress(0.0)
    status_text = st.empty()
    step_count = 0

    # Expander für Kritik-Details
    critique_container = st.container()

    steps = [
        ("Claude", "badge-claude", call_claude, claude_model),
        ("Perplexity", "badge-perplexity", call_perplexity, perplexity_model),
        ("ChatGPT", "badge-chatgpt", call_chatgpt, openai_model),
    ]

    for r in range(1, rounds + 1):
        critique_for_round = compress_critique_log(full_log)

        for name, badge_class, func, model in steps:
            step_count += 1
            status_text.markdown(
                f'<span class="step-badge {badge_class}">{name}</span> '
                f'Runde {r}/{rounds} – arbeitet...',
                unsafe_allow_html=True,
            )
            progress_bar.progress(step_count / total_steps)

            try:
                raw = func(text, critique_for_round, model)
                doc, critique = parse_structured_output(raw)
                text = doc
                full_log += f"\n[Runde {r} – {name}]\n{critique}\n"
                save_intermediate(output_dir, r, name.lower(), doc, critique)

                with critique_container.expander(f"Runde {r} – {name}", expanded=False):
                    st.markdown(critique)

            except Exception as e:
                st.error(f"Fehler bei {name} (Runde {r}): {e}")
                st.stop()

    # Finale Synthese
    step_count += 1
    status_text.markdown(
        '<span class="step-badge badge-synthesis">Synthese</span> '
        'Erstelle finales Dokument + Dissens-Register...',
        unsafe_allow_html=True,
    )
    progress_bar.progress(step_count / total_steps)

    try:
        result = call_synthesis(text, full_log, claude_model)
    except Exception as e:
        st.error(f"Fehler bei der Synthese: {e}")
        st.stop()

    progress_bar.progress(1.0)
    status_text.markdown("**Fertig!**")

    # ---------------------------------------------------------------------------
    # Ergebnis
    # ---------------------------------------------------------------------------

    st.markdown("---")
    st.markdown("## Ergebnis")

    st.markdown(result)

    # Download
    st.download_button(
        label="Ergebnis als Markdown herunterladen",
        data=result,
        file_name="strategie_ergebnis.md",
        mime="text/markdown",
        use_container_width=True,
    )

    # Vollständiger Kritik-Verlauf
    with st.expander("Vollständiger Kritik-Verlauf"):
        st.text(full_log)
