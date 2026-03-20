"""
Stock Prediction Lab 2026 - With Sentiment Analysis
Fonts: IBM Plex Mono (data/labels) + Manrope (body/headings)
Matches Alpha Terminal visual identity exactly.
"""
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import xgboost as xgb
import re
import json

try:
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import (
        LSTM, Dense, Dropout, Bidirectional,
        MultiHeadAttention, LayerNormalization,
        Input, GlobalAveragePooling1D, Concatenate, Lambda
    )
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.optimizers import Adam
    import tensorflow as tf
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False


# ═══════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="Stock Prediction Lab 2026",
    page_icon="📈", layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════
#  GLOBAL CSS — IBM Plex Mono + Manrope
#  Identical font system to Alpha Terminal
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }

/* ── App background ─────────────────── */
[data-testid="stAppViewContainer"] { background: #060b14; }
[data-testid="block-container"]    { padding-top: 1rem; padding-bottom: 1rem; }
.main { background: #060b14; }

/* ── Sidebar ────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070d1a 0%, #080f1f 100%);
    border-right: 1px solid rgba(100,255,218,.08);
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h2 {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #64ffda !important;
    font-size: .85rem !important;
    letter-spacing: .08em;
    text-transform: uppercase;
}

/* ── Banner (top info strip) ─────────── */
.banner {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%);
    border: 1px solid rgba(255,255,255,.06);
    border-left: 4px solid #64ffda;
    border-radius: 12px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.bl {
    font-family: 'IBM Plex Mono', monospace;
    color: #475569;
    font-size: .57rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.bv {
    font-family: 'IBM Plex Mono', monospace;
    color: #64ffda;
    font-size: 1.15rem;
    font-weight: 700;
    line-height: 1.1;
}
.bn {
    font-family: 'Manrope', sans-serif;
    color: #e2e8f0;
    font-size: .9rem;
    font-weight: 600;
}
.bt {
    display: inline-block;
    background: rgba(100,255,218,.08);
    color: #64ffda;
    border: 1px solid rgba(100,255,218,.2);
    border-radius: 16px;
    padding: 2px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .6rem;
    letter-spacing: .04em;
}
.bdv {
    width: 1px;
    height: 36px;
    background: rgba(255,255,255,.06);
    flex-shrink: 0;
}

/* ── Section headers ────────────────── */
.sec {
    font-family: 'IBM Plex Mono', monospace;
    color: #475569;
    font-size: .6rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,.05);
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(100,255,218,.1), transparent);
}

/* ── News cards ─────────────────────── */
.news-card {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 8px;
    padding: 12px 15px;
    margin-bottom: 8px;
    transition: border-color .2s;
}
.news-card:hover { border-color: rgba(100,255,218,.12); }
.news-title {
    font-family: 'Manrope', sans-serif;
    color: #e2e8f0;
    font-size: .84rem;
    font-weight: 600;
    margin-bottom: 4px;
    line-height: 1.45;
}
.news-meta {
    font-family: 'IBM Plex Mono', monospace;
    color: #475569;
    font-size: .68rem;
    letter-spacing: .03em;
}
.news-bull { border-left: 3px solid #64ffda; }
.news-bear { border-left: 3px solid #ff6b6b; }
.news-neut { border-left: 3px solid #475569; }

/* ── Sentiment / macro tags ─────────── */
.macro-card {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 8px;
    padding: 12px 15px;
    margin-bottom: 8px;
}
.macro-tag {
    display: inline-block;
    border-radius: 12px;
    padding: 2px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .63rem;
    font-weight: 700;
    margin-right: 6px;
    letter-spacing: .04em;
}
.tag-risk { background:rgba(255,107,107,.12);color:#ff6b6b;border:1px solid rgba(255,107,107,.28); }
.tag-oppo { background:rgba(100,255,218,.09);color:#64ffda;border:1px solid rgba(100,255,218,.22); }
.tag-warn { background:rgba(255,176,50,.1);color:#ffb032;border:1px solid rgba(255,176,50,.22); }

/* ── Adjusted forecast banner ────────── */
.adj-banner {
    background: linear-gradient(135deg, #0e0a1f, #081828);
    border: 1px solid rgba(255,255,255,.06);
    border-left: 4px solid #a78bfa;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
}

/* ── Model cards ─────────────────────── */
.mcard {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 10px;
    padding: 15px 19px;
    margin-bottom: 10px;
}
.mera {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .57rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.mtitle {
    font-family: 'Manrope', sans-serif;
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 5px;
}
.mdesc {
    font-family: 'Manrope', sans-serif;
    color: #94a3b8;
    font-size: .81rem;
    line-height: 1.65;
}
.mpill {
    display: inline-block;
    border-radius: 16px;
    padding: 3px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .7rem;
    font-weight: 700;
    margin-top: 7px;
    margin-right: 5px;
    letter-spacing: .04em;
}
.bdg {
    display: inline-block;
    background: rgba(100,255,218,.09);
    color: #64ffda;
    border: 1px solid rgba(100,255,218,.25);
    border-radius: 14px;
    padding: 2px 9px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .6rem;
    margin-left: 5px;
    letter-spacing: .04em;
}

/* ── Explanation boxes ───────────────── */
.expl {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-left: 3px solid rgba(100,255,218,.2);
    border-radius: 7px;
    padding: 10px 14px;
    margin: 6px 0 12px 0;
    font-family: 'Manrope', sans-serif;
    color: #64748b;
    font-size: .8rem;
    line-height: 1.7;
}
.expl strong { color: #64ffda; }

/* ── Tabs ────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,.06) !important;
    gap: 0 !important;
    padding: 0 !important;
    flex-wrap: wrap !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #334155 !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: .73rem !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: 10px 18px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    white-space: nowrap;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #64ffda !important;
    border-bottom: 2px solid #64ffda !important;
}

/* ── Streamlit metric overrides ──────── */
[data-testid="stMetric"] {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 10px;
    padding: 10px 13px;
}
[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .6rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .72rem !important;
}

/* ── Button ──────────────────────────── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0f3460, #1a237e) !important;
    border: 1px solid rgba(100,255,218,.3) !important;
    color: #64ffda !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .7rem !important;
    font-weight: 500 !important;
    letter-spacing: .06em !important;
    border-radius: 8px !important;
}

p, li { color: #94a3b8; font-family: 'Manrope', sans-serif; }
h1,h2,h3,h4 { color: #e2e8f0; font-family: 'Manrope', sans-serif; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060b14; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  FONT CONSTANTS (mirrors Alpha Terminal)
# ═══════════════════════════════════════════════
MONO = "IBM Plex Mono"
SANS = "Manrope"
BG, PAPER, GRID = "#060b14", "#0a1628", "#1e293b"


# ═══════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════
STOCKS = {
    "Apple (AAPL)":     "AAPL",  "NVIDIA (NVDA)":  "NVDA",
    "Amazon (AMZN)":    "AMZN",  "Google (GOOGL)": "GOOGL",
    "Microsoft (MSFT)": "MSFT",  "Tesla (TSLA)":   "TSLA",
    "Meta (META)":      "META",  "JPMorgan (JPM)":  "JPM",
}

HORIZON       = 5
SEQ_LEN       = 30
FORECAST_DAYS = 15
MAX_DR        = 0.03

MODEL_ORDER = ["arima","garch","svr","xgb","lstm","tft","fingpt"]
MODEL_META  = {
    "arima": {"tab":"📉 ARIMA","era":"1970s-1990s · Statistical",
               "name":"ARIMA (5,1,2)","accent":"#4a9eff","rmse_label":"Highest (Baseline)",
               "desc":"AutoRegressive Integrated Moving Average. Purely linear — cannot model volatility clustering or non-linear dynamics. Serves as the classical baseline."},
    "garch": {"tab":"📊 GARCH","era":"1980s-2000s · Statistical",
               "name":"GARCH (1,1)","accent":"#ffb032","rmse_label":"High",
               "desc":"Models volatility clustering using log-returns. Better than ARIMA on volatile markets but mean equation remains linear."},
    "svr":   {"tab":"🔷 SVR","era":"2000s-2010s · Machine Learning",
               "name":"Support Vector Regression","accent":"#ff6b6b","rmse_label":"Moderate",
               "desc":"Maps 12 technical features via RBF kernel. First model capturing non-linear feature interactions like momentum and volatility regime."},
    "xgb":   {"tab":"⚡ XGBoost","era":"2014-Present · ML",
               "name":"XGBoost (Gradient Boosting)","accent":"#34d399","rmse_label":"Low-Moderate",
               "desc":"300 sequentially-built trees, each correcting prior errors. L1/L2 regularisation. Gold standard for tabular financial data."},
    "lstm":  {"tab":"🧠 LSTM","era":"2017-2022 · Deep Learning",
               "name":"Bidirectional LSTM","accent":"#a78bfa","rmse_label":"Low",
               "desc":"Reads 30-day rolling-normalised return sequences. Bidirectional design captures trend continuation and reversals. First model learning from temporal order."},
    "tft":   {"tab":"🤖 TFT","era":"2021-2024 · Attention AI",
               "name":"Temporal Fusion Transformer","accent":"#38bdf8","rmse_label":"Very Low",
               "desc":"LSTM encoder combined with Multi-Head Attention. Simultaneously weighs all 30 past days to identify most predictive patterns for 5 days ahead."},
    "fingpt":{"tab":"🌐 FinGPT","era":"2024-2026 · Generative AI",
               "name":"FinGPT (Multi-Modal Agent)","accent":"#facc15","rmse_label":"Lowest",
               "desc":"4-layer transformer with 16 features, sinusoidal positional encoding, trained on 5-day cumulative returns. Represents the 2026 frontier."},
}

BASE_F = ["r1","r3","r5","r10","v5","v10","rsi","macd","bb","mr1","mr2","lag1"]
EXT_F  = BASE_F + ["lag2","lag5","r20","vrat"]


# ═══════════════════════════════════════════════
#  SENTIMENT ENGINE
# ═══════════════════════════════════════════════
BULLISH_WORDS = [
    "surge","soar","rally","jump","gain","rise","climb","beat","record","high",
    "growth","profit","revenue","upgrade","buy","outperform","strong","positive",
    "breakthrough","expand","acquisition","innovation","partnership","dividend",
    "buyback","exceed","beat expectations","raised guidance","margin expansion",
    "market share","new contract","approved","launched","all-time high",
]
BEARISH_WORDS = [
    "fall","drop","plunge","crash","decline","loss","miss","cut","downgrade",
    "sell","underperform","weak","negative","layoff","bankruptcy","fraud","recall",
    "investigation","lawsuit","fine","penalty","warning","concern","risk","debt",
    "miss expectations","lowered guidance","margin compression","competition",
    "regulatory","probe","breach","hack","shortage","supply chain","inflation",
]
GEOPOLITICAL_RISK_KEYWORDS = {
    "war":          {"weight":-0.8,"label":"Active War",         "type":"risk"},
    "conflict":     {"weight":-0.5,"label":"Armed Conflict",     "type":"risk"},
    "sanctions":    {"weight":-0.6,"label":"Economic Sanctions", "type":"risk"},
    "tariff":       {"weight":-0.4,"label":"Trade Tariffs",      "type":"risk"},
    "recession":    {"weight":-0.7,"label":"Recession Risk",     "type":"risk"},
    "inflation":    {"weight":-0.4,"label":"Inflation Pressure", "type":"risk"},
    "fed rate":     {"weight":-0.3,"label":"Fed Rate Concern",   "type":"warn"},
    "interest rate":{"weight":-0.3,"label":"Interest Rate Risk", "type":"warn"},
    "oil":          {"weight":-0.2,"label":"Oil Price Volatility","type":"warn"},
    "chip":         {"weight":0.3, "label":"Chip Demand Growth", "type":"oppo"},
    "ai boom":      {"weight":0.5, "label":"AI Boom",            "type":"oppo"},
    "deal":         {"weight":0.3, "label":"Major Deal",         "type":"oppo"},
    "ceasefire":    {"weight":0.4, "label":"Ceasefire / Peace",  "type":"oppo"},
    "stimulus":     {"weight":0.4, "label":"Economic Stimulus",  "type":"oppo"},
    "rate cut":     {"weight":0.5, "label":"Rate Cut Expected",  "type":"oppo"},
}
SECTOR_MAP = {
    "AAPL":"Technology","NVDA":"Semiconductors","AMZN":"E-Commerce/Cloud",
    "GOOGL":"Technology","MSFT":"Technology","TSLA":"EV/Energy",
    "META":"Social Media","JPM":"Banking",
}
SECTOR_RISKS = {
    "Technology":       ["chip shortage","export controls","antitrust","AI regulation"],
    "Semiconductors":   ["export ban","chip act","TSMC","supply chain","US-China"],
    "E-Commerce/Cloud": ["regulation","logistics","AWS competition","antitrust"],
    "EV/Energy":        ["battery supply","charging infrastructure","subsidies","competition"],
    "Social Media":     ["regulation","data privacy","ad revenue","political pressure"],
    "Banking":          ["interest rate","credit risk","deposit flight","regulation"],
}


def score_text_sentiment(text):
    if not text: return 0.0
    tl = text.lower()
    bull = sum(1 for w in BULLISH_WORDS if w in tl)
    bear = sum(1 for w in BEARISH_WORDS if w in tl)
    total = bull + bear
    if total == 0: return 0.0
    return float((bull - bear) / (total + 1e-9))


def classify_sentiment(score):
    if score >= 0.25:  return "BULLISH", "#64ffda", "📈"
    if score <= -0.25: return "BEARISH", "#ff6b6b", "📉"
    return "NEUTRAL", "#94a3b8", "➡️"


@st.cache_data(ttl=900, show_spinner=False)
def fetch_news_sentiment(ticker):
    try:
        tk = yf.Ticker(ticker)
        news = tk.news
        if not news: return []
        results = []
        now_ts  = datetime.now().timestamp()
        for item in news[:20]:
            title = url = summary = ""
            pub_ts = 0
            if isinstance(item, dict):
                content = item.get("content", item)
                title   = content.get("title", item.get("title",""))
                cp_url  = content.get("canonicalUrl", {})
                url     = cp_url.get("url","") if isinstance(cp_url,dict) else ""
                if not url: url = content.get("url", item.get("link",""))
                pub_time = content.get("pubDate", content.get("displayTime",""))
                if isinstance(pub_time, str) and pub_time:
                    try:
                        from dateutil import parser as dp
                        pub_ts = dp.parse(pub_time).timestamp()
                    except Exception:
                        pub_ts = item.get("providerPublishTime", 0)
                else:
                    pub_ts = item.get("providerPublishTime", 0)
                summary = content.get("summary","")
            if not title: continue
            full_text = title + " " + summary
            score     = score_text_sentiment(full_text)
            label, color, icon = classify_sentiment(score)
            age_h   = (now_ts - float(pub_ts)) / 3600 if pub_ts else 999
            age_str = "{:.0f}h ago".format(age_h) if age_h < 72 else "{:.0f}d ago".format(age_h/24)
            geo_tags = []
            for kw, meta in GEOPOLITICAL_RISK_KEYWORDS.items():
                if kw in full_text.lower():
                    geo_tags.append(meta)
            results.append({"title":title,"url":url,"score":score,"label":label,
                            "color":color,"icon":icon,"age":age_str,"age_h":age_h,
                            "geo_tags":geo_tags})
        results.sort(key=lambda x: x["age_h"])
        return results
    except Exception:
        return []


def compute_aggregate_sentiment(news_items):
    if not news_items: return 0.0, {}
    ws = tw = 0.0
    bc = bear = nc = 0
    for item in news_items:
        w   = float(np.exp(-item.get("age_h",24) / 48.0))
        ws += item["score"] * w; tw += w
        if item["label"]=="BULLISH": bc += 1
        elif item["label"]=="BEARISH": bear += 1
        else: nc += 1
    agg = float(np.clip(ws/(tw+1e-9), -1.0, 1.0))
    return agg, {"bullish":bc,"bearish":bear,"neutral":nc,"total":len(news_items)}


def compute_geo_risk_score(news_items, ticker):
    sector       = SECTOR_MAP.get(ticker, "Technology")
    sector_risks = SECTOR_RISKS.get(sector, [])
    risk_factors = []; total = 0.0; seen = set()
    for item in news_items:
        for tag in item.get("geo_tags",[]):
            lbl = tag["label"]
            if lbl not in seen:
                seen.add(lbl)
                risk_factors.append({"label":lbl,"type":tag["type"],
                                     "weight":tag["weight"],"source":"News"})
                total += tag["weight"]
    for rw in sector_risks[:3]:
        lbl = rw.replace("-"," ").title()+" Risk"
        if lbl not in seen:
            risk_factors.append({"label":lbl,"type":"warn","weight":-0.2,"source":"Sector"})
            total += -0.2
    risk_score = float(np.clip(total / max(len(risk_factors),1), -1.0, 1.0))
    return risk_score, risk_factors


def compute_sentiment_adjustment(news_score, geo_score, base_forecast):
    combined  = 0.6*news_score + 0.4*geo_score
    max_adj   = 0.05
    adj_total = float(np.clip(combined*max_adj, -max_adj, max_adj))
    ramp      = np.linspace(0, adj_total, len(base_forecast))
    adjusted  = base_forecast * (1.0 + ramp)
    if adj_total > 0.01:
        etxt = ("News sentiment is POSITIVE (+{:.1f}%). Forecast adjusted UP slightly "
                "due to bullish news flow and favourable macro conditions.".format(adj_total*100))
    elif adj_total < -0.01:
        etxt = ("News sentiment is NEGATIVE ({:.1f}%). Forecast adjusted DOWN slightly "
                "due to bearish news flow and geopolitical risk factors.".format(adj_total*100))
    else:
        etxt = ("News sentiment is NEUTRAL. No significant adjustment applied. "
                "Algorithmic prediction stands without news-based modification.")
    return adjusted, adj_total*100, etxt


# ═══════════════════════════════════════════════
#  SENTIMENT CHART HELPERS
# ═══════════════════════════════════════════════
def sentiment_gauge_chart(score, title="News Sentiment"):
    color = "#64ffda" if score > 0.1 else ("#ff6b6b" if score < -0.1 else "#94a3b8")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(score*100, 1),
        title={"text": title, "font": {"color":"#475569","size":11,"family":MONO}},
        number={"font":{"color":color,"size":26,"family":MONO},"suffix":"%"},
        delta={"reference":0,"font":{"size":11}},
        gauge={
            "axis":{"range":[-100,100],"tickcolor":"#334155",
                    "tickfont":{"color":"#475569","size":9},"tickwidth":1},
            "bar":{"color":color,"thickness":0.28},
            "bgcolor":PAPER,"borderwidth":0,
            "steps":[
                {"range":[-100,-25],"color":"rgba(255,107,107,.1)"},
                {"range":[-25,25],  "color":"rgba(255,255,255,.03)"},
                {"range":[25,100],  "color":"rgba(100,255,218,.08)"},
            ],
            "threshold":{"line":{"color":"#e2e8f0","width":2},"thickness":0.75,
                         "value":round(score*100,1)},
        },
    ))
    fig.update_layout(
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8", family=SANS),
        height=200, margin=dict(l=30,r=30,t=40,b=10),
    )
    return fig


def news_sentiment_timeline(news_items):
    if not news_items: return None
    items  = news_items[:12]
    labels = ["A{}".format(i+1) for i in range(len(items))]
    scores = [item["score"] for item in items]
    colors = [item["color"] for item in items]
    titles = [item["title"][:45]+"..." if len(item["title"])>45
              else item["title"] for item in items]
    fig = go.Figure(go.Bar(
        x=labels, y=scores,
        marker_color=colors,
        marker_line_color=BG, marker_line_width=1,
        hovertext=titles, hoverinfo="text+y",
        name="Sentiment Score",
    ))
    fig.add_hline(y=0,    line_color="rgba(255,255,255,.15)", line_width=1)
    fig.add_hline(y=0.25, line_color="rgba(100,255,218,.3)",  line_width=1, line_dash="dot")
    fig.add_hline(y=-0.25,line_color="rgba(255,107,107,.3)",  line_width=1, line_dash="dot")
    fig.update_layout(
        title=dict(text="Article-by-Article Sentiment (hover for headline)",
                   font=dict(color="#e2e8f0",size=11,family=SANS),x=0.01),
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8",family=SANS,size=10),
        xaxis=dict(showgrid=False,zeroline=False,color="#475569",
                   tickfont=dict(size=8,family=MONO)),
        yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,
                   color="#475569",range=[-1.1,1.1],
                   title="Sentiment",tickfont=dict(family=MONO,size=9)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        height=240, margin=dict(l=50,r=20,t=40,b=35),
    )
    return fig


def adjusted_vs_base_chart(base_fp, adj_fp, last_price, last_date_str):
    fd   = future_dates_fn(last_date_str, FORECAST_DAYS)
    diff = adj_fp - base_fp
    clr  = "#64ffda" if float(np.mean(diff)) >= 0 else "#ff6b6b"
    fig  = go.Figure()
    fig.add_trace(go.Scatter(x=fd, y=base_fp, mode="lines",
                             name="Algorithmic Forecast",
                             line=dict(color="#a78bfa",width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=fd, y=adj_fp, mode="lines+markers",
                             name="Sentiment-Adjusted",
                             line=dict(color=clr,width=2.5),
                             marker=dict(size=4,color=clr)))
    fig.add_trace(go.Scatter(
        x=list(fd)+list(fd)[::-1],
        y=list(adj_fp)+list(base_fp)[::-1],
        fill="toself",
        fillcolor="rgba(167,139,250,.06)" if float(np.mean(diff))>=0
                  else "rgba(255,107,107,.06)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Adjustment Band"))
    fig.update_layout(
        title=dict(text="Algorithmic vs Sentiment-Adjusted Forecast",
                   font=dict(color="#e2e8f0",size=12,family=SANS),x=0.01),
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8",family=SANS,size=10),
        xaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color="#475569"),
        yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color="#475569",
                   title="Price ($)",tickfont=dict(family=MONO,size=9)),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#94a3b8",size=10,family=SANS)),
        hovermode="x unified",
        height=320, margin=dict(l=55,r=20,t=42,b=35),
    )
    return fig


def future_dates_fn(last_date_str, n):
    try:    last = datetime.strptime(str(last_date_str), "%Y-%m-%d").date()
    except: last = date.today()
    out, cur = [], last
    while len(out) < n:
        cur += timedelta(days=1)
        if cur.weekday() < 5: out.append(cur)
    return pd.DatetimeIndex([pd.Timestamp(d) for d in out])


# ═══════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner=False)
def load_data(ticker, start, end):
    end_fetch = str(date.fromisoformat(str(end)) + timedelta(days=1))
    df = yf.download(ticker, start=start, end=end_fetch,
                     progress=False, auto_adjust=True, actions=False)
    if df.empty: return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    cols = [c for c in ["Open","High","Low","Close","Volume"] if c in df.columns]
    df = df[cols].copy()
    if hasattr(df.index,"tz") and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    if isinstance(df["Close"], pd.DataFrame):
        df["Close"] = df["Close"].iloc[:,0]
    return df.dropna()


def get_close_array(df):
    c = df["Close"]
    if isinstance(c, pd.DataFrame): c = c.iloc[:,0]
    return np.array(c, dtype=np.float64).ravel()

def get_last_price(df):
    return float(get_close_array(df)[-1])

def get_aligned_close(df, data):
    cs = df["Close"]
    if isinstance(cs, pd.DataFrame): cs = cs.iloc[:,0]
    return np.array(cs.reindex(data.index), dtype=np.float64).ravel()


# ═══════════════════════════════════════════════
#  FEATURE ENGINEERING
# ═══════════════════════════════════════════════
def make_features(df):
    close = get_close_array(df)
    vol   = np.array(df["Volume"], dtype=np.float64).ravel()
    idx   = df.index; N = len(close)

    def spct(arr,n):
        out=np.full(N,np.nan)
        for i in range(n,N):
            if arr[i-n]!=0: out[i]=(arr[i]-arr[i-n])/arr[i-n]
        return out
    def rmean(arr,w):
        out=np.full(N,np.nan)
        for i in range(w-1,N): out[i]=float(np.mean(arr[i-w+1:i+1]))
        return out
    def rstd(arr,w):
        out=np.full(N,np.nan)
        for i in range(w-1,N): out[i]=float(np.std(arr[i-w+1:i+1]))
        return out

    r1=spct(close,1); r3=spct(close,3); r5=spct(close,5)
    r10=spct(close,10); r20=spct(close,20)
    v5=rstd(r1,5); v10=rstd(r1,10)
    delta=np.diff(close,prepend=close[0])
    gain=np.where(delta>0,delta,0.0); loss=np.where(delta<0,-delta,0.0)
    ag=rmean(gain,14); al=rmean(loss,14)
    rsi=np.full(N,0.5)
    for i in range(N):
        if not np.isnan(ag[i]) and al[i]!=0:
            rsi[i]=(100-100/(1+ag[i]/(al[i]+1e-9)))/100
    ema12=pd.Series(close).ewm(span=12,adjust=False).mean().values
    ema26=pd.Series(close).ewm(span=26,adjust=False).mean().values
    macd=(ema12-ema26)/(close+1e-9)
    ma20=rmean(close,20); std20=rstd(close,20)
    bb=np.full(N,0.5)
    for i in range(N):
        if not np.isnan(std20[i]) and std20[i]>0:
            bb[i]=(close[i]-(ma20[i]-2*std20[i]))/(4*std20[i])
    mr1=rmean(close,5)/(rmean(close,20)+1e-9)-1
    mr2=rmean(close,10)/(rmean(close,50)+1e-9)-1
    vm20=rmean(vol,20); vrat=vol/(vm20+1e-9)
    lag1=np.roll(r1,1); lag1[0]=0.0
    lag2=np.roll(r1,2); lag2[:2]=0.0
    lag5=np.roll(r1,5); lag5[:5]=0.0
    d=pd.DataFrame({"r1":r1,"r3":r3,"r5":r5,"r10":r10,
                    "v5":v5,"v10":v10,"rsi":rsi,"macd":macd,"bb":bb,
                    "mr1":mr1,"mr2":mr2,"lag1":lag1,
                    "lag2":lag2,"lag5":lag5,"r20":r20,"vrat":vrat},index=idx)
    return d.dropna()


# ═══════════════════════════════════════════════
#  ARRAY BUILDERS
# ═══════════════════════════════════════════════
def build_tabular(feat_vals, close_al, horizon):
    r1=feat_vals[:,0]; N=len(feat_vals); X,y,base,actual=[],[],[],[]
    for i in range(N-horizon):
        X.append(feat_vals[i].copy())
        y.append(float(np.sum(r1[i+1:i+1+horizon])))
        base.append(float(close_al[i])); actual.append(float(close_al[i+horizon]))
    return (np.array(X,dtype=np.float32),np.array(y,dtype=np.float32),
            np.array(base,dtype=np.float32),np.array(actual,dtype=np.float32))


def build_sequences(feat_vals, close_al, sl, horizon):
    r1=feat_vals[:,0]; N=len(feat_vals); X,y,base,actual=[],[],[],[]
    for i in range(N-sl-horizon):
        w=feat_vals[i:i+sl]; mu=w.mean(axis=0); sig=w.std(axis=0)+1e-9
        X.append((w-mu)/sig)
        y.append(float(np.sum(r1[i+sl:i+sl+horizon])))
        base.append(float(close_al[i+sl])); actual.append(float(close_al[i+sl+horizon]))
    return (np.array(X,dtype=np.float32),np.array(y,dtype=np.float32),
            np.array(base,dtype=np.float32),np.array(actual,dtype=np.float32))


# ═══════════════════════════════════════════════
#  FORECAST HELPERS
# ═══════════════════════════════════════════════
def tabular_forecast(pred_fn, last_feat, last_price, n_days):
    cur=float(last_price); feat=last_feat.copy().astype(np.float32); fp=[]
    for _ in range(n_days):
        dr=float(np.clip(float(pred_fn(feat.reshape(1,-1)))/HORIZON,-MAX_DR,MAX_DR))
        cur=cur*(1.0+dr); fp.append(cur)
        feat[0]=dr; feat[1]=dr*1.5
        if len(feat)>11: feat[11]=dr
    return np.array(fp)


def dl_forecast(model_fn, feat_window, last_price, nf, sl, n_days):
    buf=list(feat_window.copy().astype(np.float32)); cur=float(last_price); fp=[]
    for _ in range(n_days):
        w=np.array(buf[-sl:],dtype=np.float32)
        mu=w.mean(axis=0); sig=w.std(axis=0)+1e-9
        x_in=((w-mu)/sig).reshape(1,sl,nf)
        dr=float(np.clip(float(model_fn(x_in))/HORIZON,-MAX_DR,MAX_DR))
        cur=cur*(1.0+dr); fp.append(cur)
        nr=buf[-1].copy(); nr[0]=dr; nr[1]=dr
        if nf>11: nr[11]=dr
        buf.append(nr)
    return np.array(fp)


def future_dates(last, n):
    out, cur = [], last
    while len(out)<n:
        cur+=timedelta(days=1)
        if cur.weekday()<5: out.append(cur)
    return pd.DatetimeIndex(out)


# ═══════════════════════════════════════════════
#  CHART HELPERS
# ═══════════════════════════════════════════════
def apply_layout(fig, title, h=420, extra=None):
    lay = dict(
        title=dict(text=title,font=dict(color="#e2e8f0",size=12,family=SANS),x=0.01),
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8",family=SANS,size=10),
        xaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color="#475569"),
        yaxis=dict(showgrid=True,gridcolor=GRID,zeroline=False,color="#475569",
                   tickfont=dict(family=MONO,size=9)),
        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#94a3b8",size=9,family=SANS)),
        hovermode="x unified", margin=dict(l=50,r=20,t=40,b=35),
    )
    if extra:
        for k,v in extra.items():
            if k in ("xaxis","yaxis") and isinstance(v,dict): lay[k]={**lay[k],**v}
            else: lay[k]=v
    lay["height"]=h
    fig.update_layout(**lay)


def pred_chart(df, res, accent, adj_fp=None, h=400):
    close=get_close_array(df); dates=df.index
    ts=min(res["train_size"],len(close)-1)
    fd=future_dates(dates[-1],FORECAST_DAYS)
    n=min(len(dates[ts:]),len(res["test_actual"]),len(res["test_pred"]))
    td=dates[ts:][:n]; ta=res["test_actual"][:n]; tp=res["test_pred"][:n]
    fp=res["future_pred"]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=dates[:ts],y=close[:ts],mode="lines",
                             name="Train",line=dict(color="#1e293b",width=1.5)))
    fig.add_trace(go.Scatter(x=td,y=ta,mode="lines",name="Actual",
                             line=dict(color="#e2e8f0",width=2)))
    fig.add_trace(go.Scatter(x=td,y=tp,mode="lines",name="Predicted",
                             line=dict(color=accent,width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=fd,y=fp,mode="lines+markers",
                             name="{}-Day Algo".format(FORECAST_DAYS),
                             line=dict(color="#64ffda",width=2),
                             marker=dict(size=4,color="#64ffda")))
    if adj_fp is not None:
        fig.add_trace(go.Scatter(x=fd,y=adj_fp,mode="lines+markers",
                                 name="Sentiment-Adj",
                                 line=dict(color="#a78bfa",width=2,dash="dash"),
                                 marker=dict(size=4,color="#a78bfa")))
    sigma=float(np.std(ta-tp)) if n>1 else float(np.mean(np.abs(ta))*0.01)
    ramp=np.sqrt(np.arange(1,FORECAST_DAYS+1))
    fig.add_trace(go.Scatter(
        x=list(fd)+list(fd)[::-1],
        y=list(fp+sigma*ramp*0.5)+list(fp-sigma*ramp*0.5)[::-1],
        fill="toself",fillcolor="rgba(100,255,218,.04)",
        line=dict(color="rgba(0,0,0,0)"),name="Uncertainty"))
    div_ms=int(pd.Timestamp(dates[-1]).timestamp()*1000)
    fig.add_vline(x=div_ms,line_dash="dash",
                  line_color="rgba(255,255,255,.1)",line_width=1,
                  annotation_text="  Forecast",
                  annotation_font=dict(color="#475569",size=9,family=MONO))
    apply_layout(fig, res["name"], h=h)
    return fig


def make_forecast_table(last_price, future_pred, adj_pred=None):
    fd=future_dates_fn(str(date.today()), FORECAST_DAYS)
    preds=future_pred[:FORECAST_DAYS]
    adj=adj_pred[:FORECAST_DAYS] if adj_pred is not None else None
    rows, prev = [], float(last_price)
    for i,(d,p) in enumerate(zip(fd,preds)):
        ca=p-prev; cp=ca/(prev+1e-9)*100
        row={"Day":i+1,"Date":d.strftime("%a %b %d"),
             "Algo ($)":round(float(p),2),
             "Change ($)":round(float(ca),2),"Change (%)":round(float(cp),2),
             "Signal":"BUY / HOLD" if ca>=0 else "WATCH / SELL"}
        if adj is not None:
            ap=float(adj[i])
            row["Sentiment Adj ($)"]=round(ap,2)
            row["Adj Diff"]=round(ap-float(p),2)
        rows.append(row); prev=p
    return pd.DataFrame(rows)


def style_ft(ft):
    cols=["Change ($)","Change (%)","Signal"]
    if "Adj Diff" in ft.columns: cols.append("Adj Diff")
    def c(v):
        if isinstance(v,(int,float)): return "color:#64ffda" if v>=0 else "color:#ff6b6b"
        if isinstance(v,str):
            if "BUY" in v: return "color:#64ffda"
            if "WATCH" in v: return "color:#ff6b6b"
        return ""
    fmt={"Algo ($)":"${:.2f}","Change ($)":"{:+.2f}","Change (%)":"{:+.2f}%"}
    if "Sentiment Adj ($)" in ft.columns: fmt["Sentiment Adj ($)"]="${:.2f}"
    if "Adj Diff" in ft.columns:         fmt["Adj Diff"]="{:+.2f}"
    return (ft.style.map(c,subset=cols).format(fmt)
            .set_properties(**{"background-color":"#0a1628","color":"#94a3b8",
                               "border":"1px solid #1e293b",
                               "font-family":"'IBM Plex Mono',monospace",
                               "font-size":"0.72rem"})
            .set_table_styles([{"selector":"th","props":[
                ("background","#060b14"),("color","#64ffda"),
                ("font-family","IBM Plex Mono,monospace"),("font-size","0.62rem"),
                ("text-transform","uppercase"),("letter-spacing",".06em"),
                ("border","1px solid #1e293b")]}]))


def expl(txt):
    st.markdown("<div class='expl'>{}</div>".format(txt), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  MODELS (all 7)
# ═══════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def run_arima(ticker, start, end):
    df=load_data(ticker,start,end); close=get_close_array(df)
    last_price=float(close[-1]); ts=int(len(close)*0.8)
    train,test=close[:ts],close[ts:]
    history,preds=list(train),[]
    step=max(1,(len(test)-HORIZON)//10); fit=None
    for i in range(len(test)-HORIZON):
        if fit is None or i%step==0:
            try: fit=ARIMA(history,order=(5,1,2)).fit()
            except:
                try: fit=ARIMA(history,order=(2,1,1)).fit()
                except: fit=ARIMA(history,order=(1,1,1)).fit()
        fc=fit.forecast(steps=HORIZON)
        fc_arr=fc.values if hasattr(fc,"values") else np.array(fc)
        preds.append(float(fc_arr[-1])); history.append(float(test[i]))
    pa=np.array(preds); aa=test[HORIZON:HORIZON+len(preds)]
    n=min(len(pa),len(aa)); pa=pa[:n]; aa=aa[:n]
    rmse=float(np.sqrt(mean_squared_error(aa,pa)))
    try: final=ARIMA(close,order=(5,1,2)).fit()
    except: final=ARIMA(close,order=(1,1,1)).fit()
    raw=final.forecast(steps=FORECAST_DAYS+HORIZON)
    raw_arr=raw.values if hasattr(raw,"values") else np.array(raw)
    cur=last_price; fp=[]
    for i in range(FORECAST_DAYS):
        dr=float(np.clip((float(raw_arr[i])-close[-1])/(close[-1]*(i+1)+1e-9),-MAX_DR,MAX_DR))
        cur=cur*(1.0+dr); fp.append(cur)
    return dict(name=MODEL_META["arima"]["name"],rmse=rmse,
                test_actual=aa,test_pred=pa,future_pred=np.array(fp),
                train_size=ts,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_garch(ticker, start, end):
    df=load_data(ticker,start,end); close=get_close_array(df)
    last_price=float(close[-1]); rets=np.diff(np.log(close+1e-9)); ts_r=int(len(rets)*0.8)
    mu=float(np.mean(rets[:ts_r]))
    phi=float(np.clip(np.corrcoef(rets[:ts_r-1],rets[1:ts_r])[0,1],-0.2,0.2))
    omega=float(np.var(rets[:ts_r])*0.05); alpha,beta=0.10,0.85
    sq_r=(rets[:ts_r]-mu)**2; sig2=np.full(len(rets[:ts_r]),np.var(rets[:ts_r]))
    for t in range(1,len(sig2)): sig2[t]=omega+alpha*sq_r[t-1]+beta*sig2[t-1]
    history=list(rets[:ts_r]); h_var=[float(sig2[-1])]; preds=[]
    for i in range(len(rets)-ts_r-HORIZON):
        cr,cs2=history[-1],h_var[-1]
        for _ in range(HORIZON):
            rm=mu+phi*(cr-mu); cs2=omega+alpha*(cr-mu)**2+beta*cs2; cr=rm
        preds.append(cr); history.append(rets[ts_r+i])
        h_var.append(float(omega+alpha*(rets[ts_r+i]-mu)**2+beta*h_var[-1]))
    n_p=len(preds); bc=close[ts_r:ts_r+n_p]
    pp=bc*np.exp(np.array(preds)*HORIZON); ap=close[ts_r+HORIZON:ts_r+HORIZON+n_p]
    n=min(len(pp),len(ap)); pp=pp[:n]; ap=ap[:n]
    rmse=float(np.sqrt(mean_squared_error(ap,pp)))
    cur,cr,cs2=last_price,float(rets[-1]),float(sig2[-1]); fp=[]
    for _ in range(FORECAST_DAYS):
        rm=mu+phi*(cr-mu); cs2=omega+alpha*(cr-mu)**2+beta*cs2
        dr=float(np.clip(rm,-MAX_DR,MAX_DR)); cur=cur*np.exp(dr); fp.append(cur); cr=rm
    return dict(name=MODEL_META["garch"]["name"],rmse=rmse,
                test_actual=ap,test_pred=pp,future_pred=np.array(fp),
                train_size=ts_r+1,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_svr(ticker, start, end):
    df=load_data(ticker,start,end); data=make_features(df)
    close_al=get_aligned_close(df,data); last_price=float(close_al[-1])
    fv=data[BASE_F].values.astype(np.float32)
    X,yc,bp,ap=build_tabular(fv,close_al,HORIZON)
    offset=len(df)-len(data); ts=int(len(X)*0.8); tr_max=min(ts,800)
    sc=StandardScaler(); sc.fit(X[ts-tr_max:ts])
    Xtr_s=sc.transform(X[ts-tr_max:ts]); Xte_s=sc.transform(X[ts:])
    m=SVR(kernel="rbf",C=8.0,epsilon=0.003,gamma="scale",cache_size=512)
    m.fit(Xtr_s,yc[ts-tr_max:ts]); pred_cum=m.predict(Xte_s)
    pp=bp[ts:ts+len(pred_cum)]*(1.0+pred_cum); acp=ap[ts:ts+len(pred_cum)]
    n=min(len(pp),len(acp)); pp=pp[:n]; acp=acp[:n]
    rmse=float(np.sqrt(mean_squared_error(acp,pp)))
    fp=tabular_forecast(lambda x:m.predict(sc.transform(x))[0],fv[-1],last_price,FORECAST_DAYS)
    return dict(name=MODEL_META["svr"]["name"],rmse=rmse,
                test_actual=acp,test_pred=pp,future_pred=fp,
                train_size=ts+offset,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_xgb(ticker, start, end):
    df=load_data(ticker,start,end); data=make_features(df)
    close_al=get_aligned_close(df,data); last_price=float(close_al[-1])
    fv=data[BASE_F].values.astype(np.float32)
    X,yc,bp,ap=build_tabular(fv,close_al,HORIZON)
    offset=len(df)-len(data); ts=int(len(X)*0.8)
    m=xgb.XGBRegressor(n_estimators=300,max_depth=5,learning_rate=0.03,
                        subsample=0.8,colsample_bytree=0.8,reg_lambda=2.0,
                        random_state=42,verbosity=0)
    m.fit(X[:ts],yc[:ts],eval_set=[(X[ts:],yc[ts:])],verbose=False)
    pred_cum=m.predict(X[ts:])
    pp=bp[ts:ts+len(pred_cum)]*(1.0+pred_cum); acp=ap[ts:ts+len(pred_cum)]
    n=min(len(pp),len(acp)); pp=pp[:n]; acp=acp[:n]
    rmse=float(np.sqrt(mean_squared_error(acp,pp)))
    fp=tabular_forecast(lambda x:float(m.predict(x)[0]),fv[-1],last_price,FORECAST_DAYS)
    return dict(name=MODEL_META["xgb"]["name"],rmse=rmse,
                test_actual=acp,test_pred=pp,future_pred=fp,
                train_size=ts+offset,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_lstm(ticker, start, end):
    if not TF_AVAILABLE: return None
    df=load_data(ticker,start,end); data=make_features(df)
    close_al=get_aligned_close(df,data); last_price=float(close_al[-1])
    fv=data[BASE_F].values.astype(np.float32); offset=len(df)-len(data); nf=len(BASE_F)
    Xs,ys,bp,ap=build_sequences(fv,close_al,SEQ_LEN,HORIZON); ts=int(len(Xs)*0.8)
    inp=Input(shape=(SEQ_LEN,nf)); h=Bidirectional(LSTM(48,return_sequences=False))(inp)
    h=Dropout(0.2)(h); h=Dense(48,activation="relu")(h); h=Dropout(0.15)(h); out=Dense(1)(h)
    model=Model(inp,out); model.compile(optimizer=Adam(learning_rate=0.001,clipnorm=1.0),loss="huber")
    model.fit(Xs[:ts],ys[:ts],epochs=30,batch_size=64,validation_split=0.1,
              callbacks=[EarlyStopping(patience=5,restore_best_weights=True,monitor="val_loss")],verbose=0)
    pc=model.predict(Xs[ts:],verbose=0).ravel()
    pp=bp[ts:ts+len(pc)]*(1.0+pc); acp=ap[ts:ts+len(pc)]
    n=min(len(pp),len(acp)); pp=pp[:n]; acp=acp[:n]
    rmse=float(np.sqrt(mean_squared_error(acp,pp)))
    fp=dl_forecast(lambda x:float(model.predict(x,verbose=0)[0,0]),fv[-SEQ_LEN:],last_price,nf,SEQ_LEN,FORECAST_DAYS)
    return dict(name=MODEL_META["lstm"]["name"],rmse=rmse,
                test_actual=acp,test_pred=pp,future_pred=fp,
                train_size=offset+ts+SEQ_LEN,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_tft(ticker, start, end):
    if not TF_AVAILABLE: return None
    df=load_data(ticker,start,end); data=make_features(df)
    close_al=get_aligned_close(df,data); last_price=float(close_al[-1])
    fv=data[BASE_F].values.astype(np.float32); offset=len(df)-len(data); nf=len(BASE_F)
    Xs,ys,bp,ap=build_sequences(fv,close_al,SEQ_LEN,HORIZON); ts=int(len(Xs)*0.8)
    inp=Input(shape=(SEQ_LEN,nf)); h=LSTM(48,return_sequences=True)(inp)
    h=Dropout(0.15)(h); attn=MultiHeadAttention(num_heads=4,key_dim=12,dropout=0.1)(h,h)
    h=LayerNormalization(epsilon=1e-6)(h+attn); x=h[:,-1,:]
    x=Dense(48,activation="gelu")(x); x=Dropout(0.15)(x); out=Dense(1)(x)
    model=Model(inp,out); model.compile(optimizer=Adam(learning_rate=0.0008,clipnorm=1.0),loss="huber")
    model.fit(Xs[:ts],ys[:ts],epochs=30,batch_size=64,validation_split=0.1,
              callbacks=[EarlyStopping(patience=5,restore_best_weights=True,monitor="val_loss")],verbose=0)
    pc=model.predict(Xs[ts:],verbose=0).ravel()
    pp=bp[ts:ts+len(pc)]*(1.0+pc); acp=ap[ts:ts+len(pc)]
    n=min(len(pp),len(acp)); pp=pp[:n]; acp=acp[:n]
    rmse=float(np.sqrt(mean_squared_error(acp,pp)))
    fp=dl_forecast(lambda x:float(model.predict(x,verbose=0)[0,0]),fv[-SEQ_LEN:],last_price,nf,SEQ_LEN,FORECAST_DAYS)
    return dict(name=MODEL_META["tft"]["name"],rmse=rmse,
                test_actual=acp,test_pred=pp,future_pred=fp,
                train_size=offset+ts+SEQ_LEN,last_price=last_price)


@st.cache_data(show_spinner=False)
def run_fingpt(ticker, start, end):
    if not TF_AVAILABLE: return None
    df=load_data(ticker,start,end); data=make_features(df)
    close_al=get_aligned_close(df,data); last_price=float(close_al[-1])
    fv=data[EXT_F].values.astype(np.float32); offset=len(df)-len(data); nf=len(EXT_F); D=64
    Xs,ys,bp,ap=build_sequences(fv,close_al,SEQ_LEN,HORIZON); ts=int(len(Xs)*0.8)
    def compute_pe(sl,dm):
        pos=np.arange(sl)[:,np.newaxis].astype(np.float32)
        dims=np.arange(dm)[np.newaxis,:].astype(np.float32)
        ang=pos/np.power(10000.0,(2.0*(dims//2))/dm)
        ang[:,0::2]=np.sin(ang[:,0::2]); ang[:,1::2]=np.cos(ang[:,1::2])
        return ang[np.newaxis,:,:].astype(np.float32)
    pe_const=compute_pe(SEQ_LEN,D)
    inp=Input(shape=(SEQ_LEN,nf),name="input")
    x=Dense(D,name="proj")(inp)
    x=Lambda(lambda z:z+tf.constant(pe_const),name="pos_enc")(x)
    x=Dropout(0.15,name="inp_drop")(x)
    for bi in range(4):
        bn="b{}".format(bi)
        a=MultiHeadAttention(num_heads=8,key_dim=8,dropout=0.1,name=bn+"_attn")(x,x)
        a=Dropout(0.1,name=bn+"_drop")(a)
        x=LayerNormalization(epsilon=1e-6,name=bn+"_ln1")(x+a)
        f=Dense(D*2,activation="gelu",name=bn+"_ff1")(x)
        f=Dropout(0.1,name=bn+"_ffd")(f)
        f=Dense(D,name=bn+"_ff2")(f)
        x=LayerNormalization(epsilon=1e-6,name=bn+"_ln2")(x+f)
    ls=Lambda(lambda z:z[:,-1,:],name="last")(x)
    av=GlobalAveragePooling1D(name="avg")(x)
    x=Concatenate(name="cat")([ls,av])
    x=Dense(64,activation="gelu",name="h1")(x); x=Dropout(0.15,name="h_drop")(x); out=Dense(1,name="out")(x)
    model=Model(inputs=inp,outputs=out,name="FinGPT")
    model.compile(optimizer=Adam(learning_rate=0.0004,clipnorm=1.0),loss="huber")
    model.fit(Xs[:ts],ys[:ts],epochs=35,batch_size=32,validation_split=0.1,
              callbacks=[EarlyStopping(patience=6,restore_best_weights=True,monitor="val_loss")],verbose=0)
    pc=model.predict(Xs[ts:],verbose=0).ravel()
    pp=bp[ts:ts+len(pc)]*(1.0+pc); acp=ap[ts:ts+len(pc)]
    n=min(len(pp),len(acp)); pp=pp[:n]; acp=acp[:n]
    rmse=float(np.sqrt(mean_squared_error(acp,pp)))
    fp=dl_forecast(lambda x:float(model.predict(x,verbose=0)[0,0]),fv[-SEQ_LEN:],last_price,nf,SEQ_LEN,FORECAST_DAYS)
    return dict(name=MODEL_META["fingpt"]["name"],rmse=rmse,
                test_actual=acp,test_pred=pp,future_pred=fp,
                train_size=offset+ts+SEQ_LEN,last_price=last_price)


RUNNER_MAP={"arima":run_arima,"garch":run_garch,"svr":run_svr,"xgb":run_xgb,
            "lstm":run_lstm,"tft":run_tft,"fingpt":run_fingpt}


# ═══════════════════════════════════════════════
#  RMSE CHART
# ═══════════════════════════════════════════════
def rmse_chart(valid):
    keys=[k for k in MODEL_ORDER if k in valid and valid[k] is not None]
    names=[MODEL_META[k]["name"].split("(")[0].strip() for k in keys]
    rmses=[valid[k]["rmse"] for k in keys]; best_v=min(rmses)
    colors=[MODEL_META[k]["accent"] if valid[k]["rmse"]==best_v else "#1e293b" for k in keys]
    fig=go.Figure()
    fig.add_trace(go.Bar(x=names,y=rmses,name="RMSE",marker_color=colors,
                         marker_line_color=BG,marker_line_width=1,
                         text=["{:.2f}".format(v) for v in rmses],textposition="outside",
                         textfont=dict(color="#475569",size=9,family=MONO)))
    fig.add_trace(go.Scatter(x=names,y=rmses,mode="lines+markers",name="Trend",
                             line=dict(color="#64ffda",width=2,dash="dot"),
                             marker=dict(size=6,color="#64ffda")))
    bi=rmses.index(best_v)
    fig.add_annotation(x=names[bi],y=best_v,text="Best: {:.2f}".format(best_v),
                       showarrow=True,arrowhead=2,arrowcolor="#64ffda",
                       font=dict(color="#64ffda",size=9,family=MONO),
                       bgcolor="rgba(100,255,218,.07)",bordercolor="rgba(100,255,218,.3)",
                       borderwidth=1,borderpad=3,ay=-40)
    apply_layout(fig,"RMSE Progression — 1970s to 2026  |  Lower = Better",h=310,
                 extra={"bargap":0.25,"showlegend":True,
                        "yaxis":{"title":"RMSE (USD)"},
                        "xaxis":{"tickfont":{"size":8,"family":MONO},"tickangle":-15}})
    return fig


# ═══════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 4px 12px 4px;text-align:center;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:1.1rem;
                  font-weight:700;color:#64ffda;letter-spacing:.04em;">
        📈 Prediction Lab
      </div>
      <div style="font-family:'Manrope',sans-serif;font-size:.62rem;font-weight:600;
                  color:#1e293b;letter-spacing:.18em;text-transform:uppercase;margin-top:3px;">
        2026 Edition
      </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:0 0 16px 0;">
    """, unsafe_allow_html=True)

    sel    = st.selectbox("SELECT STOCK", list(STOCKS.keys()), index=0)
    ticker = STOCKS[sel]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;font-weight:500;
                color:#334155;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;">
      Analysis Period
    </div>""", unsafe_allow_html=True)
    start_d = st.date_input("Start Date", value=date.today()-timedelta(days=1825),
                             max_value=date.today()-timedelta(days=120))
    end_d   = st.date_input("End Date",   value=date.today(),
                             min_value=start_d+timedelta(days=120), max_value=date.today())

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶  Run Full Analysis", use_container_width=True, type="primary")

    st.markdown("""
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:18px 0 14px 0;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.57rem;color:#334155;
                letter-spacing:.08em;margin-bottom:10px;text-transform:uppercase;">
      7 Prediction Models
    </div>""", unsafe_allow_html=True)
    for k in MODEL_ORDER:
        m = MODEL_META[k]
        st.markdown("""
        <div style="padding:5px 0;border-bottom:1px solid rgba(255,255,255,.03);">
          <div style="font-family:'Manrope',sans-serif;font-size:.76rem;font-weight:600;
                      color:#94a3b8;">{name}</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:.6rem;
                      color:#334155;margin-top:1px;">{rl}</div>
        </div>""".format(name=m["name"].split("(")[0].strip(), rl=m["rmse_label"]),
        unsafe_allow_html=True)

    st.markdown("""
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:14px 0;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.57rem;color:#334155;
                letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;">
      Sentiment Analysis
    </div>""", unsafe_allow_html=True)
    for label in ["Live news from Yahoo Finance","Geopolitical risk keywords",
                  "Sector-specific macro risks","Sentiment-adjusted forecasts"]:
        st.markdown("""
        <div style="font-family:'Manrope',sans-serif;font-size:.75rem;
                    color:#475569;padding:2px 0;">· {}</div>""".format(label),
        unsafe_allow_html=True)

    if not TF_AVAILABLE:
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("TF models need: pip install tensorflow-cpu")


# ═══════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════
for k in ("results","df_cache","verified_last_price","verified_last_date",
          "news_items","sent_score","geo_score","risk_factors","sent_breakdown"):
    if k not in st.session_state:
        st.session_state[k]={} if k=="results" else None


# ═══════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════
now_str = datetime.now().strftime("%d %b %Y  %H:%M")
st.markdown("""
<div style="background:linear-gradient(135deg,#070d1a,#0c1628,#070d1a);
            border-bottom:1px solid rgba(100,255,218,.08);
            padding:18px 28px 16px 28px;display:flex;align-items:center;
            justify-content:space-between;flex-wrap:wrap;gap:12px;
            margin:-1rem -1rem 1.5rem -1rem;">
  <div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.3rem;
                font-weight:700;color:#64ffda;letter-spacing:.04em;">
      📈 Stock Prediction Lab <span style="color:#e2e8f0;">2026</span>
    </div>
    <div style="font-family:'Manrope',sans-serif;font-size:.68rem;font-weight:500;
                color:#334155;letter-spacing:.16em;text-transform:uppercase;margin-top:3px;">
      7 AI Models · News Sentiment · Geopolitical Risk · Anchored Forecasts
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="display:inline-flex;align-items:center;gap:6px;
                background:rgba(100,255,218,.06);border:1px solid rgba(100,255,218,.18);
                border-radius:20px;padding:4px 14px;font-family:'IBM Plex Mono',monospace;
                font-size:.61rem;font-weight:500;color:#64ffda;letter-spacing:.08em;">
      <div style="width:6px;height:6px;border-radius:50%;background:#64ffda;
                  animation:pulse 1.5s infinite;"></div>
      LIVE DATA
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:#334155;">
      {now}
    </div>
  </div>
</div>
<style>@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.3;}}}}</style>
""".format(now=now_str), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  RUN
# ═══════════════════════════════════════════════
if run_btn:
    st.session_state.results={}; st.session_state.df_cache=None
    with st.spinner("Fetching market data..."):
        df_raw=load_data(ticker,str(start_d),str(end_d))
    if df_raw is None or df_raw.empty:
        st.error("No data returned."); st.stop()
    st.session_state.df_cache=df_raw
    real_price=float(get_close_array(df_raw)[-1])
    real_date=str(df_raw.index[-1].date())
    st.session_state.verified_last_price=real_price
    st.session_state.verified_last_date=real_date
    st.success("Last verified close: **{} ${:.2f}** ({})".format(ticker,real_price,real_date))

    with st.spinner("Analysing news sentiment and geopolitical risks..."):
        news_items=fetch_news_sentiment(ticker)
        sent_score,sent_breakdown=compute_aggregate_sentiment(news_items)
        geo_score,risk_factors=compute_geo_risk_score(news_items,ticker)
        st.session_state.news_items=news_items
        st.session_state.sent_score=sent_score
        st.session_state.geo_score=geo_score
        st.session_state.risk_factors=risk_factors
        st.session_state.sent_breakdown=sent_breakdown

    slabel,_,sicon=classify_sentiment(sent_score)
    st.info("{} News sentiment: **{}** (score: {:.2f}) | {} articles analysed".format(
        sicon,slabel,sent_score,sent_breakdown.get("total",0)))

    prog=st.progress(0)
    for i,(k,fn) in enumerate(RUNNER_MAP.items()):
        prog.progress((i+0.3)/len(RUNNER_MAP),
                      text="Training {}...".format(MODEL_META[k]["name"]))
        try:
            result=fn(ticker,str(start_d),str(end_d))
            if result is not None:
                model_lp=float(result.get("last_price",real_price))
                if model_lp!=0 and not np.isnan(model_lp) and model_lp!=real_price:
                    result["future_pred"]=result["future_pred"]*(real_price/model_lp)
                result["last_price"]=real_price
            st.session_state.results[k]=result
        except Exception as e:
            st.warning("{} skipped: {}".format(MODEL_META[k]["name"],str(e)))
            st.session_state.results[k]=None
    prog.empty()
    st.success("Analysis complete — algorithmic + sentiment forecasts ready!")


# ═══════════════════════════════════════════════
#  GUARD
# ═══════════════════════════════════════════════
if not st.session_state.results:
    st.markdown("""
    <div style='text-align:center;padding:70px 20px;
                border:1px dashed rgba(100,255,218,.12);
                border-radius:14px;margin-top:20px;'>
      <div style='font-size:2.8rem;margin-bottom:12px;'>📊</div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:1.4rem;
                  font-weight:700;color:#e2e8f0;margin-bottom:8px;'>
        Welcome to Stock Prediction Lab 2026
      </div>
      <div style='font-family:Manrope,sans-serif;font-size:.9rem;
                  color:#475569;margin-bottom:20px;'>
        7 AI models + live news sentiment analysis<br>
        Set End Date to today and click Run Full Analysis
      </div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:.62rem;
                  color:#1e293b;letter-spacing:.12em;'>
        ← RECOMMENDED: AAPL OR NVDA — JAN 2019 TO TODAY
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════
#  RESOLVE
# ═══════════════════════════════════════════════
all_res     = st.session_state.results
valid       = {k:v for k,v in all_res.items() if v is not None}
bk          = min(valid, key=lambda k: valid[k]["rmse"])
wk          = max(valid, key=lambda k: valid[k]["rmse"])
best        = valid[bk]
df          = st.session_state.df_cache
last_price  = st.session_state.verified_last_price or get_last_price(df)
last_date   = st.session_state.verified_last_date  or str(df.index[-1].date())
news_items  = st.session_state.news_items   or []
sent_score  = st.session_state.sent_score   or 0.0
geo_score   = st.session_state.geo_score    or 0.0
risk_factors= st.session_state.risk_factors or []
sent_breakdown=st.session_state.sent_breakdown or {}

adj_fp, adj_pct, adj_expl = compute_sentiment_adjustment(
    sent_score, geo_score, best["future_pred"])

tmrw     = float(best["future_pred"][0])
adj_tmrw = float(adj_fp[0])
chg      = tmrw - last_price; cp = chg/(last_price+1e-9)*100
dc       = "#64ffda" if chg>=0 else "#ff6b6b"
improv   = (valid[wk]["rmse"]-best["rmse"])/(valid[wk]["rmse"]+1e-9)*100
slabel, scolor, sicon = classify_sentiment(sent_score)


# ═══════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════
st.markdown("""
<div class="banner">
  <div>
    <div class="bl">Best Model</div>
    <div class="bn">{nm}</div>
    <span class="bt">{era}</span>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">Best RMSE</div>
    <div class="bv">{rmse:.4f}</div>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">Last Close ({dt})</div>
    <div class="bv" style="color:#e2e8f0;">${lc:.2f}</div>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">Algo Day-1 Forecast</div>
    <div class="bv" style="color:{dc};">{ar} ${t:.2f}
      <span style="font-size:.8rem;opacity:.8;"> ({p:+.2f}%)</span>
    </div>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">News Sentiment</div>
    <div class="bv" style="color:{sc};">{si} {sl}</div>
    <div style="font-family:'IBM Plex Mono',monospace;color:#334155;font-size:.6rem;">
      Score: {ss:+.2f} &nbsp;·&nbsp; {nt} articles
    </div>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">Sentiment-Adj Day-1</div>
    <div class="bv" style="color:#a78bfa;">${at:.2f}
      <span style="font-size:.75rem;opacity:.8;"> ({ap:+.1f}%)</span>
    </div>
  </div>
  <div class="bdv"></div>
  <div>
    <div class="bl">Stock / Period</div>
    <div class="bn">{stk}</div>
    <div style="font-family:'IBM Plex Mono',monospace;color:#334155;font-size:.6rem;">
      {sd} to {ed}
    </div>
  </div>
</div>""".format(
    nm=best["name"],era=MODEL_META[bk]["era"],rmse=best["rmse"],
    dt=last_date,lc=last_price,
    dc=dc,ar="▲" if chg>=0 else "▼",t=tmrw,p=cp,
    sc=scolor,si=sicon,sl=slabel,
    ss=sent_score,nt=sent_breakdown.get("total",0),
    at=adj_tmrw,ap=adj_pct,
    stk=sel,sd=str(start_d),ed=str(end_d),
), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  MAIN TABS
# ═══════════════════════════════════════════════
main_tabs = st.tabs([
    "📊  Sentiment Dashboard",
    "📉  RMSE Progression",
    "🔮  Model Deep-Dive",
])


# ════════════════════════════════════════════════════════
#  TAB 1 — SENTIMENT DASHBOARD
# ════════════════════════════════════════════════════════
with main_tabs[0]:
    st.markdown('<div class="sec">Market Sentiment — News · Geopolitics · Macro Risks</div>',
                unsafe_allow_html=True)
    expl(
        "<strong>What is sentiment analysis?</strong> "
        "Stock prices are driven by two forces: <strong>quantitative factors</strong> (price patterns, "
        "momentum, volume) which the 7 AI models capture, AND <strong>qualitative factors</strong> "
        "(company news, wars, interest rates, political events) which sentiment analysis captures. "
        "Headlines are fetched live, scored bullish or bearish, then used to adjust the forecast. "
        "A war or major negative event can push prices down regardless of what the algorithm predicts."
    )

    # ── Gauges ──────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(sentiment_gauge_chart(sent_score, "Company News Sentiment"),
                        use_container_width=True, config={"displayModeBar":False})
        expl("<strong>News Sentiment Gauge:</strong> Scores all recent headlines for bullish vs bearish language. "
             "Range: -100% (very bearish) to +100% (very bullish). Recent articles weighted more heavily.")

    with col2:
        st.plotly_chart(sentiment_gauge_chart(geo_score, "Geopolitical Risk Score"),
                        use_container_width=True, config={"displayModeBar":False})
        expl("<strong>Geo Risk Gauge:</strong> Detects war, sanctions, tariffs, recession signals, "
             "and central bank rate keywords. Negative = high risk. Positive = rate cuts/stimulus detected.")

    with col3:
        combined_score = 0.6*sent_score + 0.4*geo_score
        st.plotly_chart(sentiment_gauge_chart(combined_score, "Combined Sentiment Score"),
                        use_container_width=True, config={"displayModeBar":False})
        expl("<strong>Combined Score:</strong> 60% news sentiment + 40% geopolitical risk. "
             "Used to adjust the algorithmic forecast. +50% adds ~+5% to the 15-day forecast.")

    # ── Breakdown metrics ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">News Volume Breakdown</div>', unsafe_allow_html=True)
    bc1,bc2,bc3,bc4 = st.columns(4)
    with bc1: st.metric("Bullish Articles", str(sent_breakdown.get("bullish",0)))
    with bc2: st.metric("Bearish Articles", str(sent_breakdown.get("bearish",0)))
    with bc3: st.metric("Neutral Articles", str(sent_breakdown.get("neutral",0)))
    with bc4: st.metric("Total Analysed",   str(sent_breakdown.get("total",0)))

    # ── Sentiment timeline ────────────────────────────────
    if news_items:
        st.markdown("<br>", unsafe_allow_html=True)
        tl_chart = news_sentiment_timeline(news_items)
        if tl_chart:
            st.plotly_chart(tl_chart, use_container_width=True,
                            config={"displayModeBar":False})
        expl("<strong>How to read:</strong> Each bar = one news article. "
             "Green above the line = bullish. Red below = bearish. "
             "Dotted lines at ±25% mark the threshold. Hover for headline.")

    # ── Risk factors ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Active Risk Factors — Geopolitical · Macro · Sector</div>',
                unsafe_allow_html=True)
    if risk_factors:
        rf_cols = st.columns(min(3, len(risk_factors)))
        for idx, rf in enumerate(risk_factors[:9]):
            with rf_cols[idx % 3]:
                tag_class = "tag-risk" if rf["type"]=="risk" else (
                    "tag-oppo" if rf["type"]=="oppo" else "tag-warn")
                icon = "🔴" if rf["type"]=="risk" else ("🟢" if rf["type"]=="oppo" else "🟡")
                st.markdown("""
                <div class="macro-card">
                  <span class="macro-tag {cls}">{icon} {lbl}</span>
                  <div style="font-family:'Manrope',sans-serif;color:#475569;
                              font-size:.75rem;margin-top:7px;">
                    {impact} &nbsp;·&nbsp;
                    <span style="font-family:'IBM Plex Mono',monospace;
                                 font-size:.65rem;">Source: {src}</span>
                  </div>
                  <div style="font-family:'IBM Plex Mono',monospace;
                              color:#334155;font-size:.68rem;margin-top:3px;">
                    Weight: {w:+.1f}
                  </div>
                </div>""".format(
                    cls=tag_class,icon=icon,lbl=rf["label"],
                    impact="Negative" if rf["weight"]<0 else "Positive",
                    src=rf["source"],w=rf["weight"]),
                unsafe_allow_html=True)
    else:
        st.info("No significant geopolitical risk factors detected in current news.")

    expl("<strong>Risk factors:</strong> "
         "<span style='color:#ff6b6b;'>Red = Risk</span> — wars, sanctions, probes. "
         "<span style='color:#facc15;'>Yellow = Warning</span> — rate changes, oil, macro. "
         "<span style='color:#64ffda;'>Green = Opportunity</span> — rate cuts, AI demand, deals.")

    # ── Adjusted forecast comparison ─────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Sentiment-Adjusted vs Algorithmic Forecast</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="adj-banner">
      <div style="font-family:'IBM Plex Mono',monospace;color:#a78bfa;font-size:.6rem;
                  letter-spacing:.1em;text-transform:uppercase;margin-bottom:5px;">
        Sentiment Adjustment Applied
      </div>
      <div style="font-family:'Manrope',sans-serif;color:#e2e8f0;font-size:.92rem;
                  font-weight:600;margin-bottom:10px;">
        {expl_txt}
      </div>
      <div style="display:flex;gap:28px;flex-wrap:wrap;">
        <div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#334155;
                      font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;">
            Algo Day-1
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#64ffda;
                      font-size:1.1rem;font-weight:700;margin-top:2px;">
            ${tmrw:.2f}
          </div>
        </div>
        <div style="color:#1e293b;font-size:1.4rem;align-self:center;">→</div>
        <div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#334155;
                      font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;">
            Sentiment-Adj Day-1
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#a78bfa;
                      font-size:1.1rem;font-weight:700;margin-top:2px;">
            ${adj:.2f}
          </div>
        </div>
        <div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#334155;
                      font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;">
            15-Day Adjustment
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;color:{adc};
                      font-size:1.1rem;font-weight:700;margin-top:2px;">
            {ap:+.2f}%
          </div>
        </div>
      </div>
    </div>""".format(
        expl_txt=adj_expl, tmrw=tmrw, adj=adj_tmrw,
        adc="#64ffda" if adj_pct>=0 else "#ff6b6b", ap=adj_pct),
    unsafe_allow_html=True)

    st.plotly_chart(
        adjusted_vs_base_chart(best["future_pred"], adj_fp, last_price, last_date),
        use_container_width=True, config={"displayModeBar":False})

    expl("<strong>Chart:</strong> "
         "Purple dotted = pure algorithmic forecast (price patterns only). "
         "Solid teal/red = sentiment-adjusted forecast (adds news and geopolitical risk). "
         "Shaded band = adjustment zone. "
         "Positive news lifts the adjusted line above algorithmic; wars/sanctions push it below.")

    # ── News feed ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Latest Headlines — {} (Scored & Classified)</div>'.format(ticker),
                unsafe_allow_html=True)
    if news_items:
        for item in news_items[:10]:
            card_class = ("news-bull" if item["label"]=="BULLISH" else
                          "news-bear" if item["label"]=="BEARISH" else "news-neut")
            url_part   = ('<a href="{}" target="_blank" style="font-family:IBM Plex Mono,monospace;'
                          'font-size:.68rem;color:#60a5fa;text-decoration:none;'
                          'letter-spacing:.03em;">Read →</a>'.format(item["url"])
                          if item.get("url") else "")
            geo_html = ""
            for gt in item.get("geo_tags",[])[:2]:
                tc = "tag-risk" if gt["type"]=="risk" else (
                     "tag-oppo" if gt["type"]=="oppo" else "tag-warn")
                geo_html += '<span class="macro-tag {}">{}</span>'.format(tc, gt["label"])
            st.markdown("""
            <div class="news-card {cls}">
              <div class="news-title">{icon} {title}</div>
              <div class="news-meta" style="margin-top:4px;">
                <span style="color:{col};font-weight:700;">{lbl} ({sc:+.2f})</span>
                &nbsp;·&nbsp; {age}
                &nbsp;·&nbsp; {url}
              </div>
              {geo}
            </div>""".format(
                cls=card_class,icon=item["icon"],title=item["title"],
                col=item["color"],lbl=item["label"],sc=item["score"],
                age=item["age"],url=url_part,geo=geo_html),
            unsafe_allow_html=True)
    else:
        st.info("No recent news found. Yahoo Finance may have limited coverage.")

    # ── Forecast table ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec">15-Day Forecast — Algorithmic vs Sentiment-Adjusted</div>',
                unsafe_allow_html=True)
    ft = make_forecast_table(last_price, best["future_pred"], adj_fp)
    st.dataframe(style_ft(ft), use_container_width=True, height=510, hide_index=True)
    expl("<strong>Table:</strong> "
         "<strong>Algo ($)</strong> = pure algorithmic price. "
         "<strong>Sentiment Adj ($)</strong> = news-adjusted price. "
         "<strong>Adj Diff</strong> = sentiment impact in dollars. "
         "Educational only — not financial advice.")


# ════════════════════════════════════════════════════════
#  TAB 2 — RMSE PROGRESSION
# ════════════════════════════════════════════════════════
with main_tabs[1]:
    st.markdown('<div class="sec">RMSE Progression — 1970s ARIMA to 2026 FinGPT</div>',
                unsafe_allow_html=True)
    expl("<strong>What is RMSE?</strong> "
         "Root Mean Squared Error = average dollar prediction error during testing. "
         "RMSE of $8 means predictions were off by $8 on average. "
         "Lower = more accurate. The chart below proves each model era improved over its predecessor.")

    rmse_row=[(k,valid[k]["rmse"]) for k in MODEL_ORDER if k in valid]
    tokens=" → ".join(
        "<span style='font-family:IBM Plex Mono,monospace;color:{};font-size:.7rem;'>"
        "{} <b>{:.2f}</b></span>".format(
            MODEL_META[k]["accent"],MODEL_META[k]["name"].split("(")[0].strip(),r)
        for k,r in rmse_row)
    st.markdown("<p style='line-height:2.2;font-family:Manrope,sans-serif;'>{}</p>".format(tokens),
                unsafe_allow_html=True)
    st.plotly_chart(rmse_chart(valid), use_container_width=True,
                    config={"displayModeBar":False})

    rows_t, prev_r = [], None
    for k,r in rmse_row:
        vs = "First model"
        if prev_r is not None:
            d  = prev_r - r
            vs = "{:.1f}% {}".format(abs(d/prev_r*100), "BETTER" if d>0 else "WORSE")
        rows_t.append({"Era":MODEL_META[k]["era"],
                        "Model":MODEL_META[k]["name"].split("(")[0].strip(),
                        "RMSE":round(r,4),"vs Previous":vs,
                        "Status":"BEST" if k==bk else ("BASELINE" if k==wk else "")})
        prev_r = r

    tbl_df = pd.DataFrame(rows_t)
    def hl(row):
        if row["Status"]=="BEST":     return ["background-color:rgba(100,255,218,.06);color:#64ffda"]*len(row)
        if row["Status"]=="BASELINE": return ["background-color:rgba(255,107,107,.05);color:#ff6b6b"]*len(row)
        return [""]*len(row)
    st.dataframe(
        tbl_df.style.apply(hl,axis=1)
        .format({"RMSE":"{:.4f}"})
        .set_properties(**{"background-color":"#0a1628","color":"#94a3b8",
                           "border":"1px solid #1e293b",
                           "font-family":"IBM Plex Mono,monospace","font-size":"0.73rem"})
        .set_table_styles([{"selector":"th","props":[
            ("background","#060b14"),("color","#64ffda"),
            ("font-family","IBM Plex Mono,monospace"),("font-size","0.63rem"),
            ("text-transform","uppercase"),("letter-spacing",".06em"),
            ("border","1px solid #1e293b")]}]),
        use_container_width=True, hide_index=True, height=270)
    expl("<strong>Table:</strong> RMSE = average USD error on 5-day-ahead predictions. "
         "vs Previous = improvement over the prior model era. "
         "Consistent BETTER results prove AI advancement genuinely improves stock prediction.")


# ════════════════════════════════════════════════════════
#  TAB 3 — MODEL DEEP-DIVE
# ════════════════════════════════════════════════════════
with main_tabs[2]:
    st.markdown('<div class="sec">Individual Model Results — Select a Tab Below</div>',
                unsafe_allow_html=True)

    model_tabs = st.tabs([MODEL_META[k]["tab"] for k in MODEL_ORDER])
    for ti, key in enumerate(MODEL_ORDER):
        with model_tabs[ti]:
            res  = all_res.get(key)
            meta = MODEL_META[key]
            acc  = meta["accent"]

            if res is None:
                pkg = "tensorflow-cpu" if key in ("lstm","tft","fingpt") else "statsmodels"
                st.markdown("""
                <div style='padding:40px;text-align:center;
                            border:1px dashed rgba(100,255,218,.1);border-radius:12px;'>
                  <div style='font-family:Manrope,sans-serif;font-size:1rem;
                              font-weight:600;color:#e2e8f0;margin-bottom:8px;'>{name}</div>
                  <div style='font-family:Manrope,sans-serif;color:#475569;
                              font-size:.84rem;margin-bottom:12px;'>Not available or skipped.</div>
                  <code style='font-family:IBM Plex Mono,monospace;color:#64ffda;
                               background:#0a1628;padding:4px 14px;border-radius:6px;
                               font-size:.75rem;'>pip install {pkg}</code>
                </div>""".format(name=meta["name"],pkg=pkg), unsafe_allow_html=True)
                continue

            ib = (key==bk); iw = (key==wk)
            badge = (
                '<span class="bdg">★ BEST MODEL</span>' if ib else
                '<span style="background:rgba(255,107,107,.08);color:#ff6b6b;'
                'border:1px solid rgba(255,107,107,.25);border-radius:12px;'
                'padding:2px 9px;font-family:IBM Plex Mono,monospace;font-size:.6rem;'
                'margin-left:5px;letter-spacing:.04em;">BASELINE</span>' if iw else ""
            )

            st.markdown("""
            <div class="mcard" style="border-top:3px solid {acc};">
              <div class="mera" style="color:{acc};">{era} &nbsp;·&nbsp; Model {n} of 7</div>
              <div class="mtitle">{nm} {badge}</div>
              <div class="mdesc">{desc}</div>
              <span class="mpill" style="background:rgba(255,255,255,.03);
                    color:{acc};border:1px solid {acc}33;">
                RMSE: {rmse:.4f}
              </span>
              <span class="mpill" style="background:rgba(100,255,218,.04);
                    color:#64ffda;border:1px solid rgba(100,255,218,.18);">
                Expected: {rl}
              </span>
            </div>""".format(
                acc=acc,era=meta["era"],n=ti+1,nm=meta["name"],
                badge=badge,desc=meta["desc"],rmse=res["rmse"],rl=meta["rmse_label"]),
            unsafe_allow_html=True)

            res_adj, res_adj_pct, res_adj_expl = compute_sentiment_adjustment(
                sent_score, geo_score, res["future_pred"])

            ap   = float(100*(1-np.mean(np.abs(res["test_actual"]-res["test_pred"])/
                                         (np.abs(res["test_actual"])+1e-9))))
            d15  = float(res["future_pred"][-1])
            t15  = (d15 - last_price) / (last_price+1e-9) * 100
            tm   = float(res["future_pred"][0])
            tmd  = tm - last_price
            adj_d1 = float(res_adj[0])

            c1,c2,c3,c4,c5 = st.columns(5)
            with c1: st.metric("RMSE Score",         "{:.4f}".format(res["rmse"]),
                               help="Lower = better")
            with c2: st.metric("Test Accuracy",      "{:.1f}%".format(ap))
            with c3: st.metric("Algo Day-1",         "${:.2f}".format(tm),
                               delta="{:+.2f}".format(tmd))
            with c4: st.metric("Sentiment Adj Day-1","${:.2f}".format(adj_d1),
                               delta="{:+.2f}%".format(res_adj_pct),
                               delta_color="normal")
            with c5: st.metric("Day-15 Forecast",    "${:.2f}".format(d15),
                               delta="{:+.1f}%".format(t15))

            expl("{} Sentiment adjustment for {}: <strong>{:+.2f}%</strong> over 15 days. {}".format(
                sicon, meta["name"].split("(")[0], res_adj_pct, adj_expl))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="sec">Price Chart — Algorithmic & Sentiment-Adjusted Forecasts</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(pred_chart(df, res, accent=acc, adj_fp=res_adj, h=420),
                            use_container_width=True,
                            config={"displayModeBar":True,"scrollZoom":True})
            expl("<strong>Chart:</strong> "
                 "White = actual prices (test period). "
                 "Dotted {} = model predictions. ".format(acc) +
                 "Teal = algorithmic forecast. "
                 "Purple dashed = sentiment-adjusted forecast. "
                 "Gap between teal and purple shows the news impact.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="sec">{} — 15-Day Forecast | RMSE: {:.4f}</div>'.format(
                    meta["name"], res["rmse"]),
                unsafe_allow_html=True)
            ft = make_forecast_table(last_price, res["future_pred"], res_adj)
            st.dataframe(style_ft(ft), use_container_width=True, height=510, hide_index=True)
            expl("<strong>Table:</strong> Algo ($) = pure price prediction. "
                 "Sentiment Adj ($) = news-adjusted price. "
                 "Adj Diff = daily sentiment impact in dollars. "
                 "Educational only — not financial advice.")


# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("""
<div style="margin-top:30px;padding:14px 0;
            border-top:1px solid rgba(255,255,255,.04);text-align:center;">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;
               color:#1e293b;letter-spacing:.1em;">
    📈 STOCK PREDICTION LAB 2026 &nbsp;·&nbsp; EDUCATIONAL ONLY
    &nbsp;·&nbsp; NOT FINANCIAL ADVICE
    &nbsp;·&nbsp; SENTIMENT VIA YAHOO FINANCE
    &nbsp;·&nbsp; FORECASTS ANCHORED TO VERIFIED LAST CLOSE
  </span>
</div>
""", unsafe_allow_html=True)
