import streamlit as st
from typing import Optional, Dict, Any, List

# ==============================================================================
# DESIGN SYSTEM TOKENS — "Minimalist Modern"
# ==============================================================================
COLOR_BACKGROUND = "#FAFAFA"         # Primary canvas: warm off-white
COLOR_FOREGROUND = "#0F172A"         # Primary text: deep slate
COLOR_MUTED = "#F1F5F9"              # Secondary surfaces & fills
COLOR_MUTED_FOREGROUND = "#64748B"   # Secondary text / descriptions
COLOR_ACCENT = "#0052FF"             # Primary action / Electric Blue
COLOR_ACCENT_SECONDARY = "#4D7CFF"   # Gradient endpoint
COLOR_ACCENT_FOREGROUND = "#FFFFFF"  # Text on accent
COLOR_BORDER = "#E2E8F0"             # Subtle structural borders
COLOR_CARD = "#FFFFFF"               # Elevated surfaces
COLOR_RING = "#0052FF"               # Focus rings

# Signature Gradients
GRADIENT_ELECTRIC = "linear-gradient(135deg, #0052FF, #4D7CFF)"
GRADIENT_HORIZONTAL = "linear-gradient(to right, #0052FF, #4D7CFF)"
GRADIENT_SUBTLE = "linear-gradient(135deg, rgba(0,82,255,0.08), rgba(77,124,255,0.03))"

# Shadow Presets
SHADOW_SM = "0 1px 3px rgba(0,0,0,0.06)"
SHADOW_MD = "0 4px 6px rgba(0,0,0,0.07)"
SHADOW_LG = "0 10px 15px rgba(0,0,0,0.08)"
SHADOW_XL = "0 20px 25px rgba(0,0,0,0.1)"
SHADOW_ACCENT = "0 4px 14px rgba(0,82,255,0.25)"
SHADOW_ACCENT_LG = "0 8px 24px rgba(0,82,255,0.35)"

# Plotly Colorway
PLOTLY_COLORWAY = ["#0052FF", "#4D7CFF", "#0F172A", "#64748B", "#10B981", "#F59E0B", "#EF4444"]


def apply_custom_css():
    """
    Injects the complete Minimalist Modern design system styling into Streamlit.
    Features:
    - Dual-font typography (Calistoga display serif + Inter UI/sans + JetBrains Mono)
    - Electric Blue gradient accents and text highlights
    - Tactile button hover lifts and active scale states
    - Elevated card surfaces with accent-tinted depth
    - Inverted dark-contrast telemetry sections with dot grid texture
    - Pulsing indicator badges and living micro-animations
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Calistoga&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Design Tokens Root */
    :root {
        --background: #FAFAFA;
        --foreground: #0F172A;
        --muted: #F1F5F9;
        --muted-foreground: #64748B;
        --accent: #0052FF;
        --accent-secondary: #4D7CFF;
        --accent-foreground: #FFFFFF;
        --border: #E2E8F0;
        --card: #FFFFFF;
        --font-display: 'Calistoga', Georgia, serif;
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    /* Global Canvas & Base Typography */
    html, body, [class*="css"] {
        font-family: var(--font-sans);
        color: var(--foreground);
        background-color: var(--background);
        -webkit-font-smoothing: antialiased;
    }

    /* Streamlit Container Layout Tuning */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1280px !important;
    }

    /* Streamlit Chrome Hiding */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* =========================================================================
       TYPOGRAPHY & SIGNATURE HEADINGS
       ========================================================================= */
    .calistoga-heading {
        font-family: var(--font-display) !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.15 !important;
        color: var(--foreground);
    }

    .gradient-text {
        background: linear-gradient(135deg, #0052FF, #4D7CFF);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        display: inline-block;
    }

    .gradient-underline {
        position: relative;
        display: inline-block;
    }
    .gradient-underline::after {
        content: "";
        position: absolute;
        bottom: -2px;
        left: 0;
        height: 6px;
        width: 100%;
        border-radius: 2px;
        background: linear-gradient(to right, rgba(0, 82, 255, 0.25), rgba(77, 124, 255, 0.15));
        z-index: 0;
    }

    /* =========================================================================
       PAGE HEADER
       ========================================================================= */
    .enterprise-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: 4px 0 18px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 22px;
    }
    .header-titles {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .page-title {
        font-family: var(--font-display);
        font-size: 26px;
        font-weight: 400;
        letter-spacing: -0.02em;
        color: var(--foreground);
        margin: 0;
        line-height: 1.2;
    }
    .page-subtitle {
        font-family: var(--font-sans);
        font-size: 13px;
        color: var(--muted-foreground);
        margin: 0;
        font-weight: 400;
        line-height: 1.5;
    }

    /* Section Label Badge (The Signature Pill) */
    .section-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border-radius: 9999px;
        border: 1px solid rgba(0, 82, 255, 0.25);
        background: rgba(0, 82, 255, 0.05);
        padding: 4px 12px;
        white-space: nowrap;
    }
    .section-badge-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: var(--accent);
        box-shadow: 0 0 8px rgba(0, 82, 255, 0.6);
        animation: pulse-dot 2s infinite ease-in-out;
    }
    .section-badge-text {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--accent);
    }

    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.35); opacity: 0.65; }
    }

    /* =========================================================================
       STEPPER WORKFLOW NAVIGATION
       ========================================================================= */
    .stepper-container {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    .stepper-label {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 700;
        color: var(--muted-foreground);
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }
    .stepper-items {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .step-node {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: var(--font-sans);
        font-size: 12px;
        font-weight: 500;
        color: var(--muted-foreground);
        padding: 5px 12px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    .step-node.active {
        color: var(--accent);
        background: rgba(0, 82, 255, 0.06);
        font-weight: 600;
        border: 1px solid rgba(0, 82, 255, 0.25);
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--muted);
        color: var(--muted-foreground);
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 700;
    }
    .step-node.active .step-number {
        background: linear-gradient(135deg, #0052FF, #4D7CFF);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(0, 82, 255, 0.4);
    }
    .stepper-sep {
        color: #cbd5e1;
        font-size: 12px;
    }

    /* =========================================================================
       NATIVE STREAMLIT METRICS CARDS OVERRIDE
       ========================================================================= */
    div[data-testid="stMetric"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0, 82, 255, 0.06) !important;
        border-color: rgba(0, 82, 255, 0.3) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-mono) !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--muted-foreground) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-sans) !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--foreground) !important;
        letter-spacing: -0.02em !important;
    }

    /* =========================================================================
       STREAMLIT BUTTONS & INTERACTIVE CONTROLS
       ========================================================================= */
    /* Primary Action Buttons */
    .stButton > button[kind="primary"], button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0052FF 0%, #4D7CFF 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 14px rgba(0, 82, 255, 0.25) !important;
        transition: all 0.2s ease-out !important;
    }
    .stButton > button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(0, 82, 255, 0.35) !important;
        filter: brightness(1.06) !important;
    }
    .stButton > button[kind="primary"]:active, button[data-testid="baseButton-primary"]:active {
        transform: scale(0.98) !important;
    }

    /* Secondary / Outline Buttons */
    .stButton > button:not([kind="primary"]), button[data-testid="baseButton-secondary"] {
        background: var(--card) !important;
        color: var(--foreground) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease-out !important;
    }
    .stButton > button:not([kind="primary"]):hover, button[data-testid="baseButton-secondary"]:hover {
        border-color: rgba(0, 82, 255, 0.35) !important;
        background: var(--muted) !important;
        color: var(--accent) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:not([kind="primary"]):active, button[data-testid="baseButton-secondary"]:active {
        transform: scale(0.98) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background: var(--card) !important;
        color: var(--foreground) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0, 82, 255, 0.15) !important;
    }

    /* Inputs, Selectboxes, Text Areas */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] > div {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--card) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-baseweb="input"]:focus-within > div,
    div[data-baseweb="select"]:focus-within > div,
    div[data-baseweb="textarea"]:focus-within > div {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.15) !important;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px !important;
        border-bottom: 1px solid var(--border) !important;
        padding-bottom: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-sans) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--muted-foreground) !important;
        padding: 8px 14px !important;
        border-radius: 6px 6px 0 0 !important;
        transition: color 0.15s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
        border-bottom-width: 2px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important;
    }

    /* =========================================================================
       INVERTED CONTRAST SECTIONS (The Signature Dark Texture)
       ========================================================================= */
    .inverted-section {
        background-color: #0F172A;
        color: #F8FAFC;
        border-radius: 16px;
        padding: 24px 28px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
        background-image: radial-gradient(circle, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 28px 28px;
        margin: 22px 0;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2);
    }
    .inverted-section::after {
        content: "";
        position: absolute;
        top: -70px;
        right: -70px;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 82, 255, 0.3), transparent 70%);
        pointer-events: none;
        filter: blur(25px);
    }
    .inverted-section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        position: relative;
        z-index: 1;
    }
    .inverted-section-title {
        font-family: var(--font-display);
        font-size: 18px;
        font-weight: 400;
        color: #FFFFFF;
        letter-spacing: -0.01em;
    }
    .inverted-section-subtitle {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 2px;
    }
    .inverted-section-body {
        position: relative;
        z-index: 1;
    }

    /* =========================================================================
       CUSTOM KPI CARDS & FEATURED WRAPPERS
       ========================================================================= */
    .kpi-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 8px;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 82, 255, 0.07);
        border-color: rgba(0, 82, 255, 0.35);
    }

    .kpi-card-featured {
        border-radius: 16px;
        background: linear-gradient(135deg, #0052FF, #4D7CFF, #0052FF);
        padding: 2px;
        box-shadow: 0 6px 18px rgba(0, 82, 255, 0.2);
        height: 100%;
        margin-bottom: 8px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card-featured:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 26px rgba(0, 82, 255, 0.32);
    }
    .kpi-card-featured-inner {
        background: var(--card);
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .kpi-label {
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 600;
        color: var(--muted-foreground);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .kpi-value {
        font-family: var(--font-sans);
        font-size: 28px;
        font-weight: 700;
        color: var(--foreground);
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .kpi-subtext {
        font-size: 12px;
        color: var(--muted-foreground);
        margin-top: 6px;
        line-height: 1.4;
    }

    /* =========================================================================
       GOVERNANCE HERO BANNER
       ========================================================================= */
    .governance-hero-banner {
        background: var(--card);
        border-left: 4px solid var(--accent);
        border-top: 1px solid var(--border);
        border-right: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 82, 255, 0.04);
        position: relative;
        overflow: hidden;
    }
    .gov-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent);
        background: rgba(0, 82, 255, 0.06);
        border: 1px solid rgba(0, 82, 255, 0.2);
        padding: 3px 8px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .gov-heading {
        font-family: var(--font-display);
        font-size: 16px;
        font-weight: 400;
        color: var(--foreground);
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .gov-subtext {
        font-size: 13px;
        color: #475569;
        line-height: 1.55;
    }

    /* =========================================================================
       APPROVAL QUEUE DOSSIER & INITIATIVE CARDS
       ========================================================================= */
    .approval-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .approval-card:hover {
        border-color: rgba(0, 82, 255, 0.35);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.05);
    }
    .approval-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    .approval-card-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--foreground);
        line-height: 1.4;
        margin-top: 2px;
    }
    .approval-meta-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        background: var(--muted);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 12px;
    }
    .meta-item-label {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        color: var(--muted-foreground);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 2px;
    }
    .meta-item-val {
        font-weight: 600;
        color: var(--foreground);
    }
    .evidence-dossier {
        background: #F8FAFC;
        border-left: 3px solid var(--accent);
        padding: 12px 16px;
        border-radius: 0 10px 10px 0;
        margin: 12px 0 16px 0;
        font-size: 12px;
        color: #334155;
    }
    .evidence-label {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 700;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .evidence-text {
        font-style: italic;
        line-height: 1.55;
    }

    /* Initiative Progress Cards */
    .initiative-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .initiative-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 82, 255, 0.3);
        box-shadow: 0 8px 16px rgba(0, 82, 255, 0.05);
    }

    /* Task Alert Cards */
    .task-alert-card {
        background: var(--card);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border: 1px solid var(--border);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .task-alert-card:hover {
        transform: translateX(2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .task-alert-card.overdue {
        border-left: 4px solid #EF4444;
        background: #FFFDFD;
    }
    .task-alert-card.upcoming {
        border-left: 4px solid var(--accent);
    }
    .task-alert-card.urgent {
        border-left: 4px solid #F59E0B;
    }

    /* Meeting Feed Card */
    .meeting-feed-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .meeting-feed-card:hover {
        border-color: rgba(0, 82, 255, 0.3);
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.04);
    }

    /* =========================================================================
       BADGES (Strict Minimalist Palette)
       ========================================================================= */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 9px;
        font-family: var(--font-mono);
        font-size: 11px;
        font-weight: 600;
        border-radius: 6px;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }
    .badge-completed { background: #ECFDF5; color: #10B981; border: 1px solid #A7F3D0; }
    .badge-in-progress { background: rgba(0, 82, 255, 0.06); color: #0052FF; border: 1px solid rgba(0, 82, 255, 0.25); }
    .badge-not-started { background: #F8FAFC; color: #64748B; border: 1px solid #E2E8F0; }
    .badge-blocked { background: #FEF2F2; color: #EF4444; border: 1px solid #FCA5A5; }
    .badge-overdue { background: #FEF2F2; color: #EF4444; border: 1px solid #F87171; font-weight: 700; }
    .badge-high { background: #FEF2F2; color: #EF4444; border: 1px solid #FCA5A5; }
    .badge-medium { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
    .badge-low { background: #ECFDF5; color: #10B981; border: 1px solid #A7F3D0; }
    .badge-confidence { background: rgba(0, 82, 255, 0.06); color: #0052FF; border: 1px solid rgba(0, 82, 255, 0.25); font-weight: 600; }

    /* =========================================================================
       EMPTY STATE BOX
       ========================================================================= */
    .empty-state-box {
        background: var(--card);
        border: 1px dashed #CBD5E1;
        border-radius: 16px;
        padding: 40px 24px;
        text-align: center;
        margin: 20px 0;
        background-image: radial-gradient(circle, rgba(0, 82, 255, 0.04) 1px, transparent 1px);
        background-size: 20px 20px;
    }
    .empty-state-title {
        font-family: var(--font-display);
        font-size: 17px;
        font-weight: 400;
        color: var(--foreground);
        margin-bottom: 6px;
    }
    .empty-state-desc {
        font-size: 13px;
        color: var(--muted-foreground);
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* =========================================================================
       SIDEBAR BRANDING BOX
       ========================================================================= */
    .sidebar-brand-box {
        padding: 8px 0 16px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .sidebar-brand-title {
        font-size: 18px;
        font-weight: 800;
        color: var(--foreground);
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sidebar-brand-logo {
        background: linear-gradient(135deg, #0052FF, #4D7CFF);
        color: #FFFFFF;
        padding: 4px 9px;
        border-radius: 8px;
        font-family: var(--font-mono);
        font-size: 13px;
        font-weight: 800;
        box-shadow: 0 2px 8px rgba(0, 82, 255, 0.35);
    }
    .sidebar-brand-subtitle {
        font-family: var(--font-sans);
        font-size: 11px;
        color: var(--muted-foreground);
        font-weight: 500;
        margin-top: 5px;
        letter-spacing: 0.02em;
    }
    </style>
    """, unsafe_allow_html=True)


def render_section_badge(text: str, pulsing: bool = True) -> str:
    """Returns HTML for the signature Minimalist Modern pill badge with pulsing dot."""
    dot_html = '<span class="section-badge-dot"></span>' if pulsing else ''
    return f"""
    <div class="section-badge-pill">
        {dot_html}
        <span class="section-badge-text">{text}</span>
    </div>
    """


def render_page_header(title: str, subtitle: str, badge_text: Optional[str] = None, highlight_word: Optional[str] = None):
    """
    Renders standardized Minimalist Modern page header:
    - Calistoga display headline with optional electric gradient text highlight & underline
    - JetBrains Mono pill badge
    - Clean Inter subtitle
    """
    # If highlight word provided or inferrable, wrap with gradient text
    headline_html = title
    if highlight_word and highlight_word in title:
        replacement = f'<span class="gradient-text gradient-underline">{highlight_word}</span>'
        headline_html = title.replace(highlight_word, replacement, 1)

    badge_html = render_section_badge(badge_text) if badge_text else ''

    st.markdown(f"""
    <div class="enterprise-header">
        <div class="header-titles">
            <h1 class="page-title">{headline_html}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)


def render_workflow_indicator(current_step: str = "Dashboard"):
    """Renders the core human-in-the-loop product workflow pipeline with Minimalist Modern stepper."""
    steps = [
        ("AI Extraction", "1. AI Extraction"),
        ("Approval Queue", "2. Human Approval"),
        ("Initiative Tracker", "3. Official Tracker"),
        ("Analytics", "4. Analytics"),
        ("Weekly Report", "5. Weekly Report")
    ]
    
    html = '<div class="stepper-container">'
    html += '<span class="stepper-label">Execution Flow:</span>'
    html += '<div class="stepper-items">'
    for i, (name, label) in enumerate(steps, 1):
        is_active = (current_step == name)
        active_class = "active" if is_active else ""
        step_title = label.split(". ")[1]
        html += f'<div class="step-node {active_class}"><span class="step-number">{i}</span>{step_title}</div>'
        if i < len(steps):
            html += '<span class="stepper-sep">&rarr;</span>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_governance_banner():
    """Renders the mandatory human-in-the-loop governance explanation banner."""
    st.markdown("""
    <div class="governance-hero-banner">
        <div class="gov-pill">Mandatory Governance Policy</div>
        <div class="gov-heading">Human Verification Required for All Deliverables</div>
        <div class="gov-subtext">
            <b>AI suggestions are never committed automatically. Every action item requires human verification.</b>
            Items staged below were inferred from meeting transcripts. Authorize deliverables to commit them to the official initiative tracker, or reject items to record them in the governance audit trail.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(title: str, description: str):
    """Renders clean Minimalist Modern empty state with texture."""
    st.markdown(f"""
    <div class="empty-state-box">
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def get_status_badge_html(status: str, is_overdue: bool = False) -> str:
    """Returns clean HTML badge for status."""
    if is_overdue and status != "Completed":
        return '<span class="badge badge-overdue">OVERDUE</span>'
    s_clean = status.lower().replace(" ", "-")
    return f'<span class="badge badge-{s_clean}">{status}</span>'


def get_priority_badge_html(priority: str) -> str:
    """Returns clean HTML badge for priority."""
    p_clean = priority.lower()
    return f'<span class="badge badge-{p_clean}">{priority} Priority</span>'


def get_confidence_badge_html(score: float) -> str:
    """Returns clean HTML badge for AI confidence score."""
    pct = int(score * 100) if score <= 1.0 else int(score)
    return f'<span class="badge badge-confidence">{pct}% Inferred Match</span>'


def render_custom_kpi_card(
    label: str,
    value: str,
    subtext: str = "",
    badge_text: str = "",
    badge_color: str = "neutral",
    is_featured: bool = False
):
    """
    Renders a Minimalist Modern KPI card.
    If is_featured=True, wraps with the 2px Electric Blue gradient border stroke.
    """
    badge_palette = {
        "blue": {"bg": "rgba(0,82,255,0.06)", "color": "#0052FF", "border": "rgba(0,82,255,0.25)"},
        "green": {"bg": "#ECFDF5", "color": "#10B981", "border": "#A7F3D0"},
        "amber": {"bg": "#FFFBEB", "color": "#D97706", "border": "#FDE68A"},
        "red": {"bg": "#FEF2F2", "color": "#EF4444", "border": "#FCA5A5"},
        "neutral": {"bg": "#F8FAFC", "color": "#64748B", "border": "#E2E8F0"}
    }
    b = badge_palette.get(badge_color, badge_palette["neutral"])
    badge_html = f'<span style="background:{b["bg"]}; color:{b["color"]}; border:1px solid {b["border"]}; font-family:var(--font-mono); font-size:11px; font-weight:600; padding:2px 8px; border-radius:6px; white-space:nowrap;">{badge_text}</span>' if badge_text else ''

    content_inner = f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span class="kpi-label">{label}</span>
            {badge_html}
        </div>
        <div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-subtext">{subtext}</div>' if subtext else ''}
        </div>
    """

    if is_featured:
        html = f"""
        <div class="kpi-card-featured">
            <div class="kpi-card-featured-inner">
                {content_inner}
            </div>
        </div>
        """
    else:
        html = f"""
        <div class="kpi-card">
            {content_inner}
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)


def render_initiative_card(item: dict):
    """Renders a structured card for an initiative with gradient progress bars."""
    health_styles = {
        "On Track": {"color": "#10B981", "bg": "#ECFDF5", "border": "#A7F3D0", "bar": "linear-gradient(90deg, #10B981, #34D399)"},
        "Needs Attention": {"color": "#D97706", "bg": "#FFFBEB", "border": "#FDE68A", "bar": "linear-gradient(90deg, #F59E0B, #FBBF24)"},
        "At Risk": {"color": "#EF4444", "bg": "#FEF2F2", "border": "#FCA5A5", "bar": "linear-gradient(90deg, #EF4444, #F87171)"}
    }
    style = health_styles.get(item["health"], health_styles["On Track"])

    st.markdown(f"""
    <div class="initiative-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div>
                <span style="font-weight:700; color:#0F172A; font-size:14px;">{item['initiative']}</span>
                <span style="font-size:12px; color:#64748B; margin-left:8px;">Lead: <b>{item['owner']}</b></span>
            </div>
            <span style="background:{style['bg']}; color:{style['color']}; border:1px solid {style['border']}; padding:2px 8px; border-radius:6px; font-family:var(--font-mono); font-weight:700; font-size:10px; letter-spacing:0.04em;">
                {item['health'].upper()}
            </span>
        </div>
        <div style="display:flex; gap:16px; font-size:12px; color:#475569; margin-bottom:8px;">
            <span>Total: <b>{item['total_tasks']}</b></span>
            <span>Completed: <b style="color:#10B981;">{item['completed']}</b></span>
            <span>In Progress: <b style="color:#0052FF;">{item['in_progress']}</b></span>
            <span>Blocked: <b style="color:#EF4444;">{item['blocked']}</b></span>
            <span>Overdue: <b style="color:#EF4444;">{item['overdue']}</b></span>
        </div>
        <div style="background:#F1F5F9; border-radius:6px; height:8px; width:100%; overflow:hidden;">
            <div style="background:{style['bar']}; height:100%; width:{item['completion_rate']}%; border-radius:6px;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#64748B; margin-top:6px;">
            <span>Sprint Commitment</span>
            <span style="font-family:var(--font-mono);"><b>{item['completion_rate']}% Complete</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_task_alert_card(task: dict, is_overdue: bool = True):
    """Renders a single overdue or upcoming deadline task item."""
    if is_overdue:
        days_late = task.get("days_late", 0)
        badge = f'<span style="background:#FEF2F2; color:#B91C1C; border:1px solid #FECACA; font-family:var(--font-mono); font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px; white-space:nowrap;">{days_late}D OVERDUE</span>'
        css_class = "task-alert-card overdue"
    else:
        days_left = task.get("days_left", 0)
        is_urgent = days_left <= 3
        badge_bg = "#FFFBEB" if is_urgent else "rgba(0,82,255,0.06)"
        badge_color = "#92400E" if is_urgent else "#0052FF"
        badge_border = "#FDE68A" if is_urgent else "rgba(0,82,255,0.25)"
        badge = f'<span style="background:{badge_bg}; color:{badge_color}; border:1px solid {badge_border}; font-family:var(--font-mono); font-size:10px; font-weight:700; padding:2px 7px; border-radius:4px; white-space:nowrap;">DUE IN {days_left}D</span>'
        css_class = "task-alert-card urgent" if is_urgent else "task-alert-card upcoming"

    date_label = "Due" if is_overdue else "Target"
    st.markdown(f"""
    <div class="{css_class}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
            <div>
                <span style="font-weight:600; color:#0F172A; font-size:13px;">#{task['id']}. {task['title']}</span>
                <div style="font-size:12px; color:#64748B; margin-top:2px;">
                    Owner: <b>{task['owner']}</b> &bull; Initiative: {task['initiative']} &bull; {date_label}: <b>{task['deadline']}</b>
                </div>
            </div>
            {badge}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_meeting_feed_card(meeting: dict):
    """Renders a concise meeting intelligence summary card."""
    summary_text = meeting['summary'] or 'Meeting notes recorded and indexed.'
    st.markdown(f"""
    <div class="meeting-feed-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:700; color:#0F172A; font-size:14px;">{meeting['title']}</div>
            <span style="background:rgba(0,82,255,0.06); color:#0052FF; border:1px solid rgba(0,82,255,0.2); font-family:var(--font-mono); font-size:10px; font-weight:600; padding:2px 7px; border-radius:4px;">
                {meeting['meeting_type']}
            </span>
        </div>
        <div style="font-size:11px; color:#64748B; margin:3px 0 6px 0;">
            Date: {meeting['meeting_date']} &bull; Organizer: <b>{meeting['organizer']}</b>
        </div>
        <div style="font-size:12px; color:#475569; line-height:1.45;">
            {summary_text}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_plotly_minimalist_layout(title: str = "", height: int = 340) -> Dict[str, Any]:
    """
    Returns standard Plotly layout dictionary matching the Minimalist Modern design system:
    - Transparent paper and plot background
    - Inter font for text, Calistoga for titles
    - Subtle slate grid lines
    - Electric blue & slate colorway
    """
    return {
        "title": {
            "text": title,
            "font": {"family": "Calistoga, serif", "size": 15, "color": "#0F172A"},
            "x": 0.02,
            "y": 0.95
        } if title else None,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "size": 11, "color": "#64748B"},
        "colorway": PLOTLY_COLORWAY,
        "margin": {"l": 20, "r": 20, "t": 35 if title else 15, "b": 25},
        "height": height,
        "xaxis": {
            "showgrid": True,
            "gridcolor": "#E2E8F0",
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"family": "Inter, sans-serif", "size": 10, "color": "#64748B"}
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "#E2E8F0",
            "gridwidth": 1,
            "zeroline": False,
            "tickfont": {"family": "Inter, sans-serif", "size": 10, "color": "#64748B"}
        },
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"family": "Inter, sans-serif", "size": 11, "color": "#475569"}
        }
    }
