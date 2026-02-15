#!/usr/bin/env python3
"""
Maure's Strategie Club – Web-Oberfläche
Streamlit-App für die Multi-KI-Dokumentenoptimierung.
Production-ready UI/UX mit Premium Think-Tank Aesthetic.
"""

import base64
import hashlib
import io
import os
import uuid
from pathlib import Path

import qrcode
import qrcode.constants
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Maure's Strategie Club",
    page_icon="https://em-content.zobj.net/source/apple/391/classical-building_1f3db-fe0f.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

# Passkey hash (SHA-256). Set MSC_PASSKEY_HASH env var or default to hash of "maure2024"
_DEFAULT_HASH = hashlib.sha256("maure2024".encode()).hexdigest()
PASSKEY_HASH = os.environ.get("MSC_PASSKEY_HASH", _DEFAULT_HASH)


def _check_auth():
    """Returns True if the user is authenticated."""
    return st.session_state.get("authenticated", False)


def _generate_qr_code(url: str) -> str:
    """Generate a QR code as base64-encoded PNG."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#c9952d", back_color="#111827")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _show_login():
    """Renders a centered login screen with QR code."""
    # Build the app URL for the QR code
    app_url = os.environ.get("MSC_APP_URL", "https://msc.demo-itw.de")
    qr_b64 = _generate_qr_code(app_url)

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        .stApp {
            background: linear-gradient(180deg, #080c18 0%, #0a0f1e 20%, #0d1425 100%) !important;
        }
        .stApp > header { background: transparent !important; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* Hide sidebar on login */
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }

        /* ── Login Card ── */
        .login-card {
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 20px;
            padding: 2.5rem 2.5rem 2rem 2.5rem;
            max-width: 420px;
            margin: 0 auto;
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.4),
                        0 0 80px rgba(201, 149, 45, 0.03);
        }

        /* Branding */
        .login-branding {
            text-align: center;
            margin-bottom: 1.8rem;
        }

        .login-ornament {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 1.2rem;
            opacity: 0.6;
        }

        .login-ornament .line {
            width: 40px;
            height: 1px;
            background: linear-gradient(90deg, transparent, #c9952d, transparent);
        }

        .login-ornament .diamond {
            width: 6px;
            height: 6px;
            background: #c9952d;
            transform: rotate(45deg);
        }

        .login-title {
            font-family: 'Lora', Georgia, serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8f9fc;
            letter-spacing: 0.02em;
            line-height: 1.2;
        }

        .login-title .accent {
            background: linear-gradient(135deg, #c9952d 0%, #dfbc5e 50%, #c9952d 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 6s ease-in-out infinite;
        }

        @keyframes shimmer {
            0%, 100% { background-position: 0% center; }
            50% { background-position: 200% center; }
        }

        .login-tagline {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.85rem;
            color: #7b92b2;
            margin-top: 0.3rem;
        }

        /* QR section */
        .qr-section {
            text-align: center;
            margin: 1.5rem 0;
        }

        .qr-wrapper {
            display: inline-block;
            background: #111827;
            border: 2px solid #1e293b;
            border-radius: 16px;
            padding: 12px;
            position: relative;
            transition: border-color 0.3s ease;
        }

        .qr-wrapper:hover {
            border-color: #c9952d40;
        }

        .qr-wrapper img {
            display: block;
            border-radius: 8px;
            width: 180px;
            height: 180px;
        }

        .qr-label {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            color: #4a6085;
            margin-top: 0.8rem;
            letter-spacing: 0.03em;
        }

        .qr-label strong {
            color: #7b92b2;
        }

        /* Divider */
        .login-divider {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1.5rem 0;
        }

        .login-divider .line {
            flex: 1;
            height: 1px;
            background: #1e293b;
        }

        .login-divider .text {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.72rem;
            color: #4a6085;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        /* Field label */
        .login-field-label {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            color: #b0c1d8;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        /* Error */
        .login-error {
            text-align: center;
            font-family: 'Source Sans 3', sans-serif;
            color: #f87171;
            font-size: 0.85rem;
            margin-top: 0.6rem;
            padding: 0.5rem 1rem;
            background: rgba(248, 113, 113, 0.06);
            border: 1px solid rgba(248, 113, 113, 0.15);
            border-radius: 10px;
        }

        /* Footer */
        .login-footer {
            text-align: center;
            margin-top: 1.8rem;
            padding-top: 1.2rem;
            border-top: 1px solid #1e293b;
        }

        .login-footer-brand {
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.72rem;
            color: #2e4066;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        /* Input styling */
        .stTextInput input {
            background: #0d1425 !important;
            border: 1px solid #243352 !important;
            border-radius: 10px !important;
            color: #f8f9fc !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 0.7rem 1rem !important;
        }

        .stTextInput input:focus {
            border-color: #c9952d !important;
            box-shadow: 0 0 0 2px rgba(201, 149, 45, 0.15) !important;
        }

        .stTextInput input::placeholder {
            color: #4a6085 !important;
        }

        /* Button styling */
        .stButton > button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #c9952d 0%, #d4a843 100%) !important;
            color: #0a0f1e !important;
            font-family: 'Source Sans 3', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.03em;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.65rem 2rem !important;
            box-shadow: 0 4px 15px rgba(201, 149, 45, 0.2) !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button[data-testid="stBaseButton-primary"]:hover {
            background: linear-gradient(135deg, #d4a843 0%, #dfbc5e 100%) !important;
            box-shadow: 0 6px 25px rgba(201, 149, 45, 0.35) !important;
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout
    _, col, _ = st.columns([1.2, 1.6, 1.2])

    with col:
        # Vertical spacer
        st.markdown('<div style="height: 8vh;"></div>', unsafe_allow_html=True)

        # Login card (HTML part)
        st.markdown(f'''
        <div class="login-card">
            <!-- Branding -->
            <div class="login-branding">
                <div class="login-ornament">
                    <div class="line"></div>
                    <div class="diamond"></div>
                    <div class="line"></div>
                </div>
                <div class="login-title">
                    Maure's <span class="accent">Strategie Club</span>
                </div>
                <div class="login-tagline">Multi-AI Strategy Debate Platform</div>
            </div>

            <!-- QR Code -->
            <div class="qr-section">
                <div class="qr-wrapper">
                    <img src="data:image/png;base64,{qr_b64}" alt="QR Code" />
                </div>
                <div class="qr-label">
                    <strong>QR-Code scannen</strong> um die App auf dem Handy zu öffnen
                </div>
            </div>

            <!-- Divider -->
            <div class="login-divider">
                <div class="line"></div>
                <div class="text">Passkey eingeben</div>
                <div class="line"></div>
            </div>

            <!-- Label -->
            <div class="login-field-label">Passkey</div>
        </div>
        ''', unsafe_allow_html=True)

        # Streamlit widgets (rendered right after the card HTML)
        passkey = st.text_input(
            "Passkey",
            type="password",
            placeholder="Passkey eingeben...",
            label_visibility="collapsed",
        )

        login_clicked = st.button("Anmelden", type="primary", use_container_width=True)

        if login_clicked:
            if hashlib.sha256(passkey.encode()).hexdigest() == PASSKEY_HASH:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.markdown(
                    '<div class="login-error">Falscher Passkey. Bitte erneut versuchen.</div>',
                    unsafe_allow_html=True,
                )

        # Footer
        st.markdown('''
        <div class="login-footer">
            <div class="login-footer-brand">
                &copy; 2024 IT Warehouse AG &middot; Powered by Claude &middot; Perplexity &middot; ChatGPT
            </div>
        </div>
        ''', unsafe_allow_html=True)


if not _check_auth():
    _show_login()
    st.stop()

# ---------------------------------------------------------------------------
# Design Tokens & CSS
# ---------------------------------------------------------------------------

# Color palette
NAVY_900 = "#0a0f1e"
NAVY_800 = "#0f1628"
NAVY_700 = "#141d35"
NAVY_600 = "#1a2744"
NAVY_500 = "#243352"
NAVY_400 = "#2e4066"
NAVY_300 = "#4a6085"
NAVY_200 = "#7b92b2"
NAVY_100 = "#b0c1d8"
GOLD_500 = "#c9952d"
GOLD_400 = "#d4a843"
GOLD_300 = "#dfbc5e"
GOLD_200 = "#e8cf87"
GOLD_100 = "#f3e4b5"
WHITE = "#f8f9fc"
TEXT_BODY = "#d1d5e0"
TEXT_MUTED = "#8892a6"
SURFACE = "#111827"
SURFACE_RAISED = "#1a2235"
BORDER = "#1e293b"

# AI system colors
CLAUDE_BG = "#1e3a5f"
CLAUDE_BORDER = "#2563eb"
CLAUDE_TEXT = "#93c5fd"
PERPLEXITY_BG = "#134e4a"
PERPLEXITY_BORDER = "#14b8a6"
PERPLEXITY_TEXT = "#5eead4"
CHATGPT_BG = "#14532d"
CHATGPT_BORDER = "#22c55e"
CHATGPT_TEXT = "#86efac"
SYNTHESIS_BG = "#451a03"
SYNTHESIS_BORDER = "#d97706"
SYNTHESIS_TEXT = "#fcd34d"

st.markdown("""
<style>
    /* ================================================================
       FONTS
       ================================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ================================================================
       GLOBAL OVERRIDES
       ================================================================ */
    .stApp {
        background: linear-gradient(180deg, #080c18 0%, #0a0f1e 20%, #0d1425 100%);
        color: #d1d5e0;
    }

    .stApp > header {
        background: transparent !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0f1e; }
    ::-webkit-scrollbar-thumb { background: #243352; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #2e4066; }

    /* ================================================================
       SIDEBAR
       ================================================================ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1425 0%, #0f1628 100%) !important;
        border-right: 1px solid #1e293b !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        font-family: 'Lora', Georgia, serif !important;
        color: #c9952d !important;
        letter-spacing: 0.03em;
    }

    section[data-testid="stSidebar"] label {
        font-family: 'Source Sans 3', -apple-system, sans-serif !important;
        color: #8892a6 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    section[data-testid="stSidebar"] .stSlider > div > div > div {
        color: #c9952d !important;
    }

    section[data-testid="stSidebar"] .stTextInput input {
        background: #141d35 !important;
        border: 1px solid #243352 !important;
        color: #d1d5e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        border-radius: 8px !important;
    }

    section[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #c9952d !important;
        box-shadow: 0 0 0 1px rgba(201, 149, 45, 0.3) !important;
    }

    /* ================================================================
       HERO SECTION
       ================================================================ */
    .hero-wrapper {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
        margin-bottom: 0.5rem;
        position: relative;
        overflow: hidden;
    }

    .hero-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            ellipse at 50% 50%,
            rgba(201, 149, 45, 0.04) 0%,
            transparent 60%
        );
        animation: hero-glow 8s ease-in-out infinite alternate;
        pointer-events: none;
    }

    @keyframes hero-glow {
        0% { opacity: 0.4; transform: scale(1); }
        100% { opacity: 1; transform: scale(1.1); }
    }

    .hero-ornament {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .hero-ornament .line {
        width: 60px;
        height: 1px;
        background: linear-gradient(90deg, transparent, #c9952d, transparent);
    }

    .hero-ornament .diamond {
        width: 6px;
        height: 6px;
        background: #c9952d;
        transform: rotate(45deg);
    }

    .hero-title {
        font-family: 'Lora', Georgia, serif;
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 700;
        color: #f8f9fc;
        letter-spacing: 0.02em;
        line-height: 1.15;
        margin: 0 0 0.4rem 0;
        position: relative;
    }

    .hero-title .accent {
        background: linear-gradient(135deg, #c9952d 0%, #dfbc5e 50%, #c9952d 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 6s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 200% center; }
    }

    .hero-subtitle {
        font-family: 'Source Sans 3', -apple-system, sans-serif;
        font-size: clamp(0.95rem, 2vw, 1.1rem);
        color: #8892a6;
        font-weight: 400;
        letter-spacing: 0.04em;
        margin: 0;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        margin-top: 1.2rem;
        padding: 0.35rem 1rem;
        background: rgba(201, 149, 45, 0.08);
        border: 1px solid rgba(201, 149, 45, 0.2);
        border-radius: 100px;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: #d4a843;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .hero-badge .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
        animation: pulse-dot 2s ease-in-out infinite;
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ================================================================
       DIVIDER
       ================================================================ */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #243352 30%, #c9952d40 50%, #243352 70%, transparent 100%);
        margin: 1rem 0 2rem 0;
    }

    /* ================================================================
       TABS
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #111827;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #1e293b;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 500;
        font-size: 0.9rem;
        color: #8892a6 !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #d1d5e0 !important;
        background: rgba(255,255,255,0.03) !important;
    }

    .stTabs [aria-selected="true"] {
        background: #1a2744 !important;
        color: #c9952d !important;
        border: 1px solid #243352 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ================================================================
       TEXT AREA
       ================================================================ */
    .stTextArea textarea {
        background: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #d1d5e0 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #c9952d !important;
        box-shadow: 0 0 0 1px rgba(201, 149, 45, 0.2), 0 4px 20px rgba(0,0,0,0.3) !important;
    }

    .stTextArea textarea::placeholder {
        color: #4a6085 !important;
        font-style: italic;
    }

    .stTextArea label {
        font-family: 'Source Sans 3', sans-serif !important;
        color: #b0c1d8 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    /* ================================================================
       FILE UPLOADER
       ================================================================ */
    .stFileUploader > div {
        background: #111827 !important;
        border: 2px dashed #243352 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }

    .stFileUploader > div:hover {
        border-color: #c9952d !important;
        background: rgba(201, 149, 45, 0.02) !important;
    }

    .stFileUploader label {
        font-family: 'Source Sans 3', sans-serif !important;
        color: #b0c1d8 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    /* ================================================================
       BUTTONS
       ================================================================ */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #c9952d 0%, #d4a843 100%) !important;
        color: #0a0f1e !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.03em;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(201, 149, 45, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #d4a843 0%, #dfbc5e 100%) !important;
        box-shadow: 0 6px 25px rgba(201, 149, 45, 0.35) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="stBaseButton-primary"]:active {
        transform: translateY(0);
    }

    .stButton > button[kind="primary"]:disabled,
    .stButton > button[data-testid="stBaseButton-primary"]:disabled {
        background: #243352 !important;
        color: #4a6085 !important;
        box-shadow: none !important;
        cursor: not-allowed;
    }

    /* Download button */
    .stDownloadButton > button {
        background: transparent !important;
        color: #c9952d !important;
        border: 1px solid #c9952d !important;
        border-radius: 12px !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        background: rgba(201, 149, 45, 0.1) !important;
        box-shadow: 0 4px 15px rgba(201, 149, 45, 0.15) !important;
    }

    /* ================================================================
       EXPANDERS
       ================================================================ */
    .streamlit-expanderHeader {
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        color: #b0c1d8 !important;
        background: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
    }

    .streamlit-expanderHeader:hover {
        color: #c9952d !important;
        border-color: #243352 !important;
    }

    .streamlit-expanderContent {
        background: #0d1425 !important;
        border: 1px solid #1e293b !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    details {
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
        background: #111827 !important;
        margin-bottom: 0.5rem;
    }

    details summary {
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 500 !important;
        color: #b0c1d8 !important;
        padding: 0.75rem 1rem !important;
    }

    details summary:hover {
        color: #c9952d !important;
    }

    details > div {
        background: #0d1425 !important;
        padding: 0.5rem 1rem !important;
    }

    /* ================================================================
       PROGRESS BAR
       ================================================================ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #c9952d, #dfbc5e, #c9952d) !important;
        background-size: 200% auto;
        animation: progress-shimmer 2s linear infinite;
        border-radius: 4px;
    }

    @keyframes progress-shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }

    .stProgress > div > div {
        background: #1a2744 !important;
        border-radius: 4px;
    }

    /* ================================================================
       TIMELINE / STEPPER
       ================================================================ */
    .debate-timeline {
        display: flex;
        align-items: center;
        gap: 0;
        margin: 1.5rem 0;
        padding: 0 0.5rem;
        overflow-x: auto;
    }

    .timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 80px;
        position: relative;
        flex-shrink: 0;
    }

    .timeline-node {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Source Sans 3', sans-serif;
        border: 2px solid;
        transition: all 0.3s ease;
        position: relative;
        z-index: 2;
    }

    .timeline-node.pending {
        background: #111827;
        border-color: #243352;
        color: #4a6085;
    }

    .timeline-node.active {
        border-color: #c9952d;
        background: rgba(201, 149, 45, 0.15);
        color: #c9952d;
        box-shadow: 0 0 15px rgba(201, 149, 45, 0.3);
        animation: node-pulse 1.5s ease-in-out infinite;
    }

    @keyframes node-pulse {
        0%, 100% { box-shadow: 0 0 10px rgba(201, 149, 45, 0.2); }
        50% { box-shadow: 0 0 20px rgba(201, 149, 45, 0.4); }
    }

    .timeline-node.done {
        background: #166534;
        border-color: #22c55e;
        color: #86efac;
    }

    .timeline-node.claude { border-color: #2563eb; background: rgba(37, 99, 235, 0.15); color: #93c5fd; }
    .timeline-node.claude.done { background: #1e3a5f; }
    .timeline-node.perplexity { border-color: #14b8a6; background: rgba(20, 184, 166, 0.15); color: #5eead4; }
    .timeline-node.perplexity.done { background: #134e4a; }
    .timeline-node.chatgpt { border-color: #22c55e; background: rgba(34, 197, 94, 0.15); color: #86efac; }
    .timeline-node.chatgpt.done { background: #14532d; }
    .timeline-node.synthesis { border-color: #d97706; background: rgba(217, 119, 6, 0.15); color: #fcd34d; }
    .timeline-node.synthesis.done { background: #451a03; }
    .timeline-node.convergence { border-color: #a855f7; background: rgba(168, 85, 247, 0.15); color: #c4b5fd; }
    .timeline-node.convergence.done { background: #3b0764; }

    .timeline-label {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.7rem;
        color: #8892a6;
        margin-top: 0.4rem;
        white-space: nowrap;
        text-align: center;
    }

    .timeline-connector {
        flex: 1;
        height: 2px;
        background: #243352;
        min-width: 20px;
        position: relative;
        top: -10px;
    }

    .timeline-connector.done {
        background: linear-gradient(90deg, #22c55e, #22c55e);
    }

    .timeline-connector.active {
        background: linear-gradient(90deg, #22c55e, #c9952d);
        animation: connector-flow 1s linear infinite;
    }

    @keyframes connector-flow {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }

    /* ================================================================
       STATUS CARDS
       ================================================================ */
    .status-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        font-family: 'Source Sans 3', sans-serif;
        transition: all 0.3s ease;
    }

    .status-card.working {
        border-color: #c9952d;
        background: linear-gradient(135deg, rgba(201, 149, 45, 0.05), rgba(201, 149, 45, 0.02));
        box-shadow: 0 4px 20px rgba(201, 149, 45, 0.08);
    }

    .status-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .status-icon.claude {
        background: rgba(37, 99, 235, 0.15);
        border: 1px solid rgba(37, 99, 235, 0.3);
        color: #93c5fd;
    }
    .status-icon.perplexity {
        background: rgba(20, 184, 166, 0.15);
        border: 1px solid rgba(20, 184, 166, 0.3);
        color: #5eead4;
    }
    .status-icon.chatgpt {
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #86efac;
    }
    .status-icon.synthesis {
        background: rgba(217, 119, 6, 0.15);
        border: 1px solid rgba(217, 119, 6, 0.3);
        color: #fcd34d;
    }

    .status-text {
        flex: 1;
    }

    .status-text .name {
        font-weight: 600;
        font-size: 0.95rem;
        color: #f8f9fc;
    }

    .status-text .detail {
        font-size: 0.82rem;
        color: #8892a6;
        margin-top: 0.15rem;
    }

    .status-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #243352;
        border-top-color: #c9952d;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .status-check {
        color: #22c55e;
        font-size: 1.2rem;
    }

    /* ================================================================
       CRITIQUE CARDS
       ================================================================ */
    .critique-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        margin-bottom: 0.6rem;
        overflow: hidden;
    }

    .critique-card-header {
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        transition: background 0.2s;
    }

    .critique-card-header:hover {
        background: rgba(255,255,255,0.02);
    }

    .critique-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.2rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Source Sans 3', sans-serif;
        letter-spacing: 0.02em;
    }

    .critique-badge.claude {
        background: rgba(37, 99, 235, 0.15);
        color: #93c5fd;
        border: 1px solid rgba(37, 99, 235, 0.25);
    }
    .critique-badge.perplexity {
        background: rgba(20, 184, 166, 0.15);
        color: #5eead4;
        border: 1px solid rgba(20, 184, 166, 0.25);
    }
    .critique-badge.chatgpt {
        background: rgba(34, 197, 94, 0.15);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.25);
    }
    .critique-badge.synthesis {
        background: rgba(217, 119, 6, 0.15);
        color: #fcd34d;
        border: 1px solid rgba(217, 119, 6, 0.25);
    }

    .critique-round {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.82rem;
        color: #8892a6;
    }

    /* ================================================================
       RESULT SECTION
       ================================================================ */
    .result-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .result-header h2 {
        font-family: 'Lora', Georgia, serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f8f9fc;
        margin: 0 0 0.3rem 0;
    }

    .result-header p {
        font-family: 'Source Sans 3', sans-serif;
        color: #8892a6;
        font-size: 0.95rem;
    }

    .result-document {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 2.5rem;
        margin: 1rem 0 1.5rem 0;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 1rem;
        line-height: 1.75;
        color: #d1d5e0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }

    .result-document h1, .result-document h2, .result-document h3,
    .result-document h4, .result-document h5, .result-document h6 {
        font-family: 'Lora', Georgia, serif !important;
        color: #f8f9fc !important;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }

    .result-document h1 { font-size: 1.8rem; border-bottom: 1px solid #1e293b; padding-bottom: 0.4em; }
    .result-document h2 { font-size: 1.5rem; color: #c9952d !important; }
    .result-document h3 { font-size: 1.25rem; }

    .result-document p { margin-bottom: 1em; }

    .result-document ul, .result-document ol {
        padding-left: 1.5em;
        margin-bottom: 1em;
    }

    .result-document li { margin-bottom: 0.4em; }

    .result-document strong { color: #f8f9fc; }

    .result-document blockquote {
        border-left: 3px solid #c9952d;
        padding-left: 1rem;
        color: #b0c1d8;
        font-style: italic;
        margin: 1em 0;
    }

    .result-document code {
        background: #1a2744;
        padding: 0.15em 0.4em;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88em;
        color: #dfbc5e;
    }

    .result-document table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
    }

    .result-document th {
        background: #1a2744;
        color: #c9952d;
        padding: 0.6em 1em;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #243352;
    }

    .result-document td {
        padding: 0.5em 1em;
        border-bottom: 1px solid #1e293b;
    }

    /* ================================================================
       SUCCESS CELEBRATION
       ================================================================ */
    .success-banner {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(201, 149, 45, 0.08));
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 16px;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
    }

    .success-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 200%;
        height: 100%;
        background: linear-gradient(90deg,
            transparent,
            rgba(201, 149, 45, 0.05),
            transparent
        );
        animation: success-sweep 3s ease-in-out;
    }

    @keyframes success-sweep {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    .success-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .success-title {
        font-family: 'Lora', Georgia, serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8f9fc;
        margin-bottom: 0.3rem;
    }

    .success-detail {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem;
        color: #8892a6;
    }

    /* ================================================================
       EMPTY STATE
       ================================================================ */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #4a6085;
    }

    .empty-state .icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }

    .empty-state h3 {
        font-family: 'Lora', Georgia, serif;
        font-size: 1.4rem;
        color: #7b92b2;
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ================================================================
       FOOTER
       ================================================================ */
    .app-footer {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid #1e293b;
    }

    .footer-brand {
        font-family: 'Lora', Georgia, serif;
        font-size: 1.05rem;
        color: #4a6085;
        letter-spacing: 0.04em;
    }

    .footer-brand .gold {
        color: #c9952d;
    }

    .footer-sub {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.72rem;
        color: #2e4066;
        margin-top: 0.3rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* ================================================================
       MOBILE RESPONSIVE
       ================================================================ */
    @media (max-width: 768px) {
        .hero-title { font-size: 1.8rem; }
        .hero-subtitle { font-size: 0.9rem; }
        .debate-timeline { flex-wrap: wrap; justify-content: center; }
        .timeline-connector { display: none; }
        .result-document { padding: 1.5rem; }
        .status-card { flex-direction: column; text-align: center; }
    }

    /* ================================================================
       MISC STREAMLIT OVERRIDES
       ================================================================ */
    .stAlert {
        border-radius: 12px !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: #c9952d !important;
        border-color: #c9952d !important;
    }

    .stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
        color: #c9952d !important;
    }

    /* Metric value */
    [data-testid="stMetricValue"] {
        font-family: 'Lora', Georgia, serif !important;
        color: #c9952d !important;
    }

    /* Hide default Streamlit menu and footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Links */
    a { color: #d4a843 !important; }
    a:hover { color: #dfbc5e !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helper: Build timeline HTML
# ---------------------------------------------------------------------------

def build_timeline_html(rounds: int, current_round: int, current_step: int, total_done: bool = False) -> str:
    """
    Build the visual timeline/stepper.
    current_step: 0=Claude, 1=Perplexity, 2=ChatGPT per round; 3=Synthesis (final).
    Steps are numbered globally: round 1 has steps 0-2, round 2 has 3-5, etc.
    Last step (rounds*3) is synthesis.
    """
    systems = [
        ("C", "claude", "Claude"),
        ("P", "perplexity", "Perplexity"),
        ("G", "chatgpt", "ChatGPT"),
    ]

    # Calculate global step index for what is currently active
    if total_done:
        global_active = rounds * 3 + 1  # beyond everything
    elif current_step == 3:
        # Synthesis step
        global_active = rounds * 3
    else:
        global_active = (current_round - 1) * 3 + current_step

    html_parts = ['<div class="debate-timeline">']

    step_index = 0
    for r in range(1, rounds + 1):
        for i, (letter, cls, label) in enumerate(systems):
            # Determine state
            if step_index < global_active:
                state = f"{cls} done"
            elif step_index == global_active and not total_done:
                state = f"{cls} active"
            else:
                state = "pending"

            html_parts.append(f'''
                <div class="timeline-step">
                    <div class="timeline-node {state}">{letter}</div>
                    <div class="timeline-label">R{r}</div>
                </div>
            ''')

            # Connector (not after last step before synthesis)
            if step_index < rounds * 3:
                if step_index < global_active - 1:
                    conn_cls = "done"
                elif step_index == global_active - 1:
                    conn_cls = "active"
                else:
                    conn_cls = ""
                html_parts.append(f'<div class="timeline-connector {conn_cls}"></div>')

            step_index += 1

    # Synthesis node
    if total_done:
        synth_state = "synthesis done"
    elif current_step == 3:
        synth_state = "synthesis active"
    else:
        synth_state = "pending"

    html_parts.append(f'''
        <div class="timeline-step">
            <div class="timeline-node {synth_state}">S</div>
            <div class="timeline-label">Synthese</div>
        </div>
    ''')

    html_parts.append('</div>')
    return ''.join(html_parts)


def build_status_html(system_name: str, system_class: str, letter: str, round_num: int,
                      total_rounds: int, is_working: bool = True) -> str:
    """Build a status card for the currently working AI system."""
    spinner = '<div class="status-spinner"></div>' if is_working else '<span class="status-check">&#10003;</span>'
    detail = f"Runde {round_num} von {total_rounds}" if round_num > 0 else "Erstelle finales Dokument"
    working_cls = "working" if is_working else ""

    return f'''
    <div class="status-card {working_cls}">
        <div class="status-icon {system_class}">{letter}</div>
        <div class="status-text">
            <div class="name">{system_name} {'arbeitet...' if is_working else 'abgeschlossen'}</div>
            <div class="detail">{detail}</div>
        </div>
        {spinner}
    </div>
    '''

# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------

st.markdown('''
<div class="hero-wrapper">
    <div class="hero-ornament">
        <div class="line"></div>
        <div class="diamond"></div>
        <div class="line"></div>
    </div>
    <h1 class="hero-title">
        Maure's <span class="accent">Strategie Club</span>
    </h1>
    <p class="hero-subtitle">
        Drei KI-Systeme &middot; Mehrere Runden &middot; Ein Strategiedokument
    </p>
    <div class="hero-badge">
        <span class="dot"></span>
        Alle Systeme bereit
    </div>
</div>
<div class="section-divider"></div>
''', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# API-Key Check
# ---------------------------------------------------------------------------

missing_keys = [
    k for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "PERPLEXITY_API_KEY")
    if not os.environ.get(k)
]
if missing_keys:
    st.markdown(f'''
    <div style="
        background: rgba(220, 38, 38, 0.08);
        border: 1px solid rgba(220, 38, 38, 0.3);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        font-family: 'Source Sans 3', sans-serif;
        color: #fca5a5;
        font-size: 0.95rem;
    ">
        <strong style="color: #f87171;">Fehlende API-Schlüssel:</strong><br>
        {', '.join(missing_keys)}<br>
        <span style="color: #8892a6; font-size: 0.85rem;">
            Bitte als Umgebungsvariablen oder in einer .env-Datei konfigurieren.
        </span>
    </div>
    ''', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------------------
# Import debate engine (lazy, after key check)
# ---------------------------------------------------------------------------

from strategy_debate import (
    call_claude, call_perplexity, call_chatgpt, call_synthesis,
    call_convergence_check,
    parse_structured_output, compress_critique_log, save_intermediate,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('''
    <div style="
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 1.5rem;
    ">
        <div style="
            font-family: 'Lora', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 700;
            color: #f8f9fc;
            letter-spacing: 0.02em;
        ">Einstellungen</div>
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.72rem;
            color: #4a6085;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 0.25rem;
        ">Debattenparameter</div>
    </div>
    ''', unsafe_allow_html=True)

    # Round count
    st.markdown('''
    <div style="
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: #8892a6;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.3rem;
    ">Debattenrunden</div>
    ''', unsafe_allow_html=True)
    rounds = st.slider(
        "Anzahl Runden",
        min_value=1, max_value=8, value=4,
        label_visibility="collapsed",
        help="Mehr Runden ergeben tiefere Analyse, dauern aber länger.",
    )

    # Estimated time
    est_minutes = rounds * 3 * 0.5 + 0.5  # rough estimate: 30s per call + synthesis
    st.markdown(f'''
    <div style="
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: #4a6085;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    ">
        Geschätzte Dauer: ~{int(est_minutes)} Min.
    </div>
    ''', unsafe_allow_html=True)

    # Auto-Stop / Convergence detection
    st.markdown('''
    <div style="
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: #8892a6;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.3rem;
        padding-top: 0.5rem;
        border-top: 1px solid #1e293b;
    ">Konvergenz-Erkennung</div>
    ''', unsafe_allow_html=True)

    auto_stop = st.toggle(
        "Auto-Stop bei Konvergenz",
        value=True,
        help="Stoppt automatisch, wenn weitere Runden keinen Mehrwert mehr bringen.",
    )

    if auto_stop:
        convergence_threshold = st.slider(
            "Confidence-Schwelle",
            min_value=50, max_value=95, value=70, step=5,
            label_visibility="visible",
            help="Wie sicher muss die Erkennung sein? Höher = konservativer (läuft eher weiter).",
        )
        min_rounds = st.slider(
            "Mindestrunden",
            min_value=1, max_value=rounds, value=min(2, rounds),
            label_visibility="visible",
            help="So viele Runden laufen mindestens, bevor Auto-Stop greifen kann.",
        )
    else:
        convergence_threshold = 70
        min_rounds = 2

    # Model configuration in expander
    st.markdown('''
    <div style="
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        color: #8892a6;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #1e293b;
    ">KI-Modelle</div>
    ''', unsafe_allow_html=True)

    with st.expander("Modellkonfiguration", expanded=False):
        st.markdown('''
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            color: #4a6085;
            margin-bottom: 0.8rem;
            line-height: 1.5;
        ">Passe die verwendeten KI-Modelle an. Standard-Einstellungen
        sind für die meisten Anwendungsfälle optimal.</div>
        ''', unsafe_allow_html=True)

        claude_model = st.text_input(
            "Claude",
            value="claude-sonnet-4-20250514",
            help="Anthropic Claude Modell-ID",
        )
        chatgpt_model = st.text_input(
            "ChatGPT",
            value="gpt-4o",
            help="OpenAI ChatGPT Modell-ID",
        )
        perplexity_model = st.text_input(
            "Perplexity",
            value="sonar-pro",
            help="Perplexity Modell-ID",
        )

    # System status indicators
    st.markdown('''
    <div style="
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #1e293b;
    ">
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            color: #8892a6;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
            margin-bottom: 0.8rem;
        ">Systemstatus</div>
    </div>
    ''', unsafe_allow_html=True)

    for label, color, icon in [
        ("Claude", "#2563eb", "C"),
        ("Perplexity", "#14b8a6", "P"),
        ("ChatGPT", "#22c55e", "G"),
    ]:
        st.markdown(f'''
        <div style="
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 0.5rem;
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.82rem;
        ">
            <div style="
                width: 28px;
                height: 28px;
                border-radius: 8px;
                background: {color}20;
                border: 1px solid {color}40;
                display: flex;
                align-items: center;
                justify-content: center;
                color: {color};
                font-weight: 700;
                font-size: 0.7rem;
            ">{icon}</div>
            <span style="color: #b0c1d8;">{label}</span>
            <span style="
                margin-left: auto;
                width: 7px;
                height: 7px;
                border-radius: 50%;
                background: #22c55e;
                box-shadow: 0 0 6px rgba(34,197,94,0.4);
            "></span>
        </div>
        ''', unsafe_allow_html=True)

    # Logout button
    st.markdown('''
    <div style="
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #1e293b;
    "></div>
    ''', unsafe_allow_html=True)

    if st.button("Abmelden", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    # Footer
    st.markdown('''
    <div style="
        text-align: center;
        margin-top: 1rem;
    ">
        <div style="
            font-family: 'Lora', Georgia, serif;
            font-size: 0.9rem;
            color: #4a6085;
        ">Maure's <span style="color: #c9952d;">Strategie Club</span></div>
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.65rem;
            color: #2e4066;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 0.2rem;
        ">v2.0 &middot; Premium Edition</div>
    </div>
    ''', unsafe_allow_html=True)

# Ensure model variables exist even if expander was never opened
if 'claude_model' not in dir():
    claude_model = "claude-sonnet-4-20250514"
if 'chatgpt_model' not in dir():
    chatgpt_model = "gpt-4o"
if 'perplexity_model' not in dir():
    perplexity_model = "sonar-pro"

# ---------------------------------------------------------------------------
# Main Content: Input Tabs
# ---------------------------------------------------------------------------

# Container for input section
input_col_l, input_col_main, input_col_r = st.columns([0.5, 5, 0.5])

with input_col_main:
    tab_prompt, tab_upload = st.tabs(["Idee eingeben", "Dokument hochladen"])

    input_text = None

    with tab_prompt:
        st.markdown('''
        <div style="
            font-family: 'Lora', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: #f8f9fc;
            margin-bottom: 0.2rem;
            margin-top: 0.5rem;
        ">Ihre Strategie-Idee</div>
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.85rem;
            color: #8892a6;
            margin-bottom: 1rem;
            line-height: 1.5;
        ">Beschreiben Sie Ihre Strategie, Geschäftsidee oder Fragestellung.
        Die drei KI-Systeme werden Ihren Text analysieren, kritisieren und
        systematisch verbessern.</div>
        ''', unsafe_allow_html=True)

        prompt_text = st.text_area(
            "Strategie-Idee oder Fragestellung",
            height=220,
            placeholder="z.B.: Entwickle eine Go-to-Market-Strategie für ein SaaS-Produkt "
                        "im Bereich Compliance-Management für den deutschen Mittelstand...",
            label_visibility="collapsed",
        )
        if prompt_text.strip():
            input_text = prompt_text.strip()

    with tab_upload:
        st.markdown('''
        <div style="
            font-family: 'Lora', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 600;
            color: #f8f9fc;
            margin-bottom: 0.2rem;
            margin-top: 0.5rem;
        ">Dokument hochladen</div>
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.85rem;
            color: #8892a6;
            margin-bottom: 1rem;
            line-height: 1.5;
        ">Laden Sie ein bestehendes Strategiedokument hoch.
        Unterstützte Formate: Markdown (.md) und Text (.txt).</div>
        ''', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Dokument hochladen",
            type=["md", "txt", "markdown"],
            label_visibility="collapsed",
        )

        # Supplementary text for uploaded documents
        st.markdown('''
        <div style="
            font-family: 'Lora', Georgia, serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #f8f9fc;
            margin-top: 1.2rem;
            margin-bottom: 0.2rem;
        ">Ergänzende Hinweise</div>
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.85rem;
            color: #8892a6;
            margin-bottom: 0.8rem;
            line-height: 1.5;
        ">Optional: Geben Sie den KI-Systemen zusätzlichen Kontext,
        Schwerpunkte oder spezifische Fragen mit.</div>
        ''', unsafe_allow_html=True)

        supplement_text = st.text_area(
            "Ergänzende Hinweise",
            height=120,
            placeholder="z.B.: Fokus auf den deutschen Markt. Bitte besonders die "
                        "Wettbewerbsanalyse und die Preisgestaltung kritisch prüfen...",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")
            # Combine document with supplementary instructions
            if supplement_text.strip():
                input_text = (
                    f"{file_content}\n\n"
                    f"---\n\n"
                    f"**Ergänzende Hinweise des Autors:**\n{supplement_text.strip()}"
                )
            else:
                input_text = file_content
            st.markdown(f'''
            <div style="
                display: flex;
                align-items: center;
                gap: 0.6rem;
                padding: 0.6rem 1rem;
                background: rgba(34, 197, 94, 0.06);
                border: 1px solid rgba(34, 197, 94, 0.15);
                border-radius: 10px;
                margin-bottom: 0.8rem;
                font-family: 'Source Sans 3', sans-serif;
                font-size: 0.85rem;
                color: #86efac;
            ">
                <span style="font-size: 1rem;">&#10003;</span>
                <span>{uploaded_file.name} erfolgreich geladen ({len(file_content):,} Zeichen)</span>
            </div>
            ''', unsafe_allow_html=True)
            with st.expander("Dokumentvorschau", expanded=False):
                st.markdown(file_content)

    # Empty state hint (when no input)
    if input_text is None:
        st.markdown('''
        <div class="empty-state">
            <div class="icon">&#9997;</div>
            <h3>Bereit für Ihre Strategie</h3>
            <p>Geben Sie oben eine Idee ein oder laden Sie ein Dokument hoch,
            um die KI-Debatte zu starten.</p>
        </div>
        ''', unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # Start Button
    # ---------------------------------------------------------------------------

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    start_debate = st.button(
        "Debatte starten",
        type="primary",
        disabled=input_text is None,
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# Debate Execution
# ---------------------------------------------------------------------------

if start_debate and input_text is not None:

    session_id = uuid.uuid4().hex[:8]
    output_dir = Path(f"/tmp/debate_{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    text = input_text
    full_log = ""

    # Total steps for progress
    total_steps = rounds * 3 + 1  # 3 systems per round + 1 synthesis

    # Layout for debate progress
    _, progress_col, _ = st.columns([0.5, 5, 0.5])

    with progress_col:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('''
        <div style="
            text-align: center;
            margin-bottom: 0.5rem;
        ">
            <div style="
                font-family: 'Lora', Georgia, serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: #f8f9fc;
            ">Debatte läuft</div>
            <div style="
                font-family: 'Source Sans 3', sans-serif;
                font-size: 0.85rem;
                color: #8892a6;
            ">Die KI-Systeme analysieren und verbessern Ihr Dokument</div>
        </div>
        ''', unsafe_allow_html=True)

        # Timeline placeholder
        timeline_placeholder = st.empty()

        # Progress bar
        progress_bar = st.progress(0.0)

        # Status card placeholder
        status_placeholder = st.empty()

        # Critique accordion section
        st.markdown('''
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            color: #8892a6;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
            margin: 1.5rem 0 0.5rem 0;
        ">Kritikpunkte</div>
        ''', unsafe_allow_html=True)

        critique_container = st.container()

    # Steps definition
    steps = [
        ("Claude", "claude", "C", call_claude, claude_model),
        ("Perplexity", "perplexity", "P", call_perplexity, perplexity_model),
        ("ChatGPT", "chatgpt", "G", call_chatgpt, chatgpt_model),
    ]

    step_count = 0
    debate_error = False
    converged = False
    convergence_reason = None
    convergence_confidence = 0
    rounds_completed = 0

    for r in range(1, rounds + 1):
        critique_for_round = compress_critique_log(full_log)
        doc_before_round = text
        round_critiques = ""

        for i, (name, cls, letter, func, model) in enumerate(steps):
            step_count += 1

            # Update timeline
            timeline_placeholder.markdown(
                build_timeline_html(rounds, r, i),
                unsafe_allow_html=True,
            )

            # Update status card
            status_placeholder.markdown(
                build_status_html(name, cls, letter, r, rounds, is_working=True),
                unsafe_allow_html=True,
            )

            # Update progress
            progress_bar.progress(step_count / total_steps)

            try:
                raw = func(text, critique_for_round, model)
                doc, critique = parse_structured_output(raw)
                text = doc
                full_log += f"\n[Runde {r} -- {name}]\n{critique}\n"
                round_critiques += f"[{name}]\n{critique}\n\n"
                save_intermediate(output_dir, r, name.lower(), doc, critique)

                # Add critique to accordion
                with critique_container.expander(
                    f"Runde {r} -- {name}",
                    expanded=False,
                ):
                    formatted_critique = critique
                    formatted_critique = formatted_critique.replace(
                        "[GEAENDERT]", "**[GEAENDERT]**"
                    ).replace(
                        "[GEÄNDERT]", "**[GEAENDERT]**"
                    ).replace(
                        "[HINZUGEFUEGT]", "**[HINZUGEFUEGT]**"
                    ).replace(
                        "[HINZUGEFÜGT]", "**[HINZUGEFUEGT]**"
                    ).replace(
                        "[DISSENS]", "**[DISSENS]**"
                    )
                    st.markdown(formatted_critique)

            except Exception as e:
                status_placeholder.empty()
                st.error(f"Fehler bei {name} (Runde {r}): {e}")
                debate_error = True
                st.stop()

        rounds_completed = r

        # --- Konvergenz-Check nach abgeschlossener Runde ---
        if auto_stop and r >= min_rounds and r < rounds:
            status_placeholder.markdown(f'''
            <div class="status-card working">
                <div class="status-icon synthesis">K</div>
                <div class="status-text">
                    <div class="name">Konvergenz-Check</div>
                    <div class="detail">Prüfe ob weitere Runden Mehrwert bringen...</div>
                </div>
                <div class="status-spinner"></div>
            </div>
            ''', unsafe_allow_html=True)

            try:
                should_stop, confidence, reason = call_convergence_check(
                    doc_before_round, text, round_critiques, r, claude_model,
                )

                if should_stop and confidence >= convergence_threshold:
                    converged = True
                    convergence_reason = reason
                    convergence_confidence = confidence

                    # Show convergence detection in critique container
                    with critique_container.expander(
                        f"Konvergenz erkannt nach Runde {r}",
                        expanded=True,
                    ):
                        st.markdown(
                            f"**Verdict:** STOP (Confidence: {confidence}%)\n\n"
                            f"**Begruendung:** {reason}"
                        )
                    break
                else:
                    # Show that check happened but debate continues
                    with critique_container.expander(
                        f"Konvergenz-Check nach Runde {r}",
                        expanded=False,
                    ):
                        verdict = "STOP" if should_stop else "CONTINUE"
                        st.markdown(
                            f"**Verdict:** {verdict} (Confidence: {confidence}%)\n\n"
                            f"**Begruendung:** {reason}"
                        )

            except Exception:
                pass  # Konvergenz-Fehler stoppen nicht die Debatte

    # ---------------------------------------------------------------------------
    # Final Synthesis
    # ---------------------------------------------------------------------------

    step_count = rounds_completed * 3 + 1

    # Update timeline to synthesis
    timeline_placeholder.markdown(
        build_timeline_html(rounds_completed if converged else rounds, rounds_completed, 3),
        unsafe_allow_html=True,
    )

    # Update status card for synthesis
    status_placeholder.markdown(
        build_status_html(
            "Synthese", "synthesis", "S", 0, rounds, is_working=True,
        ),
        unsafe_allow_html=True,
    )
    progress_bar.progress(0.9)

    try:
        result = call_synthesis(text, full_log, claude_model)
    except Exception as e:
        status_placeholder.empty()
        st.error(f"Fehler bei der Synthese: {e}")
        st.stop()

    # Completion
    progress_bar.progress(1.0)

    # Final timeline state
    timeline_placeholder.markdown(
        build_timeline_html(
            rounds_completed if converged else rounds,
            rounds_completed, 3, total_done=True,
        ),
        unsafe_allow_html=True,
    )

    # Clear status card and show success
    status_placeholder.empty()

    with progress_col:
        # Success banner
        if converged:
            banner_detail = (
                f"{rounds_completed} von {rounds} Runden &middot; "
                f"Auto-Stop bei {convergence_confidence}% Confidence &middot; "
                f"3 KI-Perspektiven &middot; 1 synthetisiertes Ergebnis"
            )
            banner_subtitle = f'''
                <div style="
                    font-family: 'Source Sans 3', sans-serif;
                    font-size: 0.82rem;
                    color: #d4a843;
                    margin-top: 0.5rem;
                    padding: 0.5rem 1rem;
                    background: rgba(201, 149, 45, 0.08);
                    border: 1px solid rgba(201, 149, 45, 0.2);
                    border-radius: 8px;
                    display: inline-block;
                ">{convergence_reason}</div>
            '''
        else:
            banner_detail = (
                f"{rounds_completed} Runden &middot; {rounds_completed * 3} Kritik-Durchläufe &middot; "
                f"3 KI-Perspektiven &middot; 1 synthetisiertes Ergebnis"
            )
            banner_subtitle = ""

        st.markdown(f'''
        <div class="success-banner">
            <div class="success-icon">&#127942;</div>
            <div class="success-title">Debatte abgeschlossen</div>
            <div class="success-detail">{banner_detail}</div>
            {banner_subtitle}
        </div>
        ''', unsafe_allow_html=True)

        # ---------------------------------------------------------------------------
        # Result Section
        # ---------------------------------------------------------------------------

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        st.markdown('''
        <div class="result-header">
            <h2>Finales Strategiedokument</h2>
            <p>Synthetisiert aus allen KI-Perspektiven und Debatten-Runden</p>
        </div>
        ''', unsafe_allow_html=True)

        # Use Streamlit's native markdown rendering inside a styled container
        st.markdown('''<div style="
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 2rem 2.5rem;
            margin: 1rem 0 1.5rem 0;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        ">''', unsafe_allow_html=True)
        st.markdown(result)
        st.markdown('</div>', unsafe_allow_html=True)

        # Action buttons
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            st.download_button(
                label="Als Markdown herunterladen",
                data=result,
                file_name=f"strategie_ergebnis_{session_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with btn_col2:
            st.download_button(
                label="Kritik-Verlauf herunterladen",
                data=full_log,
                file_name=f"kritik_verlauf_{session_id}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        # Full critique log
        st.markdown('''
        <div style="
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.78rem;
            color: #8892a6;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
            margin: 2rem 0 0.5rem 0;
        ">Vollständiger Debatten-Verlauf</div>
        ''', unsafe_allow_html=True)

        with st.expander("Gesamten Kritik-Verlauf anzeigen", expanded=False):
            st.text(full_log)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown('''
<div class="app-footer">
    <div class="footer-brand">
        Maure's <span class="gold">Strategie Club</span>
    </div>
    <div class="footer-sub">
        Claude &middot; Perplexity &middot; ChatGPT &middot; Powered by Multi-AI Debate
    </div>
</div>
''', unsafe_allow_html=True)
