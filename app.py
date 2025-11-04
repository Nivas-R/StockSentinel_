# ---- StockSentinel - Learning & Trading Intelligence ----
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import os
import unicodedata
from fpdf import FPDF
import pytz
import time
import threading
import numpy as np
from plotly.subplots import make_subplots

# Ensure folder exists
os.makedirs("data", exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="STOCKSENTINEL",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'price_alerts' not in st.session_state:
    st.session_state.price_alerts = {}
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = "Apple Inc."
if 'compact_mode' not in st.session_state:
    st.session_state.compact_mode = False
if 'compare_stocks' not in st.session_state:
    st.session_state.compare_stocks = []

# NEW ELECTRIC CYAN & NAVY BLUE THEME CSS
modern_cyan_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800&family=Roboto+Mono:wght@400;500;600&display=swap');

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stHeaderActionElements {display: none;}

    /* NEW ELECTRIC CYAN THEME VARIABLES */
    :root {
        --bg-primary: #000000;
        --bg-secondary: #0a0e1a;
        --bg-navy: #001233;
        --bg-card: #0d1526;
        --bg-card-hover: #162038;
        --text-primary: #FFFFFF;
        --text-secondary: #B8C5D6;
        --text-muted: #7A8BA3;
        --accent-cyan: #00FFFF;
        --accent-cyan-glow: rgba(0, 255, 255, 0.5);
        --accent-blue: #0080FF;
        --border-subtle: rgba(0, 255, 255, 0.1);
        --border-accent: rgba(0, 255, 255, 0.4);
        --success: #00FF88;
        --danger: #FF4757;
        --warning: #FFA502;
        --glow-cyan: 0 0 20px rgba(0, 255, 255, 0.6), 0 0 40px rgba(0, 255, 255, 0.3);
    }

    /* Global Styles */
    * {
        font-family: 'Inter', 'Poppins', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-navy) 50%, var(--bg-primary) 100%);
        color: var(--text-primary);
    }

    /* Animated Grid Background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            linear-gradient(90deg, transparent 48%, rgba(0, 255, 255, 0.03) 49%, rgba(0, 255, 255, 0.03) 51%, transparent 52%),
            linear-gradient(0deg, transparent 48%, rgba(0, 255, 255, 0.03) 49%, rgba(0, 255, 255, 0.03) 51%, transparent 52%);
        background-size: 50px 50px;
        opacity: 0.4;
        z-index: 0;
        pointer-events: none;
        animation: gridPulse 4s ease-in-out infinite;
    }

    @keyframes gridPulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 0.6; }
    }

    /* Hero Header Section */
    .hero-section {
        position: relative;
        background: linear-gradient(135deg, var(--bg-navy) 0%, var(--bg-secondary) 100%);
        border-radius: 20px;
        padding: 60px 40px;
        margin-bottom: 40px;
        border: 2px solid var(--accent-cyan);
        overflow: hidden;
        box-shadow: var(--glow-cyan);
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
        animation: heroRotate 15s linear infinite;
    }

    @keyframes heroRotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .hero-content {
        position: relative;
        z-index: 1;
    }

    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4.5rem);
        font-weight: 900;
        color: var(--text-primary);
        margin: 0 0 16px 0;
        letter-spacing: -2px;
        line-height: 1.1;
        text-shadow: 0 0 30px var(--accent-cyan-glow);
    }

    .hero-title .accent {
        color: var(--accent-cyan);
        text-shadow: var(--glow-cyan);
        animation: textGlow 2s ease-in-out infinite;
    }

    @keyframes textGlow {
        0%, 100% { text-shadow: var(--glow-cyan); }
        50% { text-shadow: 0 0 30px rgba(0, 255, 255, 0.8), 0 0 60px rgba(0, 255, 255, 0.5); }
    }

    .hero-subtitle {
        font-size: clamp(1rem, 2vw, 1.4rem);
        color: var(--text-secondary);
        margin: 0 0 32px 0;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Enhanced Glass Card */
    .glass-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--border-subtle);
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
        transition: left 0.6s ease;
    }

    .glass-card:hover {
        background: linear-gradient(135deg, var(--bg-card-hover) 0%, var(--bg-navy) 100%);
        border-color: var(--accent-cyan);
        transform: translateY(-4px);
        box-shadow: 0 10px 40px rgba(0, 255, 255, 0.3);
    }

    .glass-card:hover::before {
        left: 100%;
    }

    /* ALWAYS VISIBLE INFO CARD */
    .info-card-permanent {
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.1) 0%, rgba(0, 128, 255, 0.05) 100%);
        border: 2px solid var(--accent-cyan);
        border-radius: 16px;
        padding: 24px 28px;
        margin: 24px 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 255, 255, 0.2);
        animation: cardFloat 3s ease-in-out infinite;
    }

    @keyframes cardFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }

    .info-card-permanent::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(0, 255, 255, 0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }

    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .info-card-permanent > * {
        position: relative;
        z-index: 1;
    }

    .info-card-title {
        color: var(--accent-cyan);
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        text-shadow: 0 0 10px var(--accent-cyan-glow);
    }

    .info-card-content {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.8;
    }

    /* Section Header */
    .section-header {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
        margin: 48px 0 24px 0;
        padding: 0 0 16px 0;
        border-bottom: 3px solid var(--border-accent);
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 150px;
        height: 3px;
        background: var(--accent-cyan);
        box-shadow: var(--glow-cyan);
        animation: headerGlow 2s ease-in-out infinite;
    }

    @keyframes headerGlow {
        0%, 100% { box-shadow: var(--glow-cyan); }
        50% { box-shadow: 0 0 30px rgba(0, 255, 255, 0.8); }
    }

    .section-header .icon {
        color: var(--accent-cyan);
        font-size: 1.8rem;
        text-shadow: var(--glow-cyan);
    }

    /* Enhanced Metric Card */
    .metric-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--border-subtle);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 255, 255, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .metric-card:hover::before {
        opacity: 1;
        animation: rotateGlow 3s linear infinite;
    }

    @keyframes rotateGlow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .metric-card:hover {
        transform: scale(1.08);
        border-color: var(--accent-cyan);
        box-shadow: 0 10px 40px rgba(0, 255, 255, 0.4);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 900;
        color: var(--text-primary);
        margin-bottom: 8px;
        font-family: 'Roboto Mono', monospace;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        position: relative;
        z-index: 1;
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }

    /* Enhanced Stock Ticker Cards */
    .ticker-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--border-subtle);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.4s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .ticker-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--accent-cyan);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }

    .ticker-card:hover::before {
        transform: scaleX(1);
    }

    .ticker-card:hover {
        border-color: var(--accent-cyan);
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(0, 255, 255, 0.3);
    }

    .ticker-name {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .ticker-price {
        color: var(--accent-cyan);
        font-size: 1.6rem;
        font-weight: 900;
        font-family: 'Roboto Mono', monospace;
        margin-bottom: 8px;
        text-shadow: 0 0 10px var(--accent-cyan-glow);
    }

    .ticker-change {
        font-size: 1rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }

    /* News Card */
    .news-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--border-subtle);
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }

    .news-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--accent-cyan);
        transform: scaleY(0);
        transition: transform 0.4s ease;
    }

    .news-card:hover::before {
        transform: scaleY(1);
    }

    .news-card:hover {
        border-color: var(--accent-cyan);
        transform: translateX(8px);
        box-shadow: 0 10px 40px rgba(0, 255, 255, 0.25);
    }

    .news-title {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .news-description {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .news-category-badge {
        display: inline-block;
        padding: 6px 16px;
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: var(--bg-primary);
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 10px;
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: var(--bg-primary);
        border: none;
        border-radius: 12px;
        padding: 14px 36px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.4);
        text-transform: uppercase;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 255, 255, 0.6);
    }

    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: statusPulse 2s infinite;
        box-shadow: 0 0 15px currentColor;
    }

    .status-online { 
        background: var(--success);
        color: var(--success);
    }
    
    .status-warning { 
        background: var(--warning);
        color: var(--warning);
    }
    
    .status-error { 
        background: var(--danger);
        color: var(--danger);
    }

    @keyframes statusPulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(0.9); }
    }

    /* Sentiment Colors */
    .sentiment-positive { 
        color: var(--success); 
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .sentiment-negative { 
        color: var(--danger); 
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
    }
    
    .sentiment-neutral { 
        color: var(--warning); 
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255, 165, 2, 0.5);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { 
        background: var(--accent-cyan); 
        border-radius: 6px;
        box-shadow: var(--glow-cyan);
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: var(--accent-blue);
    }

    /* Enhanced Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--bg-secondary);
        padding: 16px;
        border-radius: 16px;
        border: 2px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        font-weight: 700;
        padding: 14px 28px;
        border-radius: 12px;
        border: 2px solid transparent;
        transition: all 0.4s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card);
        border-color: var(--border-accent);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: var(--bg-primary);
        border: none;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.5);
    }

    /* Enhanced Data Table */
    .dataframe {
        background: var(--bg-card) !important;
        border: 2px solid var(--border-accent) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background: var(--bg-navy) !important;
        color: var(--accent-cyan) !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem !important;
        padding: 18px 14px !important;
        border-bottom: 3px solid var(--accent-cyan) !important;
    }

    .dataframe tbody tr {
        border-bottom: 1px solid var(--border-subtle) !important;
        transition: all 0.3s ease;
    }

    .dataframe tbody tr:hover {
        background: var(--bg-card-hover) !important;
        transform: scale(1.01);
    }

    .dataframe tbody tr td {
        color: var(--text-primary) !important;
        padding: 16px 14px !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.95rem !important;
    }

    /* Video Card */
    .video-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 2px solid var(--border-subtle);
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        transition: all 0.4s ease;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .video-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue));
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }

    .video-card:hover::before {
        transform: scaleX(1);
    }

    .video-card:hover {
        border-color: var(--accent-cyan);
        transform: translateY(-8px);
        box-shadow: 0 15px 50px rgba(0, 255, 255, 0.3);
    }

    .video-card h4 {
        color: var(--text-primary);
        margin-bottom: 14px;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .video-card p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    .video-card button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
        color: var(--bg-primary);
        border: none;
        padding: 14px 32px;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        border-radius: 12px;
        transition: all 0.4s ease;
        font-size: 1rem;
    }

    .video-card button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 255, 255, 0.5);
    }

    /* Price Display */
    .price-display {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-navy) 100%);
        border: 3px solid var(--accent-cyan);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--glow-cyan);
    }

    .price-display::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 255, 255, 0.15) 0%, transparent 70%);
        animation: priceRotate 20s linear infinite;
    }

    @keyframes priceRotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .price-display > * {
        position: relative;
        z-index: 1;
    }

    .company-name {
        font-size: 2rem;
        font-weight: 900;
        color: var(--text-primary);
        margin-bottom: 24px;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }

    .current-price {
        font-size: 4rem;
        font-weight: 900;
        font-family: 'Roboto Mono', monospace;
        margin-bottom: 16px;
        text-shadow: var(--glow-cyan);
    }

    .price-change {
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }

    /* AI Insight Card */
    .ai-insight {
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.15) 0%, rgba(0, 128, 255, 0.1) 100%);
        border: 3px solid var(--accent-cyan);
        border-radius: 20px;
        padding: 32px;
        margin: 28px 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 255, 255, 0.3);
    }

    .ai-insight::before {
        content: '◆';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 4rem;
        opacity: 0.1;
        color: var(--accent-cyan);
        animation: iconFloat 3s ease-in-out infinite;
    }

    @keyframes iconFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .ai-insight-title {
        color: var(--accent-cyan);
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        text-shadow: var(--glow-cyan);
    }

    .ai-insight-content {
        color: var(--text-secondary);
        font-size: 1.1rem;
        line-height: 1.8;
    }

    /* Score Gauge */
    .score-gauge {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
        background: conic-gradient(
            var(--accent-cyan) 0deg,
            var(--accent-cyan) calc(3.6deg * var(--score)),
            var(--bg-secondary) calc(3.6deg * var(--score)),
            var(--bg-secondary) 360deg
        );
        box-shadow: var(--glow-cyan);
    }

    .score-gauge::before {
        content: '';
        position: absolute;
        width: 105px;
        height: 105px;
        border-radius: 50%;
        background: var(--bg-card);
    }

    .score-value {
        position: relative;
        z-index: 1;
        font-size: 2.5rem;
        font-weight: 900;
        font-family: 'Roboto Mono', monospace;
        text-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
    }

    /* Glossary Term */
    .glossary-term {
        background: var(--bg-card);
        border-left: 4px solid var(--accent-cyan);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }

    .glossary-term:hover {
        background: var(--bg-card-hover);
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.2);
    }

    .glossary-term strong {
        color: var(--accent-cyan);
        font-size: 1.1rem;
        display: block;
        margin-bottom: 6px;
        text-shadow: 0 0 10px var(--accent-cyan-glow);
    }

    /* ENHANCED COMPANY SELECTOR */
    .company-selector-container {
        background: linear-gradient(135deg, var(--bg-navy) 0%, var(--bg-secondary) 100%);
        border: 3px solid var(--accent-cyan);
	border-radius: 20px;
        padding: 40px;
        margin: 30px 0;
        box-shadow: var(--glow-cyan);
        position: relative;
        overflow: hidden;
    }

    .company-selector-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(0, 255, 255, 0.05) 50%, transparent 70%);
        animation: selectorShine 3s infinite;
    }

    @keyframes selectorShine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .company-selector-title {
        color: var(--accent-cyan);
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
        text-shadow: var(--glow-cyan);
        position: relative;
        z-index: 1;
    }

    .company-info-display {
        background: var(--bg-card);
        border: 2px solid var(--border-accent);
        border-radius: 16px;
        padding: 24px;
        margin-top: 20px;
        position: relative;
        z-index: 1;
    }

    .company-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-top: 16px;
    }

    .company-info-item {
        text-align: center;
        padding: 12px;
        background: var(--bg-secondary);
        border-radius: 10px;
        border: 1px solid var(--border-subtle);
        transition: all 0.3s ease;
    }

    .company-info-item:hover {
        border-color: var(--accent-cyan);
        transform: scale(1.05);
    }

    .company-info-label {
        color: var(--text-muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .company-info-value {
        color: var(--accent-cyan);
        font-size: 1.1rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-subtitle { font-size: 1rem; }
        .section-header { font-size: 1.5rem; }
        .glass-card { padding: 20px; }
        .metric-card { padding: 20px; }
        .company-selector-container { padding: 24px; }
    }

    /* Loading Animation */
    .loading-spinner {
        border: 4px solid var(--border-subtle);
        border-top: 4px solid var(--accent-cyan);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 30px auto;
        box-shadow: var(--glow-cyan);
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Fade-in Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fadeInUp 0.8s ease-out;
    }

    /* News Category Tabs */
    .news-category-tabs {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }

    .news-category-tab {
        padding: 12px 24px;
        background: var(--bg-card);
        border: 2px solid var(--border-subtle);
        border-radius: 12px;
        color: var(--text-secondary);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .news-category-tab:hover {
        border-color: var(--accent-cyan);
        color: var(--accent-cyan);
        transform: translateY(-2px);
    }

    .news-category-tab.active {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
        color: var(--bg-primary);
        border: none;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.4);
    }
</style>
"""

st.markdown(modern_cyan_css, unsafe_allow_html=True)

# Sidebar with Glossary and Controls
with st.sidebar:
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: var(--accent-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px; text-shadow: var(--glow-cyan);">
            <span>◈</span> Control Panel
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact Mode Toggle
    if st.checkbox("Compact Mode", value=st.session_state.compact_mode):
        st.session_state.compact_mode = True
    else:
        st.session_state.compact_mode = False
    
    st.markdown("---")
    
    # Quick Search
    st.markdown("### ◎ Quick Search")
    search_query = st.text_input("Search company...", placeholder="e.g., Apple, Tesla")
    
    st.markdown("---")
    
    # Quick Glossary
    with st.expander("■ Quick Glossary", expanded=False):
        glossary_terms = {
            "Stock": "A share in the ownership of a company",
            "P/E Ratio": "Price-to-Earnings ratio - valuation metric",
            "RSI": "Relative Strength Index (0-100). >70 overbought, <30 oversold",
            "MACD": "Moving Average Convergence Divergence indicator",
            "Dividend": "Portion of profits distributed to shareholders",
            "Market Cap": "Total value of all outstanding shares",
            "Volume": "Number of shares traded in a period",
            "Bull Market": "Rising prices and investor optimism",
            "Bear Market": "Falling prices (20%+ decline) and pessimism",
            "Volatility": "Statistical measure of price fluctuation",
            "Bollinger Bands": "Volatility bands around moving average"
        }
        
        for term, definition in glossary_terms.items():
            st.markdown(f"""
            <div class="glossary-term">
                <strong>{term}</strong>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">{definition}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Movers Section
    with st.expander("◢ Market Movers", expanded=False):
        st.markdown("""
        <div class="info-card-permanent">
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                Live market data for top gainers and losers will appear here during market hours.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feedback Section
    with st.expander("◉ Feedback & Suggestions", expanded=False):
        feedback = st.text_area("Share your suggestions:", placeholder="How can we improve?")
        if st.button("Submit Feedback"):
            if feedback:
                st.success("✅ Thank you for your feedback!")
            else:
                st.warning("⚠️ Please enter your feedback")

# Hero Section
st.markdown("""
<div class="hero-section fade-in">
    <div class="hero-content">
        <h1 class="hero-title">
            STOCK<span class="accent">SENTINEL</span>
        </h1>
        <p class="hero-subtitle">
            <strong style="color: var(--accent-cyan);">Learning & Trading Intelligence</strong><br>
            Real-time market analytics platform with AI-powered insights, comprehensive analysis tools,
            and educational resources to empower your investment journey.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Market Status & System Info Widget
current_time = datetime.now()
ist = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist)
market_open = current_time_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close = current_time_ist.replace(hour=15, minute=30, second=0, microsecond=0)

if market_open <= current_time_ist <= market_close:
    market_status = "OPEN"
    status_class = "status-online"
elif current_time_ist < market_open:
    market_status = "PRE-MARKET"
    status_class = "status-warning"
else:
    market_status = "CLOSED"
    status_class = "status-error"

system_col1, system_col2, system_col3, system_col4 = st.columns(4)

with system_col1:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="status-indicator {status_class}"></div>
        <div class="metric-label">Indian Market</div>
        <div style="font-size: 1.4rem; color: var(--text-primary); font-weight: 700; margin-top: 8px;">{market_status}</div>
    </div>
    """, unsafe_allow_html=True)

with system_col2:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Current Time (IST)</div>
        <div style="font-size: 1.4rem; color: var(--accent-cyan); font-weight: 700; margin-top: 8px; font-family: 'Roboto Mono', monospace; text-shadow: var(--glow-cyan);">{current_time_ist.strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

with system_col3:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Trading Hours</div>
        <div style="font-size: 1.1rem; color: var(--text-secondary); margin-top: 8px;">9:15 AM - 3:30 PM</div>
    </div>
    """, unsafe_allow_html=True)

with system_col4:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Session Refreshes</div>
        <div style="font-size: 1.4rem; color: var(--text-primary); font-weight: 700; margin-top: 8px;">{st.session_state.refresh_counter}</div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Functions
@st.cache_data(ttl=300, show_spinner=False)
def get_latest_stock_data(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        periods_to_try = [period, "3mo", "6mo", "1y"]
        hist = pd.DataFrame()
        
        for p in periods_to_try:
            try:
                hist = stock.history(period=p, timeout=15)
                if not hist.empty:
                    break
            except:
                continue
        
        if hist.empty:
            return pd.DataFrame(), None, {}
        
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        except:
            info = {}
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
        
        return hist, current_price, info
    except Exception as e:
        return pd.DataFrame(), None, {}

API_KEY = "35be8e6d38f940aea0927849daec8cbb"
analyzer = SentimentIntensityAnalyzer()

@st.cache_data(ttl=900, show_spinner=False)
def fetch_news_by_category(query, category, limit=5):
    """Fetch news with category label"""
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize={limit}&apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = []
            if data.get("status") == "ok" and data.get("articles"):
                for article in data["articles"]:
                    title = article.get("title")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "Unknown")
                    published_at = article.get("publishedAt", "")
                    url_link = article.get("url", "#")
                    if title and title != "[Removed]" and len(title.strip()) > 10:
                        score = analyzer.polarity_scores(f"{title} {description}")["compound"]
                        sentiment = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                        try:
                            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            relative_time = "Today" if pub_date.date() == datetime.now().date() else f"{(datetime.now().date() - pub_date.date()).days} days ago"
                        except:
                            relative_time = "Recently"
                        articles.append({
                            "Title": title,
                            "Description": description or "Click to read more...",
                            "Sentiment": sentiment,
                            "Source": source,
                            "Time": relative_time,
                            "Url": url_link,
                            "Score": score,
                            "Category": category
                        })
            return articles
        return []
    except:
        return []

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def calculate_enhanced_analyst_score(info, stock_data, all_news):
    score = 0
    score_breakdown = {}
    
    # Momentum Score (25 points)
    momentum_score = 0
    if not stock_data.empty and len(stock_data) > 20:
        try:
            short_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-5]) / stock_data['Close'].iloc[-5]
            if short_change > 0.05: momentum_score += 10
            elif short_change > 0.02: momentum_score += 7
            elif short_change > 0: momentum_score += 4
            
            if len(stock_data) > 10:
                med_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-10]) / stock_data['Close'].iloc[-10]
                if med_change > 0.15: momentum_score += 10
                elif med_change > 0.10: momentum_score += 7
                elif med_change > 0.05: momentum_score += 4
                elif med_change > 0: momentum_score += 2
            
            if len(stock_data) > 20:
                long_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-20]) / stock_data['Close'].iloc[-20]
                if long_change > 0.20: momentum_score += 5
                elif long_change > 0.10: momentum_score += 3
                elif long_change > 0: momentum_score += 1
        except:
            pass
    score_breakdown['Momentum'] = momentum_score
    score += momentum_score

    # Valuation Score (25 points)
    valuation_score = 0
    try:
        pe_ratio = info.get('trailingPE')
        pb_ratio = info.get('priceToBook')
        debt_equity = info.get('debtToEquity', 0)
        
        if pe_ratio and 0 < pe_ratio <= 15: valuation_score += 15
        elif pe_ratio and 15 < pe_ratio <= 25: valuation_score += 10
        elif pe_ratio and 25 < pe_ratio <= 35: valuation_score += 5
        
        if pb_ratio and 0.5 <= pb_ratio <= 3: valuation_score += 5
        elif pb_ratio and 3 < pb_ratio <= 5: valuation_score += 3
        
        if debt_equity < 0.3: valuation_score += 5
        elif debt_equity < 0.6: valuation_score += 3
        elif debt_equity < 1.0: valuation_score += 1
    except:
        pass
    score_breakdown['Valuation'] = valuation_score
    score += valuation_score
    
    # News Sentiment Score (25 points)
    sentiment_score = 0
    if all_news:
        positive = sum(1 for news in all_news if "Positive" in news["Sentiment"])
        sentiment_score = int((positive / len(all_news)) * 25)
    score_breakdown['News Sentiment'] = sentiment_score
    score += sentiment_score
    
    # Volume Analysis (15 points)
    volume_score = 0
    if not stock_data.empty and 'Volume' in stock_data.columns:
        try:
            current_volume = stock_data['Volume'].iloc[-1]
            avg_volume_20 = stock_data['Volume'].tail(min(20, len(stock_data))).mean()
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
            
            if volume_ratio > 2.0: volume_score += 15
            elif volume_ratio > 1.5: volume_score += 12
            elif volume_ratio > 1.2: volume_score += 8
            elif volume_ratio > 0.8: volume_score += 5
        except:
            pass
    score_breakdown['Volume Interest'] = volume_score
    score += volume_score
    
    # Market Cap Score (10 points)
    market_cap_score = 0
    try:
        market_cap = info.get('marketCap', 0)
        if market_cap > 1000000000000: market_cap_score += 10
        elif market_cap > 100000000000: market_cap_score += 8
        elif market_cap > 10000000000: market_cap_score += 6
        elif market_cap > 1000000000: market_cap_score += 4
        else: market_cap_score += 2
    except:
        pass
    score_breakdown['Market Cap'] = market_cap_score
    score += market_cap_score
    
    return min(score, 100), score_breakdown

def create_glowing_line_chart(stock_data, price_column, title):
    """Create a glowing line chart with cyan/blue colors"""
    if stock_data.empty or len(stock_data) < 2:
        return None
    
    first_price = stock_data[price_column].iloc[0]
    last_price = stock_data[price_column].iloc[-1]
    is_upward = last_price >= first_price
    
    line_color = '#00FFFF' if is_upward else '#FF4757'
    fill_color = 'rgba(0, 255, 255, 0.2)' if is_upward else 'rgba(255, 71, 87, 0.2)'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data[price_column],
        mode='lines',
        name='Price',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': title, 'font': {'size': 16, 'color': 'white'}, 'x': 0.5},
        font=dict(color='white'),
        plot_bgcolor='#000000',
        paper_bgcolor='#0a0e1a',
        height=350,
        xaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True),
        yaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

# Stock Selection with ENHANCED COMPANY INFO
stock_options = {
    "Apple Inc.": {"ticker": "AAPL", "sector": "Technology", "country": "USA"},
    "Microsoft Corp.": {"ticker": "MSFT", "sector": "Technology", "country": "USA"},
    "Amazon.com Inc.": {"ticker": "AMZN", "sector": "E-Commerce", "country": "USA"},
    "Google Inc.": {"ticker": "GOOGL", "sector": "Technology", "country": "USA"},
    "Tesla Inc.": {"ticker": "TSLA", "sector": "Automotive", "country": "USA"},
    "Meta Platforms": {"ticker": "META", "sector": "Social Media", "country": "USA"},
    "Netflix Inc.": {"ticker": "NFLX", "sector": "Entertainment", "country": "USA"},
    "NVIDIA Corp.": {"ticker": "NVDA", "sector": "Semiconductors", "country": "USA"},
    "Infosys Ltd.": {"ticker": "INFY", "sector": "IT Services", "country": "India"},
    "Tata Consultancy Services": {"ticker": "TCS.NS", "sector": "IT Services", "country": "India"},
    "Reliance Industries": {"ticker": "RELIANCE.NS", "sector": "Conglomerate", "country": "India"},
    "HDFC Bank Ltd.": {"ticker": "HDFCBANK.NS", "sector": "Banking", "country": "India"},
    "Adani Enterprises": {"ticker": "ADANIENT.NS", "sector": "Conglomerate", "country": "India"},
    "ICICI Bank Ltd.": {"ticker": "ICICIBANK.NS", "sector": "Banking", "country": "India"},
    "Wipro Ltd.": {"ticker": "WIPRO.NS", "sector": "IT Services", "country": "India"},
    "ITC Ltd.": {"ticker": "ITC.NS", "sector": "FMCG", "country": "India"},
    "State Bank of India": {"ticker": "SBIN.NS", "sector": "Banking", "country": "India"}
}

# ENHANCED COMPANY SELECTOR SECTION
st.markdown("""
<div class="company-selector-container fade-in">
    <div class="company-selector-title">
         Choose Company for Analysis
    </div>
</div>
""", unsafe_allow_html=True)

selector_col1, selector_col2 = st.columns([2, 1])

with selector_col1:
    selected_name = st.selectbox(
        "Select a company to analyze:",
        list(stock_options.keys()),
        key="main_selector",
        label_visibility="collapsed"
    )
    stock_ticker = stock_options[selected_name]["ticker"]
    
    # Display company info
    company_info = stock_options[selected_name]
    st.markdown(f"""
    <div class="company-info-display">
        <div style="text-align: center; margin-bottom: 16px;">
            <h3 style="color: var(--accent-cyan); margin: 0; text-shadow: var(--glow-cyan);">{selected_name}</h3>
        </div>
        <div class="company-info-grid">
            <div class="company-info-item">
                <div class="company-info-label">Ticker</div>
                <div class="company-info-value">{company_info['ticker']}</div>
            </div>
            <div class="company-info-item">
                <div class="company-info-label">Sector</div>
                <div class="company-info-value">{company_info['sector']}</div>
            </div>
            <div class="company-info-item">
                <div class="company-info-label">Country</div>
                <div class="company-info-value">{company_info['country']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with selector_col2:
    if st.button("↻ Refresh Data", use_container_width=True):
        st.session_state.refresh_counter += 1
        st.session_state.last_refresh = datetime.now()
        st.cache_data.clear()
        st.rerun()

# INFO CARD for Company Selector
st.markdown("""
<div class="info-card-permanent">
    <div class="info-card-title">
        ◆ About Company Selection
    </div>
    <div class="info-card-content">
        • Select any company from the dropdown to view detailed analysis<br>
        • Company information includes ticker symbol, sector, and country<br>
        • Real-time data is fetched when you select a company<br>
        • Use the Refresh button to get the latest market data
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch data
with st.spinner(f"Fetching data for {selected_name}..."):
    stock_data, current_price, stock_info = get_latest_stock_data(stock_ticker)
    
    # Fetch categorized news (10-15 articles total)
    company_news = fetch_news_by_category(selected_name, "Company News", 5)
    tech_news = fetch_news_by_category("technology stocks", "Tech News", 5)
    market_news = fetch_news_by_category("stock market", "Market News", 5)
    all_news = company_news + tech_news + market_news

# Currency conversion
if not stock_ticker.endswith(".NS"):
    usd_to_inr = 83.2
    if not stock_data.empty:
        stock_data["Close_INR"] = stock_data["Close"] * usd_to_inr
        stock_data["Open_INR"] = stock_data["Open"] * usd_to_inr
        stock_data["High_INR"] = stock_data["High"] * usd_to_inr
        stock_data["Low_INR"] = stock_data["Low"] * usd_to_inr
    price_column = "Close_INR"
    currency_symbol = "₹"
    current_price_inr = current_price * usd_to_inr if current_price else None
else:
    price_column = "Close"
    currency_symbol = "₹"
    current_price_inr = current_price

# Live Market Ticker Section
st.markdown('<div class="section-header"><span class="icon">◢</span> Top Stocks in the Market</div>', unsafe_allow_html=True)

# INFO CARD
st.markdown("""
<div class="info-card-permanent">
    <div class="info-card-title">
        ◆ Market Indices Overview
    </div>
    <div class="info-card-content">
        • Real-time price updates for major market indices across global markets<br>
        • NIFTY 50 & SENSEX track Indian stock market performance<br>
        • NASDAQ, S&P 500, DOW JONES represent US market health<br>
        • Green (▲) indicates positive movement, Red (▼) indicates decline<br>
        • Percentages show daily change compared to previous close
    </div>
</div>
""", unsafe_allow_html=True)

major_indices = {
    "NIFTY 50": "^NSEI", 
    "SENSEX": "^BSESN", 
    "NASDAQ": "^IXIC", 
    "S&P 500": "^GSPC",
    "DOW JONES": "^DJI"
}

ticker_cols = st.columns(5)

for i, (name, symbol) in enumerate(major_indices.items()):
    with ticker_cols[i]:
        try:
            index_data, index_price, _ = get_latest_stock_data(symbol, "5d")
            if index_price and not index_data.empty and len(index_data) > 1:
                last_close = index_data["Close"].iloc[-2]
                change = index_price - last_close
                change_percent = (change / last_close) * 100 if last_close != 0 else 0
                
                change_color = "var(--success)" if change >= 0 else "var(--danger)"
                arrow = "▲" if change >= 0 else "▼"
                
                st.markdown(f"""
                <div class="ticker-card">
                    <div class="ticker-name">{name}</div>
                    <div class="ticker-price">{index_price:,.0f}</div>
                    <div class="ticker-change" style="color: {change_color};">
                        {arrow} {abs(change_percent):.2f}%
                    </div>
                    <div style="margin-top: 12px; height: 40px; background: var(--bg-secondary); border-radius: 6px;"></div>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown(f"""
            <div class="ticker-card">
                <div class="ticker-name">{name}</div>
                <div style="color: var(--text-muted); font-size: 0.9rem; margin-top: 12px;">Loading...</div>
            </div>
            """, unsafe_allow_html=True)

# Main Tabs
tabs = st.tabs([
    "◆ Dashboard & Market Overview",
    "◈ Company Insights",
    "◭ Trading & Technical Analysis",
    "◉ News & Sentiment Analysis",
    "■ Learning Center",
    "◇ Stock Comparison Tool"
])

# TAB 1: Dashboard & Market Overview
with tabs[0]:
    st.markdown('<div class="section-header"><span class="icon">◆</span> Dashboard & Market Overview</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ Dashboard Guide
        </div>
        <div class="info-card-content">
            • <strong>Global Market Summary:</strong> Track performance of major indices worldwide<br>
            • <strong>System Information:</strong> Monitor data freshness and platform status<br>
            • <strong>Watchlist Management:</strong> Keep track of your favorite stocks in one place<br>
            • <strong>Real-time Updates:</strong> All data refreshes automatically for accuracy
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Global Market Summary
    st.markdown("### ◉ Global Market Summary")
    
    market_cols = st.columns(4)
    
    for i, (name, symbol) in enumerate(list(major_indices.items())[:4]):
        with market_cols[i]:
            try:
                index_data, index_price, _ = get_latest_stock_data(symbol, "5d")
                if index_price and not index_data.empty and len(index_data) > 1:
                    last_close = index_data["Close"].iloc[-2]
                    change = index_price - last_close
                    change_percent = (change / last_close) * 100 if last_close != 0 else 0
                    
                    change_color = "var(--success)" if change >= 0 else "var(--danger)"
                    arrow = "▲" if change >= 0 else "▼"
                    
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div style="font-size: 0.9rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px; text-shadow: var(--glow-cyan);">{name}</div>
                        <div class="metric-value" style="font-size: 1.6rem;">{index_price:,.0f}</div>
                        <div style="color: {change_color}; font-size: 1.1rem; margin-top: 8px; font-weight: 700;">
                            {arrow} {change_percent:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                    <div style="font-size: 0.9rem; font-weight: 700; color: var(--accent-cyan);">{name}</div>
                    <div style="color: var(--text-muted); font-size: 1rem;">Loading...</div>
                </div>
                """, unsafe_allow_html=True)
    
    # System Information
    st.markdown("### ◈ System Information")
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Last Update</div>
            <div style="font-size: 1.2rem; color: var(--accent-cyan); margin-top: 8px; font-family: 'Roboto Mono', monospace; text-shadow: var(--glow-cyan);">{st.session_state.last_refresh.strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Watchlist Items</div>
            <div style="font-size: 1.2rem; color: var(--text-primary); margin-top: 8px;">{len(st.session_state.watchlist)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col3:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Data Source</div>
            <div style="font-size: 1.2rem; color: var(--text-primary); margin-top: 8px;">Yahoo Finance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col4:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Market Status</div>
            <div style="font-size: 1.2rem; color: var(--text-primary); margin-top: 8px;">{market_status}</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: Company Insights
with tabs[1]:
    st.markdown('<div class="section-header"><span class="icon">◈</span> Company Insights</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ Understanding Company Insights
        </div>
        <div class="info-card-content">
            • <strong>Current Price:</strong> Real-time stock price with daily change percentage<br>
            • <strong>Price Movement Chart:</strong> Visual representation of recent stock performance<br>
            • <strong>Company Profile:</strong> Key business information including sector and industry<br>
            • <strong>Valuation Metrics:</strong> P/E Ratio shows price relative to earnings, P/B shows price to book value<br>
            • <strong>Market Data:</strong> Market capitalization indicates company size and stability<br>
            • <strong>AI Analyst Score:</strong> Comprehensive score (0-100) based on multiple factors<br>
            • <strong>Watchlist:</strong> Add stocks to track them easily in your personal list
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price Display
        if current_price and not stock_data.empty and len(stock_data) > 1:
            try:
                last_close = stock_data[price_column].iloc[-2]
                price_change = current_price_inr - last_close
                change_percent = (price_change / last_close) * 100
                
                arrow = "▲" if price_change >= 0 else "▼"
                price_color = "var(--success)" if price_change >= 0 else "var(--danger)"
                
                st.markdown(f"""
                <div class="price-display">
                    <h2 class="company-name">{selected_name}</h2>
                    <div class="current-price" style="color: {price_color};">
                        {currency_symbol}{current_price_inr:.2f}
                    </div>
                    <div class="price-change" style="color: {price_color};">
                        {arrow} {currency_symbol}{abs(price_change):.2f} ({change_percent:+.2f}%)
                    </div>
                    <p style="color: var(--text-muted); margin-top: 20px; font-size: 0.9rem;">
                        Last Updated: {stock_data.index[-1].strftime('%Y-%m-%d %H:%M')} IST
                    </p>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
        
        # Mini Price Chart
        if not stock_data.empty:
            st.markdown("### ◭ Recent Price Movement (Last 30 Days)")
            
            recent_data = stock_data.tail(30)
            fig_mini = create_glowing_line_chart(recent_data, price_column, "")
            if fig_mini:
                st.plotly_chart(fig_mini, use_container_width=True)
        
        # Company Information
        if stock_info:
            st.markdown("### ■ Company Profile")
            
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-cyan); margin-bottom: 12px; text-shadow: var(--glow-cyan);">Business Info</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">Sector:</strong> {stock_info.get("sector", "N/A")}<br>
                        <strong style="color: var(--text-primary);">Industry:</strong> {stock_info.get("industry", "N/A")}<br>
                        <strong style="color: var(--text-primary);">Employees:</strong> {stock_info.get("fullTimeEmployees", "N/A"):,}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col2:
                pe_ratio = stock_info.get("trailingPE", "N/A")
                pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio
                pb_ratio = stock_info.get("priceToBook", "N/A")
                pb_display = f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else pb_ratio
                roe = stock_info.get("returnOnEquity", "N/A")
                roe_display = f"{roe:.2%}" if isinstance(roe, (int, float)) else roe
                
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-cyan); margin-bottom: 12px; text-shadow: var(--glow-cyan);">Valuation Metrics</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">P/E Ratio:</strong> {pe_display}<br>
                        <strong style="color: var(--text-primary);">P/B Ratio:</strong> {pb_display}<br>
                        <strong style="color: var(--text-primary);">ROE:</strong> {roe_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col3:
                market_cap = stock_info.get("marketCap", 0) / 10000000
                high_52 = stock_info.get("fiftyTwoWeekHigh", "N/A")
                high_display = f"₹{high_52:.2f}" if isinstance(high_52, (int, float)) else high_52
                low_52 = stock_info.get("fiftyTwoWeekLow", "N/A")
                low_display = f"₹{low_52:.2f}" if isinstance(low_52, (int, float)) else low_52
                
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-cyan); margin-bottom: 12px; text-shadow: var(--glow-cyan);">Market Data</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">Market Cap:</strong> ₹{market_cap:.1f} Cr<br>
                        <strong style="color: var(--text-primary);">52W High:</strong> {high_display}<br>
                        <strong style="color: var(--text-primary);">52W Low:</strong> {low_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Watchlist Section
        st.markdown("### ◎ My Watchlist")
        
        if st.button(f"+ Add {selected_name}", use_container_width=True):
            if stock_ticker not in [item['symbol'] for item in st.session_state.watchlist]:
                st.session_state.watchlist.append({
                    'symbol': stock_ticker,
                    'name': selected_name,
                    'added_date': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                st.success("✅ Added to watchlist!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.info("ℹ️ Already in watchlist!")
        
        if st.session_state.watchlist:
            for item in st.session_state.watchlist:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"""
                    <div class="glass-card {'compact' if st.session_state.compact_mode else ''}" style="padding: 12px; margin: 8px 0;">
                        <strong style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">{item['name']}</strong><br>
                        <small style="color: var(--text-muted);">{item['added_date']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("×", key=f"del_{item['symbol']}", help="Remove"):
                        st.session_state.watchlist = [i for i in st.session_state.watchlist if i['symbol'] != item['symbol']]
                        st.rerun()
        else:
            st.info("◎ No stocks in watchlist")
        
        # Analyst Score
        st.markdown("### ◆ AI Analyst Score")
        score, breakdown = calculate_enhanced_analyst_score(stock_info, stock_data, all_news)
        
        # Score interpretation
        if score >= 70:
            score_color = "var(--success)"
            score_text = "Strong Buy"
            score_desc = "Highly favorable outlook"
        elif score >= 50:
            score_color = "var(--warning)"
            score_text = "Hold"
            score_desc = "Balanced risk-reward"
        else:
            score_color = "var(--danger)"
            score_text = "Caution"
            score_desc = "Exercise caution"
        
        st.markdown(f"""
        <div class="ai-insight">
            <div class="ai-insight-title">
                <span>◭</span> Overall Investment Score
            </div>
            <div style="text-align: center; margin: 24px 0;">
                <div class="score-gauge" style="--score: {score};">
                    <span class="score-value" style="color: {score_color};">{score}</span>
                </div>
                <div style="margin-top: 16px;">
                    <div style="font-size: 1.4rem; font-weight: 700; color: {score_color};">{score_text}</div>
                    <div style="color: var(--text-secondary); margin-top: 4px;">{score_desc}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Score Breakdown
        st.markdown("#### ◢ Score Breakdown")
        for category, value in breakdown.items():
            max_value = 25 if category in ['Momentum', 'Valuation', 'News Sentiment'] else (15 if category == 'Volume Interest' else 10)
            percentage = (value / max_value) * 100
            bar_color = "var(--success)" if percentage > 70 else ("var(--warning)" if percentage > 40 else "var(--danger)")
            
            st.markdown(f"""
            <div class="glass-card compact">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: var(--text-primary);">{category}</strong>
                    <span style="color: {bar_color}; font-weight: 700; font-family: 'Roboto Mono', monospace;">{value}/{max_value}</span>
                </div>
                <div style="background: var(--bg-secondary); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {bar_color}; width: {percentage}%; height: 100%; transition: width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Stats Panel
        st.markdown("### ◉ Quick Stats")
        if not stock_data.empty and len(stock_data) >= 5:
            try:
                today_high = stock_data[price_column].tail(1).iloc[0]
                today_low = stock_data[price_column].tail(1).iloc[0]
                avg_volume = stock_data['Volume'].tail(20).mean()
                
                st.markdown(f"""
                <div class="glass-card compact">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: var(--text-secondary);">Today's High:</span>
                        <span style="color: var(--success); font-weight: 700;">₹{today_high:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: var(--text-secondary);">Today's Low:</span>
                        <span style="color: var(--danger); font-weight: 700;">₹{today_low:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Avg Volume (20D):</span>
                        <span style="color: var(--text-primary); font-weight: 700;">{int(avg_volume):,}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass

# TAB 3: Trading & Technical Analysis
with tabs[2]:
    st.markdown('<div class="section-header"><span class="icon">◭</span> Trading & Technical Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ Technical Analysis Guide
        </div>
        <div class="info-card-content">
            • <strong>Candlestick Chart:</strong> Shows open, high, low, close prices. Green = price up, Red = price down<br>
            • <strong>Bollinger Bands:</strong> Volatility indicator. Price near upper band = overbought, near lower = oversold<br>
            • <strong>Volume:</strong> Trading activity. High volume confirms price movements<br>
            • <strong>RSI (Relative Strength Index):</strong> >70 overbought (sell signal), <30 oversold (buy signal)<br>
            • <strong>MACD:</strong> Momentum indicator. MACD line above signal = bullish, below = bearish<br>
            • <strong>Trading Performance Table:</strong> Historical price data with daily changes
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not stock_data.empty and len(stock_data) > 10:
        try:
            close_prices = stock_data[price_column]
            
            # Calculate indicators
            rsi = calculate_rsi(close_prices)
            macd_line, signal_line, histogram = calculate_macd(close_prices)
            upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(close_prices)
            
            # Create comprehensive chart with COLORFUL CANDLESTICKS
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=('Candlestick Chart with Bollinger Bands', 'Volume', 'RSI', 'MACD'),
                vertical_spacing=0.08,
                row_heights=[0.4, 0.2, 0.2, 0.2]
            )
            
            # Colorful Candlestick Chart
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'] if 'Open' in stock_data.columns else stock_data[price_column],
                high=stock_data['High'] if 'High' in stock_data.columns else stock_data[price_column],
                low=stock_data['Low'] if 'Low' in stock_data.columns else stock_data[price_column],
                close=stock_data[price_column],
                name='Price',
                increasing_line_color='#00FFFF',
                increasing_fillcolor='#00FFFF',
                decreasing_line_color='#FF4757',
                decreasing_fillcolor='#FF4757',
                increasing_line_width=2,
                decreasing_line_width=2
            ), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=stock_data.index, y=upper_bb, name='Upper BB', 
                                    line=dict(color='rgba(255,255,255,0.3)', dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=lower_bb, fill='tonexty', name='Lower BB',
                                    line=dict(color='rgba(255,255,255,0.3)', dash='dash'),
                                    fillcolor='rgba(0, 255, 255, 0.1)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=middle_bb, name='SMA 20',
                                    line=dict(color='#00FFFF', width=2)), row=1, col=1)
            
            # Volume
            colors = ['#00FFFF' if stock_data[price_column].iloc[i] >= stock_data[price_column].iloc[i-1] 
                     else '#FF4757' for i in range(1, len(stock_data))]
            colors.insert(0, '#FF4757')
            fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], name='Volume',
                                marker_color=colors, opacity=0.7), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=stock_data.index, y=rsi, name='RSI',
                                    line=dict(color='#00FFFF', width=3)), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#FF4757", line_width=2, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00FF88", line_width=2, row=3, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=stock_data.index, y=macd_line, name='MACD',
                                    line=dict(color='#00FFFF', width=3)), row=4, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=signal_line, name='Signal',
                                    line=dict(color='#FFA502', width=2)), row=4, col=1)
            colors_hist = ['#00FF88' if h >= 0 else '#FF4757' for h in histogram]
            fig.add_trace(go.Bar(x=stock_data.index, y=histogram, name='Histogram',
                                marker_color=colors_hist, opacity=0.6), row=4, col=1)
            
            fig.update_layout(
                title={'text': f'{selected_name} - Technical Analysis Dashboard', 
                      'font': {'size': 22, 'color': 'white'}, 'x': 0.5},
                font=dict(color='white'),
                plot_bgcolor='#000000',
                paper_bgcolor='#0a0e1a',
                height=1100,
                showlegend=True,
                hovermode='x unified',
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True)
            fig.update_yaxes(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical Indicators Summary
            st.markdown("### ◎ Technical Indicators Summary")
            ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)
            
            with ind_col1:
                current_rsi = rsi.iloc[-1] if not rsi.empty and pd.notna(rsi.iloc[-1]) else None
                if current_rsi:
                    rsi_signal = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
                    rsi_color = "var(--danger)" if current_rsi > 70 else "var(--success)" if current_rsi < 30 else "var(--warning)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {rsi_color};">{current_rsi:.1f}</div>
                        <div class="metric-label">RSI</div>
                        <div style="color: {rsi_color}; font-size: 0.9rem; margin-top: 8px; font-weight: 600;">{rsi_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col2:
                current_macd = macd_line.iloc[-1] if not macd_line.empty and pd.notna(macd_line.iloc[-1]) else None
                current_signal = signal_line.iloc[-1] if not signal_line.empty and pd.notna(signal_line.iloc[-1]) else None
                if current_macd and current_signal:
                    macd_signal = "Bullish" if current_macd > current_signal else "Bearish"
                    macd_color = "var(--success)" if current_macd > current_signal else "var(--danger)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {macd_color};">{current_macd:.2f}</div>
                        <div class="metric-label">MACD</div>
                        <div style="color: {macd_color}; font-size: 0.9rem; margin-top: 8px; font-weight: 600;">{macd_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col3:
                current_price_val = close_prices.iloc[-1]
                current_bb_upper = upper_bb.iloc[-1] if not upper_bb.empty else None
                current_bb_lower = lower_bb.iloc[-1] if not lower_bb.empty else None
                if current_bb_upper and current_bb_lower:
                    bb_position = ((current_price_val - current_bb_lower) / (current_bb_upper - current_bb_lower)) * 100
                    if current_price_val > current_bb_upper:
                        bb_signal = "Above Upper"
                        bb_color = "var(--danger)"
                    elif current_price_val < current_bb_lower:
                        bb_signal = "Below Lower"
                        bb_color = "var(--success)"
                    else:
                        bb_signal = "Within Bands"
                        bb_color = "var(--warning)"
                    
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {bb_color};">{bb_position:.1f}%</div>
                        <div class="metric-label">BB Position</div>
                        <div style="color: {bb_color}; font-size: 0.9rem; margin-top: 8px; font-weight: 600;">{bb_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col4:
                if 'Volume' in stock_data.columns:
                    current_volume = stock_data['Volume'].iloc[-1]
                    avg_volume_20 = stock_data['Volume'].tail(min(20, len(stock_data))).mean()
                    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
                    volume_signal = "High" if volume_ratio > 1.5 else "Low" if volume_ratio < 0.7 else "Normal"
                    volume_color = "var(--success)" if volume_ratio > 1.5 else "var(--danger)" if volume_ratio < 0.7 else "var(--warning)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {volume_color};">{volume_ratio:.1f}x</div>
                        <div class="metric-label">Volume Ratio</div>
                        <div style="color: {volume_color}; font-size: 0.9rem; margin-top: 8px; font-weight: 600;">{volume_signal}</div>
		</div>
                    """, unsafe_allow_html=True)
            
            # Recent Trading Performance Table
            st.markdown("### ◢ Recent Trading Performance")
            
            if not stock_data.empty:
                try:
                    last_10 = stock_data.tail(10).copy()
                    display_data = []
                    
                    for idx in last_10.index:
                        row_data = last_10.loc[idx]
                        
                        if price_column == "Close_INR":
                            open_price = row_data.get("Open_INR", row_data.get("Open", 0) * 83.2)
                            high_price = row_data.get("High_INR", row_data.get("High", 0) * 83.2)
                            low_price = row_data.get("Low_INR", row_data.get("Low", 0) * 83.2)
                            close_price = row_data.get("Close_INR", row_data.get("Close", 0) * 83.2)
                        else:
                            open_price = row_data.get("Open", 0)
                            high_price = row_data.get("High", 0)
                            low_price = row_data.get("Low", 0)
                            close_price = row_data.get("Close", 0)
                        
                        volume = row_data.get("Volume", 0)
                        
                        display_data.append({
                            "Date": idx.strftime('%Y-%m-%d'),
                            "Open (₹)": f"₹{open_price:.2f}",
                            "High (₹)": f"₹{high_price:.2f}",
                            "Low (₹)": f"₹{low_price:.2f}",
                            "Close (₹)": f"₹{close_price:.2f}",
                            "Volume": f"{int(volume):,}",
                        })
                    
                    for i in range(1, len(display_data)):
                        prev_close = float(display_data[i-1]["Close (₹)"].replace("₹", "").replace(",", ""))
                        curr_close = float(display_data[i]["Close (₹)"].replace("₹", "").replace(",", ""))
                        
                        daily_change = curr_close - prev_close
                        change_percent = (daily_change / prev_close * 100) if prev_close != 0 else 0
                        
                        display_data[i]["Daily Change"] = f"₹{daily_change:+.2f}"
                        display_data[i]["Change %"] = f"{change_percent:+.2f}%"
                    
                    display_data[0]["Daily Change"] = "N/A"
                    display_data[0]["Change %"] = "N/A"
                    
                    display_df = pd.DataFrame(display_data)
                    display_df = display_df.set_index("Date")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=450
                    )
                    
                except Exception as e:
                    st.error(f"⚠️ Error displaying trading data: {str(e)}")
                    
        except Exception as e:
            st.error(f"⚠️ Error creating technical analysis: {e}")
    else:
        st.markdown("""
        <div class="info-card-permanent">
            <div class="info-card-title">ℹ️ Limited Data Available</div>
            <div class="info-card-content">
                Displaying available data with reduced timeframe. Some technical indicators may have limited accuracy with fewer data points.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show whatever data is available
        if not stock_data.empty:
            fig_simple = create_glowing_line_chart(stock_data, price_column, f"{selected_name} - Price Movement")
            if fig_simple:
                st.plotly_chart(fig_simple, use_container_width=True)

# TAB 4: News & Sentiment Analysis
with tabs[3]:
    st.markdown('<div class="section-header"><span class="icon">◉</span> News & Sentiment Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ News & Sentiment Analysis Guide
        </div>
        <div class="info-card-content">
            • <strong>Sentiment Analysis:</strong> AI analyzes news tone (Positive/Negative/Neutral)<br>
            • <strong>Company News:</strong> Latest updates specifically about the selected company<br>
            • <strong>Tech News:</strong> Technology sector news affecting tech stocks<br>
            • <strong>Market News:</strong> General stock market trends and economic updates<br>
            • <strong>Overall Sentiment:</strong> Aggregate sentiment helps gauge market psychology<br>
            • <strong>Source & Time:</strong> Each article shows original source and publication time
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sentiment Analysis Overview
    st.markdown("### ◭ Sentiment Summary")
    
    if all_news:
        positive_count = sum(1 for news in all_news if "Positive" in news["Sentiment"])
        negative_count = sum(1 for news in all_news if "Negative" in news["Sentiment"])
        neutral_count = len(all_news) - positive_count - negative_count
        
        sent_col1, sent_col2, sent_col3, sent_col4 = st.columns(4)
        
        with sent_col1:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--success);">{positive_count}</div>
                <div class="metric-label">Positive News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col2:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--warning);">{neutral_count}</div>
                <div class="metric-label">Neutral News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col3:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--danger);">{negative_count}</div>
                <div class="metric-label">Negative News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col4:
            overall = "Positive" if positive_count > negative_count else "Negative" if negative_count > positive_count else "Neutral"
            color = "var(--success)" if overall == "Positive" else "var(--danger)" if overall == "Negative" else "var(--warning)"
            
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: {color}; font-size: 1.5rem;">{overall}</div>
                <div class="metric-label">Overall Sentiment</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sentiment Distribution Chart
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_sentiment = go.Figure(data=[go.Pie(
                labels=['Positive', 'Neutral', 'Negative'],
                values=[positive_count, neutral_count, negative_count],
                marker_colors=['#00FF88', '#FFA502', '#FF4757'],
                hole=.4,
                textfont_size=14,
                textfont_color='white'
            )])
            
            fig_sentiment.update_layout(
                title="Sentiment Distribution",
                font=dict(color='white'),
                paper_bgcolor='#0a0e1a',
                plot_bgcolor='#000000',
                height=400
            )
            
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col_chart2:
            # Category distribution
            category_counts = {}
            for news in all_news:
                cat = news.get("Category", "Other")
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            fig_category = go.Figure(data=[go.Bar(
                x=list(category_counts.keys()),
                y=list(category_counts.values()),
                marker_color='#00FFFF',
                text=list(category_counts.values()),
                textposition='auto',
            )])
            
            fig_category.update_layout(
                title="News by Category",
                font=dict(color='white'),
                paper_bgcolor='#0a0e1a',
                plot_bgcolor='#000000',
                height=400,
                xaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)', title="Count")
            )
            
            st.plotly_chart(fig_category, use_container_width=True)
        
        # NEWS CATEGORIES IN TABS
        st.markdown("### ◎ Latest News Articles")
        
        news_tabs = st.tabs(["📰 Company News", "💻 Tech News", "📊 Market News"])
        
        with news_tabs[0]:
            st.markdown(f"#### Company News for {selected_name}")
            company_articles = [n for n in all_news if n.get("Category") == "Company News"]
            
            if company_articles:
                for news in company_articles:
                    sentiment_class = "sentiment-neutral"
                    if "Positive" in news["Sentiment"]:
                        sentiment_class = "sentiment-positive"
                    elif "Negative" in news["Sentiment"]:
                        sentiment_class = "sentiment-negative"
                    
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">{news['Title']}</div>
                        <div class="news-description">{news['Description'][:200]}... 
                            <a href="{news['Url']}" target="_blank" style="color: var(--accent-cyan); font-weight: 600; text-decoration: none;">
                                Read Full Article →
                            </a>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-subtle);">
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <span class="news-category-badge">Company News</span>
                                <span class="{sentiment_class}">
                                    {news['Sentiment']}
                                </span>
                                <span style="color: var(--accent-cyan); font-weight: 600;">◉ {news['Source']}</span>
                            </div>
                            <div style="color: var(--text-muted); font-size: 0.85rem;">■ {news['Time']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No company news available at the moment.")
        
        with news_tabs[1]:
            st.markdown("#### Technology Sector News")
            tech_articles = [n for n in all_news if n.get("Category") == "Tech News"]
            
            if tech_articles:
                for news in tech_articles:
                    sentiment_class = "sentiment-neutral"
                    if "Positive" in news["Sentiment"]:
                        sentiment_class = "sentiment-positive"
                    elif "Negative" in news["Sentiment"]:
                        sentiment_class = "sentiment-negative"
                    
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">{news['Title']}</div>
                        <div class="news-description">{news['Description'][:200]}... 
                            <a href="{news['Url']}" target="_blank" style="color: var(--accent-cyan); font-weight: 600; text-decoration: none;">
                                Read Full Article →
                            </a>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-subtle);">
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <span class="news-category-badge" style="background: linear-gradient(135deg, #0080FF, #00FFFF);">Tech News</span>
                                <span class="{sentiment_class}">
                                    {news['Sentiment']}
                                </span>
                                <span style="color: var(--accent-cyan); font-weight: 600;">◉ {news['Source']}</span>
                            </div>
                            <div style="color: var(--text-muted); font-size: 0.85rem;">■ {news['Time']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tech news available at the moment.")
        
        with news_tabs[2]:
            st.markdown("#### General Market News")
            market_articles = [n for n in all_news if n.get("Category") == "Market News"]
            
            if market_articles:
                for news in market_articles:
                    sentiment_class = "sentiment-neutral"
                    if "Positive" in news["Sentiment"]:
                        sentiment_class = "sentiment-positive"
                    elif "Negative" in news["Sentiment"]:
                        sentiment_class = "sentiment-negative"
                    
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title">{news['Title']}</div>
                        <div class="news-description">{news['Description'][:200]}... 
                            <a href="{news['Url']}" target="_blank" style="color: var(--accent-cyan); font-weight: 600; text-decoration: none;">
                                Read Full Article →
                            </a>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-subtle);">
                            <div style="display: flex; align-items: center; gap: 16px;">
                                <span class="news-category-badge" style="background: linear-gradient(135deg, #FFA502, #FF4757);">Market News</span>
                                <span class="{sentiment_class}">
                                    {news['Sentiment']}
                                </span>
                                <span style="color: var(--accent-cyan); font-weight: 600;">◉ {news['Source']}</span>
                            </div>
                            <div style="color: var(--text-muted); font-size: 0.85rem;">■ {news['Time']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No market news available at the moment.")
    else:
        st.info("ℹ️ Unable to fetch news at the moment. Please refresh the page.")

# TAB 5: Learning Center
with tabs[4]:
    st.markdown('<div class="section-header"><span class="icon">■</span> Learning Center</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ Your Learning Journey Starts Here
        </div>
        <div class="info-card-content">
            • <strong>Video Tutorials:</strong> Curated educational content in English, Tamil, Malayalam, and Hindi<br>
            • <strong>Stock Market Basics:</strong> Understand fundamental concepts before investing<br>
            • <strong>Key Concepts:</strong> Learn about P/E ratios, market cap, IPOs, and more<br>
            • <strong>Common Mistakes:</strong> Avoid pitfalls that trap beginner investors<br>
            • <strong>Pro Tips:</strong> Professional strategies to improve your trading success<br>
            • <strong>Multi-language Support:</strong> Learn in your preferred language for better understanding
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: var(--accent-cyan); margin-bottom: 20px; text-shadow: var(--glow-cyan);">◭ Master the Stock Market</h3>
        <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.8;">
            Welcome to your comprehensive guide to stock market investing. Whether you're a complete beginner 
            or looking to enhance your knowledge, we've got you covered with curated video tutorials and 
            expert insights in multiple languages!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Video Tutorials Section
    st.markdown("### ◎ Video Tutorials")
    
    # Language tabs - NOW WITH MALAYALAM
    lang_tabs = st.tabs(["◆ English", "◆ Tamil", "◆ Malayalam", "◆ Hindi"])
    
    # English Videos
    with lang_tabs[0]:
        st.markdown("#### English Tutorials")
        
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        
        with eng_col1:
            st.markdown("""
            <div class="video-card">
                <h4>Stock Market for Beginners</h4>
                <p>Complete guide to understanding stock market basics and building wealth.</p>
                <a href="https://youtu.be/p7HKvqRI_Bo" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with eng_col2:
            st.markdown("""
            <div class="video-card">
                <h4>How to Invest in Stocks</h4>
                <p>Step-by-step guide on choosing stocks and making your first investment.</p>
                <a href="https://youtu.be/8Ij7A1VCB7I" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with eng_col3:
            st.markdown("""
            <div class="video-card">
                <h4>Candlestick Patterns</h4>
                <p>Master candlestick chart reading and make informed trading decisions.</p>
                <a href="https://youtu.be/tW13N4Hll88" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # Tamil Videos
    with lang_tabs[1]:
        st.markdown("#### Tamil Tutorials")
        
        tam_col1, tam_col2, tam_col3 = st.columns(3)
        
        with tam_col1:
            st.markdown("""
            <div class="video-card">
                <h4>பங்கு சந்தை அடிப்படைகள்</h4>
                <p>தொடக்கநிலையாளர்களுக்கான பங்கு சந்தை முழுமையான வழிகாட்டி</p>
                <a href="https://youtu.be/RfOKl-ya5BY" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with tam_col2:
            st.markdown("""
            <div class="video-card">
                <h4>பங்கு முதலீடு எப்படி செய்வது</h4>
                <p>பங்குகளை தேர்வு செய்தல் மற்றும் முதலீடு செய்வதற்கான வழிமுறைகள்</p>
                <a href="https://youtu.be/64SziSDJTNU" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with tam_col3:
            st.markdown("""
            <div class="video-card">
                <h4>கேண்டில்ஸ்டிக் வாசிப்பு</h4>
                <p>கேண்டில்ஸ்டிக் விளக்கப்படங்களை படிக்க கற்றுக்கொள்ளுங்கள்</p>
                <a href="https://youtu.be/Jpvi6r4wCvA" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # MALAYALAM Videos (NEW)
    with lang_tabs[2]:
        st.markdown("#### Malayalam Tutorials")
        
        mal_col1, mal_col2, mal_col3 = st.columns(3)
        
        with mal_col1:
            st.markdown("""
            <div class="video-card">
                <h4>Stock Market for Beginners</h4>
                <p>തുടക്കക്കാർക്കുള്ള സ്റ്റോക്ക് മാർക്കറ്റ് പൂർണ്ണ ഗൈഡ്</p>
                <a href="https://youtu.be/UJFD32F521U?si=gRa5NPUxIr4tiK5w" target="_blank" style="text-decoration: none;">
                    <button>▶ വീഡിയോ കാണുക</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with mal_col2:
            st.markdown("""
            <div class="video-card">
                <h4>How to Invest in Share Market</h4>
                <p>ഷെയർ മാർക്കറ്റിൽ നിക്ഷേപിക്കുന്നതെങ്ങനെ</p>
                <a href="https://youtu.be/rB5VAcFcQ1k?si=2wQc7TBS2v0OOB0e" target="_blank" style="text-decoration: none;">
                    <button>▶ വീഡിയോ കാണുക</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with mal_col3:
            st.markdown("""
            <div class="video-card">
                <h4>How to Read Candlestick</h4>
                <p>കാൻഡിൽസ്റ്റിക്ക് ചാർട്ട് വായിക്കുന്നതെങ്ങനെ</p>
                <a href="https://youtu.be/9126111ubPo?si=QoXYSQrLyQCdjiXM" target="_blank" style="text-decoration: none;">
                    <button>▶ വീഡിയോ കാണുക</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # Hindi Videos
    with lang_tabs[3]:
        st.markdown("#### Hindi Tutorials")
        
        hin_col1, hin_col2, hin_col3 = st.columns(3)
        
        with hin_col1:
            st.markdown("""
            <div class="video-card">
                <h4>शेयर बाजार की बुनियादी बातें</h4>
                <p>शुरुआती लोगों के लिए शेयर बाजार की संपूर्ण गाइड</p>
                <a href="https://youtu.be/hsbhN7i7H8E" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with hin_col2:
            st.markdown("""
            <div class="video-card">
                <h4>शेयर में निवेश कैसे करें</h4>
                <p>शेयर चुनने और निवेश करने के लिए चरण-दर-चरण मार्गदर्शिका</p>
                <a href="https://youtu.be/BeVw7UH_i9U" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with hin_col3:
            st.markdown("""
            <div class="video-card">
                <h4>कैंडलस्टिक चार्ट पढ़ना</h4>
                <p>कैंडलस्टिक चार्ट और पैटर्न को समझें और सीखें</p>
                <a href="https://youtu.be/lQpulkxLHe0" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Educational Content
    st.markdown("### ◢ Educational Resources")
    
    learn_tabs = st.tabs([
        "◆ Basics",
        "◈ Key Concepts",
        "◭ Common Mistakes",
        "◉ Pro Tips"
    ])
    
    with learn_tabs[0]:
        st.markdown("#### Stock Market Fundamentals")
        
        basics_col1, basics_col2 = st.columns(2)
        
        with basics_col1:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: var(--accent-cyan); margin-bottom: 16px; text-shadow: var(--glow-cyan);">◆ What is a Stock?</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    A stock represents ownership in a company. When you buy a stock, you become a partial owner 
                    (shareholder) of that company. As the company grows and becomes more valuable, your stock 
                    can increase in value too.
                </p>
                <br>
                <h4 style="color: var(--accent-cyan); margin-bottom: 16px; text-shadow: var(--glow-cyan);">◈ How Does Trading Work?</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    Trading involves buying and selling stocks through stock exchanges (like NSE and BSE in India). 
                    You place orders through a broker, and trades are executed when buyers and sellers agree on a price.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with basics_col2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: var(--accent-cyan); margin-bottom: 16px; text-shadow: var(--glow-cyan);">◭ Bull vs Bear Markets</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    <strong style="color: var(--success);">Bull Market:</strong> Period of rising stock prices, 
                    investor optimism, and economic growth. Investors are confident and buying.<br><br>
                    <strong style="color: var(--danger);">Bear Market:</strong> Period of falling stock prices (usually 
                    20%+ decline), pessimism, and economic concerns. Investors are cautious and selling.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: var(--accent-cyan); margin-bottom: 20px; text-shadow: var(--glow-cyan);">◉ Technical vs Fundamental Analysis</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px;">
                <div style="border-left: 4px solid var(--accent-cyan); padding-left: 16px;">
                    <h5 style="color: var(--text-primary); margin-bottom: 12px;">Technical Analysis</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Studies price movements, charts, and patterns to predict future price movements. 
                        Uses indicators like RSI, MACD, moving averages. Best for short-term trading.
                    </p>
                </div>
                <div style="border-left: 4px solid var(--accent-cyan); padding-left: 16px;">
                    <h5 style="color: var(--text-primary); margin-bottom: 12px;">Fundamental Analysis</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Evaluates company's financial health, earnings, management, industry position. 
                        Uses ratios like P/E, ROE, debt-to-equity. Best for long-term investing.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with learn_tabs[1]:
        st.markdown("#### Essential Stock Market Concepts")
        
        concept_col1, concept_col2 = st.columns(2)
        
        with concept_col1:
            concepts = {
                "Market Capitalization": "Total value of all company shares. Large-cap (>₹20,000 Cr), Mid-cap (₹5,000-20,000 Cr), Small-cap (<₹5,000 Cr)",
                "P/E Ratio": "Price-to-Earnings ratio. Shows how much investors pay per rupee of earnings. Lower P/E may indicate undervaluation.",
                "Dividend": "Portion of company profits distributed to shareholders. Provides regular income along with potential capital gains."
            }
            
            for term, explanation in concepts.items():
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-cyan); margin-bottom: 10px; text-shadow: var(--glow-cyan);">◆ {term}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{explanation}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with concept_col2:
            concepts2 = {
                "IPO": "Initial Public Offering - when a private company first sells shares to the public, becoming a publicly traded company.",
                "Volatility": "Measure of price fluctuation. High volatility means bigger price swings, higher risk but potential for higher returns.",
                "Liquidity": "How easily you can buy or sell a stock without affecting its price. High liquidity means you can trade quickly at fair prices."
            }
            
            for term, explanation in concepts2.items():
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-cyan); margin-bottom: 10px; text-shadow: var(--glow-cyan);">◆ {term}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{explanation}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with learn_tabs[2]:
        st.markdown("#### Common Beginner Mistakes to Avoid")
        
        mistakes = [
            ("Investing Without Research", "Never invest in a company without understanding its business model, financials, and future prospects."),
            ("Emotional Trading", "Don't let fear or greed drive your decisions. Stick to your investment plan and strategy."),
            ("Following Tips Blindly", "Avoid investing based on hot tips from friends or social media without your own analysis."),
            ("Not Diversifying", "Don't put all your money in one stock. Spread investments across sectors to reduce risk."),
            ("Trying to Time the Market", "Consistently predicting market tops and bottoms is nearly impossible. Focus on time IN the market."),
            ("Overtrading", "Frequent buying and selling increases costs and rarely beats a disciplined long-term approach."),
            ("Ignoring Risk Management", "Always set stop losses and never invest more than you can afford to lose."),
            ("Reacting to News Impulsively", "Market news often creates short-term volatility. Focus on long-term fundamentals.")
        ]
        
        for i in range(0, len(mistakes), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                title, desc = mistakes[i]
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid var(--danger);">
                    <h5 style="color: var(--danger); margin-bottom: 10px;">× {title}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if i + 1 < len(mistakes):
                with col2:
                    title, desc = mistakes[i + 1]
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--danger);">
                        <h5 style="color: var(--danger); margin-bottom: 10px;">× {title}</h5>
                        <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with learn_tabs[3]:
        st.markdown("#### Professional Trading Tips")
        
        tips = [
            ("Create an Investment Plan", "Define your goals, risk tolerance, time horizon, and investment strategy before you start."),
            ("Set Realistic Expectations", "Aim for consistent 12-15% annual returns rather than chasing unrealistic 100% gains."),
            ("Never Stop Learning", "Markets evolve constantly. Keep educating yourself through books, courses, and analysis."),
            ("Start Small", "Begin with amounts you're comfortable losing while you learn. Gradually increase as you gain experience."),
            ("Track Your Performance", "Maintain a trading journal. Analyze your wins and losses to improve your strategy."),
            ("Do Your Due Diligence", "Read annual reports, understand company financials, and analyze industry trends before investing."),
            ("Be Patient", "Wealth creation through stocks takes time. Avoid the temptation of quick gains."),
            ("Use Stop Losses", "Protect your capital by setting automatic sell orders at predetermined loss levels.")
        ]
        
        for i in range(0, len(tips), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                title, desc = tips[i]
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid var(--success);">
                    <h5 style="color: var(--success); margin-bottom: 10px;">✓ {title}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if i + 1 < len(tips):
                with col2:
                    title, desc = tips[i + 1]
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--success);">
                        <h5 style="color: var(--success); margin-bottom: 10px;">✓ {title}</h5>
                        <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)

# TAB 6: Stock Comparison Tool
with tabs[5]:
    st.markdown('<div class="section-header"><span class="icon">◇</span> Stock Comparison Tool</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card-permanent">
        <div class="info-card-title">
            ◆ Stock Comparison Guide
        </div>
        <div class="info-card-content">
            • <strong>Compare Up to 3 Stocks:</strong> Analyze multiple companies side-by-side<br>
            • <strong>Key Metrics Comparison:</strong> View price, market cap, P/E ratio, and more<br>
            • <strong>Price Chart Comparison:</strong> Visual comparison of 30-day price movements<br>
            • <strong>Sector Analysis:</strong> Compare companies within same or different sectors<br>
            • <strong>Make Informed Decisions:</strong> Use comparative data to choose best investments
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stock Selection for Comparison
    st.markdown("### ◎ Select Stocks to Compare")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        stock1 = st.selectbox("Stock 1", list(stock_options.keys()), key="comp1")
    with comp_col2:
        stock2 = st.selectbox("Stock 2", list(stock_options.keys()), index=1, key="comp2")
    with comp_col3:
        stock3 = st.selectbox("Stock 3 (Optional)", ["None"] + list(stock_options.keys()), key="comp3")
    
    if st.button("◭ Compare Stocks", use_container_width=True):
        stocks_to_compare = [stock1, stock2]
        if stock3 != "None":
            stocks_to_compare.append(stock3)
        
        # Fetch data for all selected stocks
        comparison_data = []
        
        for stock_name in stocks_to_compare:
            ticker = stock_options[stock_name]["ticker"]
            data, price, info = get_latest_stock_data(ticker, "1mo")
            
            if not ticker.endswith(".NS") and price:
                price = price * 83.2
            
            if price and info:
                comparison_data.append({
                    "Company": stock_name,
                    "Current Price (₹)": f"₹{price:.2f}" if price else "N/A",
                    "Market Cap (Cr)": f"₹{info.get('marketCap', 0) / 10000000:.1f}" if info.get('marketCap') else "N/A",
                    "P/E Ratio": f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "N/A",
                    "P/B Ratio": f"{info.get('priceToBook', 'N/A'):.2f}" if isinstance(info.get('priceToBook'), (int, float)) else "N/A",
                    "52W High (₹)": f"₹{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A",
                    "52W Low (₹)": f"₹{info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekLow'), (int, float)) else "N/A",
                    "Sector": info.get('sector', 'N/A'),
                    "Industry": info.get('industry', 'N/A')
                })
        
        if comparison_data:
            st.markdown("### ◢ Comparison Results")
            
            # Create comparison table
            df_comparison = pd.DataFrame(comparison_data)
            df_comparison = df_comparison.set_index("Company")
            
            st.dataframe(df_comparison, use_container_width=True, height=400)
            
            # Price comparison chart
            st.markdown("### ◭ Price Comparison (Last 30 Days)")
            
            fig_comparison = go.Figure()
            
            colors_list = ['#00FFFF', '#00FF88', '#FFA502']
            
            for idx, stock_name in enumerate(stocks_to_compare):
                ticker = stock_options[stock_name]["ticker"]
                data, _, _ = get_latest_stock_data(ticker, "1mo")
                
                if not data.empty:
                    price_col = "Close"
                    if not ticker.endswith(".NS"):
                        data["Close"] = data["Close"] * 83.2
                    
                    fig_comparison.add_trace(go.Scatter(
                        x=data.index,
                        y=data["Close"],
                        mode='lines',
                        name=stock_name,
                        line=dict(width=3, color=colors_list[idx % len(colors_list)]),
                        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:.2f}<extra></extra>'
                    ))
            
            fig_comparison.update_layout(
                title={'text': 'Stock Price Comparison', 'font': {'size': 20, 'color': 'white'}, 'x': 0.5},
                font=dict(color='white'),
                plot_bgcolor='#000000',
                paper_bgcolor='#0a0e1a',
                height=550,
                xaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True, title="Date"),
                yaxis=dict(gridcolor='rgba(0, 255, 255, 0.1)', showgrid=True, title="Price (₹)"),
                hovermode='x unified',
                legend=dict(
                    bgcolor='rgba(13, 21, 38, 0.8)',
                    bordercolor='var(--accent-cyan)',
                    borderwidth=2,
                    font=dict(size=12)
                )
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.warning("⚠️ Unable to fetch comparison data. Please try again.")

# Footer
st.markdown("""
<div style="margin-top: 80px; padding: 40px 0; border-top: 3px solid var(--accent-cyan); text-align: center;">
    <h2 style="color: var(--accent-cyan); margin-bottom: 20px; font-size: 2.5rem; text-shadow: var(--glow-cyan);">STOCKSENTINEL</h2>
    <p style="color: var(--text-secondary); font-size: 1.2rem; margin-bottom: 24px;">
        <strong style="color: var(--accent-cyan);">Learning & Trading Intelligence</strong>
    </p>
    <div style="display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; margin-bottom: 24px;">
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◆</span> Real-time Data
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◉</span> News Analysis
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◭</span> Technical Indicators
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◈</span> AI Insights
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◎</span> Watchlist
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">■</span> Learning Hub
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-cyan); text-shadow: var(--glow-cyan);">◇</span> Stock Comparison
        </span>
    </div>
    <div style="background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(0, 128, 255, 0.05)); border: 2px solid var(--accent-cyan); border-radius: 16px; padding: 28px; margin: 24px auto; max-width: 900px; box-shadow: var(--glow-cyan);">
        <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.8; margin: 0;">
            <strong style="color: var(--warning);">⚠️ Disclaimer:</strong> This tool is designed for educational and informational purposes only. 
            Stock market investments involve substantial risk. Past performance does not guarantee future results. 
            Always consult with qualified financial advisors before making investment decisions. 
            The creators of this tool are not responsible for any financial losses.
        </p>
    </div>
    <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 24px;">
        Built with ❤️ using Streamlit | Powered by yfinance & NewsAPI
    </p>
    <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 12px;">
        © 2024 StockSentinel. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)

# System Online Indicator
st.markdown(f"""
<div style="position: fixed; bottom: 20px; right: 20px; background: linear-gradient(135deg, var(--bg-card), var(--bg-navy)); 
     color: white; padding: 14px 24px; border: 2px solid var(--accent-cyan); border-radius: 12px; font-size: 0.9rem; z-index: 1000; 
     box-shadow: var(--glow-cyan);">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div class="status-indicator status-online"></div>
        <span style="color: var(--accent-cyan); font-weight: 700;">System Online | {current_time_ist.strftime('%H:%M:%S')}</span>
    </div>
</div>
""", unsafe_allow_html=True)
			