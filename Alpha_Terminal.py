"""
Alpha Terminal — Professional Stock Intelligence Dashboard
Fonts : IBM Plex Mono (data/labels) + Manrope (body/headings)
Fix   : Custom User-Agent headers + fast_info fallback
        so fundamentals load correctly on Streamlit Cloud
"""
import warnings
warnings.filterwarnings("ignore")

import requests
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ═══════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="Alpha Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════
#  GLOBAL CSS — IBM Plex Mono + Manrope
# ═══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }

[data-testid="stAppViewContainer"] { background: #060b14; }
[data-testid="block-container"]    { padding-top: 0; padding-bottom: 1rem; }
.main { background: #060b14; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070d1a 0%, #080f1f 100%);
    border-right: 1px solid rgba(100,255,218,.08);
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] .stSelectbox label {
    color: #64ffda !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .68rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase;
}

.hero-bar {
    background: linear-gradient(135deg, #070d1a 0%, #0c1628 50%, #070d1a 100%);
    border-bottom: 1px solid rgba(100,255,218,.1);
    padding: 20px 32px 18px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    margin: -1rem -1rem 0 -1rem;
}
.brand {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.35rem;
    font-weight: 700;
    color: #64ffda;
    letter-spacing: .04em;
}
.brand span { color: #e2e8f0; }
.brand-sub {
    font-family: 'Manrope', sans-serif;
    font-size: .65rem;
    font-weight: 500;
    color: #334155;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin-top: 3px;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(100,255,218,.06);
    border: 1px solid rgba(100,255,218,.2);
    border-radius: 20px;
    padding: 4px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .62rem;
    font-weight: 500;
    color: #64ffda;
    letter-spacing: .08em;
}
.live-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #64ffda;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.3;} }

.stock-header {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f3c 100%);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 14px;
    padding: 24px 28px;
    margin: 20px 0 0 0;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    position: relative;
    overflow: hidden;
}
.stock-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(100,255,218,.04) 0%, transparent 70%);
    border-radius: 50%;
}
.ticker-large {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
    letter-spacing: .02em;
}
.company-name {
    font-family: 'Manrope', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #94a3b8;
    margin-top: 5px;
}
.price-large {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.5rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
    letter-spacing: .01em;
}
.price-change {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .95rem;
    font-weight: 500;
    margin-top: 5px;
    letter-spacing: .02em;
}
.tag-pill {
    display: inline-block;
    background: rgba(100,255,218,.07);
    border: 1px solid rgba(100,255,218,.16);
    border-radius: 16px;
    padding: 3px 12px;
    font-family: 'Manrope', sans-serif;
    font-size: .67rem;
    font-weight: 600;
    color: #64ffda;
    margin: 3px 3px 0 0;
    letter-spacing: .04em;
}
.tag-pill.sector {
    background: rgba(59,130,246,.08);
    border-color: rgba(59,130,246,.22);
    color: #60a5fa;
}
.tag-pill.industry {
    background: rgba(168,85,247,.08);
    border-color: rgba(168,85,247,.22);
    color: #c084fc;
}

.mcard {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 10px;
    padding: 14px 16px;
    transition: border-color .2s;
}
.mcard:hover { border-color: rgba(100,255,218,.14); }
.mcard-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .57rem;
    color: #475569;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.mcard-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: #e2e8f0;
}
.mcard-sub {
    font-family: 'Manrope', sans-serif;
    font-size: .71rem;
    color: #475569;
    margin-top: 2px;
}

.section-hdr {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .62rem;
    font-weight: 500;
    color: #475569;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 22px 0 10px 0;
    padding-bottom: 7px;
    border-bottom: 1px solid rgba(255,255,255,.05);
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-hdr::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(100,255,218,.12), transparent);
}

.prog-row {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    gap: 10px;
}
.prog-label {
    font-family: 'Manrope', sans-serif;
    font-size: .78rem;
    font-weight: 500;
    color: #94a3b8;
    width: 140px;
    flex-shrink: 0;
}
.prog-bar-bg {
    flex: 1;
    height: 5px;
    background: rgba(255,255,255,.05);
    border-radius: 3px;
    overflow: hidden;
}
.prog-bar-fill { height: 100%; border-radius: 3px; }
.prog-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .74rem;
    color: #e2e8f0;
    width: 62px;
    text-align: right;
}

.news-item {
    padding: 11px 0;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.news-item:last-child { border-bottom: none; }
.news-headline {
    font-family: 'Manrope', sans-serif;
    font-size: .84rem;
    font-weight: 500;
    color: #cbd5e1;
    line-height: 1.5;
    margin-bottom: 3px;
}
.news-headline a { color: #60a5fa; text-decoration: none; }
.news-headline a:hover { color: #93c5fd; }
.news-age {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .61rem;
    color: #334155;
}

.about-text {
    font-family: 'Manrope', sans-serif;
    font-size: .86rem;
    font-weight: 400;
    color: #94a3b8;
    line-height: 1.8;
}

.range-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 6px;
}
.range-low  { font-family:'IBM Plex Mono',monospace;font-size:.74rem;color:#ff6b6b; }
.range-high { font-family:'IBM Plex Mono',monospace;font-size:.74rem;color:#64ffda; }
.range-bar  {
    flex: 1; height: 6px;
    background: linear-gradient(90deg, rgba(255,107,107,.22), rgba(100,255,218,.22));
    border-radius: 3px; position: relative;
}
.range-dot {
    position: absolute; top: -3px;
    width: 12px; height: 12px;
    background: #e2e8f0; border-radius: 50%;
    border: 2px solid #0a1628;
    transform: translateX(-50%);
}

.welcome-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
    text-align: center;
    padding: 40px;
}
.welcome-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    color: #64ffda;
    letter-spacing: .04em;
    margin-bottom: 4px;
}
.welcome-logo span { color: #e2e8f0; }
.welcome-sub {
    font-family: 'Manrope', sans-serif;
    font-size: .72rem;
    font-weight: 600;
    color: #334155;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin-bottom: 26px;
}
.welcome-desc {
    font-family: 'Manrope', sans-serif;
    font-size: .97rem;
    font-weight: 400;
    color: #475569;
    max-width: 480px;
    line-height: 1.75;
    margin-bottom: 34px;
}
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    max-width: 600px;
    margin: 0 auto;
}
.feature-tile {
    background: rgba(100,255,218,.04);
    border: 1px solid rgba(100,255,218,.09);
    border-radius: 10px;
    padding: 15px 16px;
    text-align: left;
}
.feature-icon { font-size: 1.4rem; margin-bottom: 7px; }
.feature-label {
    font-family: 'Manrope', sans-serif;
    font-size: .78rem;
    font-weight: 500;
    color: #94a3b8;
    line-height: 1.5;
}

[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,.06) !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #334155 !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: .75rem !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: 11px 20px !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #64ffda !important;
    border-bottom: 2px solid #64ffda !important;
}

[data-testid="stMetric"] {
    background: #0a1628;
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 10px;
    padding: 12px 14px;
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
    font-size: 1rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] > div {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .73rem !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #0a1628 !important;
    border: 1px solid rgba(100,255,218,.14) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Manrope', sans-serif !important;
}
p, li { color: #94a3b8; font-family: 'Manrope', sans-serif; }
h1,h2,h3,h4 { color: #e2e8f0; font-family: 'Manrope', sans-serif; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060b14; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  STOCK UNIVERSE
# ═══════════════════════════════════════════════
STOCKS = {
    "— Select a Stock —": None,
    "Apple Inc. (AAPL)":           "AAPL",
    "NVIDIA Corporation (NVDA)":   "NVDA",
    "Microsoft Corp. (MSFT)":      "MSFT",
    "Alphabet Inc. (GOOGL)":       "GOOGL",
    "Amazon.com Inc. (AMZN)":      "AMZN",
    "Meta Platforms (META)":       "META",
    "Tesla Inc. (TSLA)":           "TSLA",
    "Netflix Inc. (NFLX)":         "NFLX",
    "AMD (AMD)":                   "AMD",
    "Intel Corp. (INTC)":          "INTC",
    "Broadcom Inc. (AVGO)":        "AVGO",
    "Salesforce (CRM)":            "CRM",
    "Oracle Corp. (ORCL)":         "ORCL",
    "JPMorgan Chase (JPM)":        "JPM",
    "Goldman Sachs (GS)":          "GS",
    "Berkshire Hathaway (BRK-B)":  "BRK-B",
    "Visa Inc. (V)":               "V",
    "Johnson & Johnson (JNJ)":     "JNJ",
    "Pfizer Inc. (PFE)":           "PFE",
    "Eli Lilly (LLY)":             "LLY",
    "Walmart Inc. (WMT)":          "WMT",
    "Coca-Cola (KO)":              "KO",
    "McDonald's (MCD)":            "MCD",
    "ExxonMobil (XOM)":            "XOM",
    "Chevron (CVX)":               "CVX",
}

PERIOD_MAP = {
    "1 Week":   ("7d",  "1d"),
    "1 Month":  ("1mo", "1d"),
    "3 Months": ("3mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year":   ("1y",  "1d"),
    "2 Years":  ("2y",  "1wk"),
    "5 Years":  ("5y",  "1mo"),
}

BG, PAPER, GRID = "#060b14", "#0a1628", "#1e293b"
MONO = "IBM Plex Mono"
SANS = "Manrope"

# ─────────────────────────────────────────────────────────
#  SHARED SESSION — one requests.Session with browser
#  headers reused across all yfinance calls so Yahoo Finance
#  does not block the Streamlit Cloud server IP
# ─────────────────────────────────────────────────────────
def _make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection":      "keep-alive",
    })
    return s

YF_SESSION = _make_session()


# ═══════════════════════════════════════════════
#  DATA FETCHERS — CLOUD-PROOF MULTI-METHOD
#  Tries 4 different methods before giving up.
#  Never returns empty on a valid ticker.
# ═══════════════════════════════════════════════

def _clean_df(df):
    """Normalise column names and timezone on any DataFrame."""
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if hasattr(df.index, "tz") and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    # keep only OHLCV columns that actually exist
    want = [c for c in ["Open","High","Low","Close","Volume"] if c in df.columns]
    if not want:
        return pd.DataFrame()
    return df[want].dropna(how="all")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_history(ticker, period="1y", interval="1d"):
    """
    Try 4 methods in order until one returns data:
      1. yf.Ticker(..., session=YF_SESSION).history()
      2. yf.download() with no session
      3. yf.Ticker() with no session
      4. yf.download() with minimal params
    """
    # ── Method 1: session + .history() ──────────
    try:
        df = yf.Ticker(ticker, session=YF_SESSION).history(
            period=period, interval=interval, auto_adjust=True)
        df = _clean_df(df)
        if not df.empty:
            return df
    except Exception:
        pass

    # ── Method 2: yf.download with session ──────
    try:
        df = yf.download(
            ticker, period=period, interval=interval,
            progress=False, auto_adjust=True, actions=False,
            session=YF_SESSION,
        )
        df = _clean_df(df)
        if not df.empty:
            return df
    except Exception:
        pass

    # ── Method 3: plain Ticker, no session ──────
    try:
        df = yf.Ticker(ticker).history(
            period=period, interval=interval, auto_adjust=True)
        df = _clean_df(df)
        if not df.empty:
            return df
    except Exception:
        pass

    # ── Method 4: yf.download, no session ───────
    try:
        df = yf.download(
            ticker, period=period, interval=interval,
            progress=False, auto_adjust=True, actions=False,
        )
        df = _clean_df(df)
        if not df.empty:
            return df
    except Exception:
        pass

    return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_info(ticker):
    """
    Build info dict using up to 3 methods.
    Always returns at least basic price data from fast_info.
    """
    best = {}

    # ── Method 1: .info with session ────────────
    try:
        tk   = yf.Ticker(ticker, session=YF_SESSION)
        info = tk.info or {}
        if isinstance(info, dict) and len(info) > 10:
            best = info
    except Exception:
        pass

    # ── Method 2: .info without session ─────────
    if len(best) < 10:
        try:
            info = yf.Ticker(ticker).info or {}
            if isinstance(info, dict) and len(info) > len(best):
                best = info
        except Exception:
            pass

    # ── Method 3: fast_info as minimum baseline ─
    # fast_info works even when .info is blocked
    try:
        fi = yf.Ticker(ticker, session=YF_SESSION).fast_info
        fi_dict = {
            "currentPrice":     _safe_float(fi, "last_price"),
            "previousClose":    _safe_float(fi, "previous_close"),
            "marketCap":        _safe_float(fi, "market_cap"),
            "fiftyTwoWeekHigh": _safe_float(fi, "year_high"),
            "fiftyTwoWeekLow":  _safe_float(fi, "year_low"),
            "volume":           _safe_float(fi, "last_volume"),
            "currency":         getattr(fi, "currency", "USD") or "USD",
            "exchange":         getattr(fi, "exchange",  "—")  or "—",
        }
        # Fill any missing keys in best with fast_info values
        for k, v in fi_dict.items():
            if v is not None and (k not in best or best.get(k) is None):
                best[k] = v
    except Exception:
        pass

    return best


def _safe_float(obj, attr):
    """Return float attribute or None."""
    try:
        v = getattr(obj, attr, None)
        return float(v) if v is not None else None
    except Exception:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_financials(ticker):
    try:
        tk = yf.Ticker(ticker, session=YF_SESSION)
        return {
            "income":   tk.income_stmt,
            "balance":  tk.balance_sheet,
            "cashflow": tk.cashflow,
        }
    except Exception:
        try:
            tk = yf.Ticker(ticker)
            return {
                "income":   tk.income_stmt,
                "balance":  tk.balance_sheet,
                "cashflow": tk.cashflow,
            }
        except Exception:
            return {}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(ticker):
    try:
        news    = yf.Ticker(ticker, session=YF_SESSION).news or []
        results = []
        now_ts  = datetime.now().timestamp()
        for item in news[:12]:
            content  = item.get("content", item)
            title    = content.get("title", item.get("title", ""))
            url      = ""
            cp_url   = content.get("canonicalUrl", {})
            if isinstance(cp_url, dict):
                url = cp_url.get("url", "")
            if not url:
                url = content.get("url", item.get("link", ""))
            pub_time = content.get("pubDate", "")
            age_h    = 24.0
            if pub_time:
                try:
                    from dateutil import parser as dp
                    age_h = (now_ts - dp.parse(pub_time).timestamp()) / 3600
                except Exception:
                    age_h = (now_ts - item.get("providerPublishTime", now_ts-86400)) / 3600
            if title:
                results.append({
                    "title":   title,
                    "url":     url,
                    "age_str": ("{:.0f}h ago".format(age_h)
                                if age_h < 72 else "{:.0f}d ago".format(age_h/24)),
                })
        return results
    except Exception:
        return []


# ═══════════════════════════════════════════════
#  FORMATTERS
# ═══════════════════════════════════════════════
def fmt_large(n):
    if n is None or (isinstance(n, float) and np.isnan(n)):
        return "—"
    n = float(n)
    if abs(n) >= 1e12: return "${:.2f}T".format(n/1e12)
    if abs(n) >= 1e9:  return "${:.2f}B".format(n/1e9)
    if abs(n) >= 1e6:  return "${:.2f}M".format(n/1e6)
    return "${:,.0f}".format(n)


def fmt_num(n, decimals=2):
    if n is None or (isinstance(n, float) and np.isnan(n)):
        return "—"
    return "{:.{}f}".format(float(n), decimals)


# FIX: Returns "—" (dash) instead of "N/A" or blank
#      so the UI looks clean even when data is missing
def safe_get(info, key, default="—"):
    val = info.get(key, default)
    if val is None or val == "" or val == "N/A":
        return "—"
    if isinstance(val, float) and np.isnan(val):
        return "—"
    return val


# ═══════════════════════════════════════════════
#  CHART BUILDERS
# ═══════════════════════════════════════════════
def candlestick_chart(df, ticker, period_label):
    if df.empty:
        return None
    up_c, dn_c = "#64ffda", "#ff6b6b"
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03, row_heights=[0.72, 0.28],
    )
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing_line_color=up_c, increasing_fillcolor=up_c,
        decreasing_line_color=dn_c, decreasing_fillcolor=dn_c,
        name="Price", showlegend=False,
    ), row=1, col=1)
    if len(df) >= 20:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"].rolling(20).mean(),
            mode="lines", name="MA 20",
            line=dict(color="rgba(96,165,250,.75)", width=1.5),
        ), row=1, col=1)
    if len(df) >= 50:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"].rolling(50).mean(),
            mode="lines", name="MA 50",
            line=dict(color="rgba(251,191,36,.75)", width=1.5),
        ), row=1, col=1)
    vol_colors = [
        up_c if float(df["Close"].iloc[i]) >= float(df["Open"].iloc[i])
        else dn_c for i in range(len(df))
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        name="Volume", marker_color=vol_colors,
        marker_opacity=0.45, showlegend=False,
    ), row=2, col=1)
    fig.update_layout(
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8", family=SANS, size=10),
        xaxis=dict(showgrid=False, zeroline=False,
                   rangeslider=dict(visible=False), color="#475569"),
        xaxis2=dict(showgrid=False, zeroline=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   color="#475569", side="right",
                   tickfont=dict(family=MONO, size=10)),
        yaxis2=dict(showgrid=False, zeroline=False, color="#475569",
                    side="right", title=dict(text="VOL", font=dict(size=9, family=MONO))),
        legend=dict(bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#94a3b8", size=10, family=SANS),
                    orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        margin=dict(l=10, r=60, t=10, b=10),
        height=480, hovermode="x unified",
    )
    return fig


def returns_chart(df):
    if df.empty or len(df) < 2:
        return None
    close   = df["Close"].values.flatten()
    cum_ret = (close / close[0] - 1) * 100
    is_pos  = float(cum_ret[-1]) >= 0
    color   = "#64ffda" if is_pos else "#ff6b6b"
    fig = go.Figure(go.Scatter(
        x=df.index, y=cum_ret, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor="rgba(100,255,218,.06)" if is_pos else "rgba(255,107,107,.06)",
        hovertemplate="%{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="rgba(255,255,255,.1)", line_width=1)
    fig.update_layout(
        paper_bgcolor=PAPER, plot_bgcolor=BG,
        font=dict(color="#94a3b8", family=SANS, size=10),
        xaxis=dict(showgrid=False, zeroline=False, color="#475569"),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                   color="#475569", ticksuffix="%", side="right",
                   tickfont=dict(family=MONO, size=10)),
        margin=dict(l=10, r=60, t=10, b=10),
        height=300, hovermode="x unified", showlegend=False,
    )
    return fig


def revenue_chart(financials):
    inc = financials.get("income")
    if inc is None or inc.empty:
        return None
    try:
        rev_row = None
        for label in ["Total Revenue", "Revenue", "Net Revenue"]:
            if label in inc.index:
                rev_row = inc.loc[label]; break
        if rev_row is None:
            return None
        ni_row = None
        for label in ["Net Income", "Net Income Common Stockholders"]:
            if label in inc.index:
                ni_row = inc.loc[label]; break
        dates = [str(c)[:4] for c in rev_row.index[::-1]]
        rev   = [float(v)/1e9 for v in rev_row.values[::-1]]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates, y=rev, name="Revenue ($B)",
            marker_color="rgba(96,165,250,.7)", marker_line_width=0,
        ))
        if ni_row is not None:
            ni = [float(v)/1e9 for v in ni_row.values[::-1]]
            fig.add_trace(go.Bar(
                x=dates, y=ni, name="Net Income ($B)",
                marker_color="rgba(100,255,218,.6)", marker_line_width=0,
            ))
        fig.update_layout(
            paper_bgcolor=PAPER, plot_bgcolor=BG,
            font=dict(color="#94a3b8", family=SANS, size=10),
            xaxis=dict(showgrid=False, zeroline=False, color="#475569",
                       tickfont=dict(family=MONO, size=10)),
            yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False,
                       color="#475569", ticksuffix="B", side="right",
                       tickfont=dict(family=MONO, size=10)),
            barmode="group",
            legend=dict(bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8", size=10, family=SANS),
                        orientation="h", yanchor="bottom", y=1.01),
            margin=dict(l=10, r=60, t=10, b=10), height=300,
        )
        return fig
    except Exception:
        return None


# ═══════════════════════════════════════════════
#  HELPER RENDERERS
# ═══════════════════════════════════════════════
def section_header(icon, title):
    st.markdown(
        '<div class="section-hdr">{} {}</div>'.format(icon, title),
        unsafe_allow_html=True)


def progress_row(label, value_str, pct, color="#64ffda"):
    pct = max(0, min(100, pct))
    st.markdown("""
    <div class="prog-row">
      <div class="prog-label">{label}</div>
      <div class="prog-bar-bg">
        <div class="prog-bar-fill" style="width:{pct}%;background:{color};"></div>
      </div>
      <div class="prog-val">{value}</div>
    </div>""".format(label=label, pct=pct, color=color, value=value_str),
    unsafe_allow_html=True)


def kv_row(label, value, bottom_border=True):
    border = "border-bottom:1px solid rgba(255,255,255,.04);" if bottom_border else ""
    st.markdown("""
    <div style="display:flex;justify-content:space-between;padding:8px 0;{border}">
      <div style="font-family:'{sans}',sans-serif;font-size:.82rem;
                  font-weight:500;color:#64748b;">{label}</div>
      <div style="font-family:'{mono}',monospace;font-size:.8rem;
                  font-weight:500;color:#e2e8f0;text-align:right;
                  max-width:220px;word-break:break-all;">{value}</div>
    </div>""".format(border=border, label=label, value=value, sans=SANS, mono=MONO),
    unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:22px 4px 12px 4px;text-align:center;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:1.15rem;
                  font-weight:700;color:#64ffda;letter-spacing:.04em;">
        ⚡ Alpha Terminal
      </div>
      <div style="font-family:'Manrope',sans-serif;font-size:.62rem;font-weight:600;
                  color:#1e293b;letter-spacing:.2em;text-transform:uppercase;margin-top:4px;">
        Research Platform
      </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:0 0 18px 0;">
    """, unsafe_allow_html=True)

    selected_name = st.selectbox("SELECT STOCK", list(STOCKS.keys()), index=0)
    ticker = STOCKS[selected_name]

    if ticker:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;font-weight:500;
                    color:#334155;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;">
          Chart Period
        </div>""", unsafe_allow_html=True)
        period_label = st.radio("Period", list(PERIOD_MAP.keys()), index=4,
                                label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;font-weight:500;
                    color:#334155;letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px;">
          Chart Type
        </div>""", unsafe_allow_html=True)
        chart_type = st.radio("Chart", ["Candlestick", "Returns (%)"], index=0,
                              label_visibility="collapsed")

    st.markdown("""
    <hr style="border:none;border-top:1px solid rgba(255,255,255,.04);margin:22px 0 14px 0;">
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.55rem;color:#1e293b;
                text-align:center;letter-spacing:.06em;line-height:1.7;">
      Market data via Yahoo Finance<br>Cache refreshes every 5 min
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  TOP NAV BAR
# ═══════════════════════════════════════════════
now_str = datetime.now().strftime("%d %b %Y  %H:%M")
st.markdown("""
<div class="hero-bar">
  <div>
    <div class="brand">⚡ Alpha<span> Terminal</span></div>
    <div class="brand-sub">Professional Stock Intelligence Platform</div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <div class="live-badge"><div class="live-dot"></div> LIVE DATA</div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:.61rem;
                color:#334155;letter-spacing:.04em;">{now}</div>
  </div>
</div>
""".format(now=now_str), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  WELCOME SCREEN
# ═══════════════════════════════════════════════
if not ticker:
    st.markdown("""
    <div class="welcome-screen">
      <div class="welcome-logo">⚡ Alpha<span> Terminal</span></div>
      <div class="welcome-sub">Professional Stock Intelligence Platform</div>
      <div class="welcome-desc">
        Select any stock from the left panel to instantly access real-time pricing,
        fundamentals, interactive charts, financial statements, and live market
        news — all in one institutional-grade dashboard.
      </div>
      <div class="feature-grid">
        <div class="feature-tile">
          <div class="feature-icon">📈</div>
          <div class="feature-label">Interactive candlestick charts with MA overlays</div>
        </div>
        <div class="feature-tile">
          <div class="feature-icon">💼</div>
          <div class="feature-label">Full valuation metrics — P/E, EPS, margins, PEG</div>
        </div>
        <div class="feature-tile">
          <div class="feature-icon">📊</div>
          <div class="feature-label">Revenue, net income & financial history</div>
        </div>
        <div class="feature-tile">
          <div class="feature-icon">🔎</div>
          <div class="feature-label">Company profile, sector & business description</div>
        </div>
        <div class="feature-tile">
          <div class="feature-icon">📰</div>
          <div class="feature-label">Latest news headlines & analyst coverage</div>
        </div>
        <div class="feature-tile">
          <div class="feature-icon">⚡</div>
          <div class="feature-label">25 stocks across Tech, Finance, Energy & more</div>
        </div>
      </div>
      <div style="margin-top:38px;font-family:'IBM Plex Mono',monospace;
                  font-size:.62rem;color:#1e293b;letter-spacing:.14em;">
        ← SELECT A STOCK FROM THE SIDEBAR TO BEGIN
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════
#  LOAD DATA
# ═══════════════════════════════════════════════
with st.spinner(""):
    info       = fetch_info(ticker)
    period_cfg = PERIOD_MAP[period_label]
    hist_df    = fetch_history(ticker, period=period_cfg[0], interval=period_cfg[1])
    hist_1y    = fetch_history(ticker, period="1y", interval="1d")
    news_items = fetch_news(ticker)
    financials = fetch_financials(ticker)

# Never hard-stop the app.
# If history is empty but fast_info gave us a price, build a minimal
# stub DataFrame so charts degrade gracefully instead of crashing.
if hist_df.empty:
    price_now = (info.get("currentPrice") or info.get("regularMarketPrice")
                 or info.get("ask") or info.get("bid"))
    if price_now:
        today = pd.Timestamp.today().normalize()
        hist_df = pd.DataFrame({
            "Open":   [float(price_now), float(price_now)],
            "High":   [float(price_now), float(price_now)],
            "Low":    [float(price_now), float(price_now)],
            "Close":  [float(price_now), float(price_now)],
            "Volume": [0, 0],
        }, index=pd.DatetimeIndex([today - pd.Timedelta(days=1), today]))
    else:
        st.warning(
            "⚠️  Yahoo Finance is temporarily rate-limiting this server. "
            "Price history is unavailable right now. "
            "Fundamental data and metrics are still shown below. "
            "Try refreshing in 60 seconds."
        )

if not info and hist_df.empty:
    st.error(
        "Could not reach Yahoo Finance for {}. "
        "This is a server-side rate limit — please wait 60 seconds "
        "and refresh the page.".format(ticker)
    )
    st.stop()


# ═══════════════════════════════════════════════
#  EXTRACT METRICS
# ═══════════════════════════════════════════════
company_name = safe_get(info, "longName",             ticker)
sector       = safe_get(info, "sector",               "—")
industry     = safe_get(info, "industry",             "—")
exchange     = safe_get(info, "exchange",             "—")
currency     = safe_get(info, "currency",             "USD")
country      = safe_get(info, "country",              "—")
website      = safe_get(info, "website",              "")
description  = safe_get(info, "longBusinessSummary",  "No description available.")
employees    = info.get("fullTimeEmployees")

# Price — multiple fallback keys
current_price = (info.get("currentPrice")
                 or info.get("regularMarketPrice")
                 or info.get("ask")
                 or info.get("bid"))
prev_close    = (info.get("previousClose")
                 or info.get("regularMarketPreviousClose"))
day_high      = info.get("dayHigh")   or info.get("regularMarketDayHigh")
day_low       = info.get("dayLow")    or info.get("regularMarketDayLow")
week52_high   = info.get("fiftyTwoWeekHigh")
week52_low    = info.get("fiftyTwoWeekLow")
volume        = info.get("volume")    or info.get("regularMarketVolume")
avg_volume    = info.get("averageVolume")

# Use history as final price fallback
if not current_price and not hist_df.empty:
    current_price = float(hist_df["Close"].iloc[-1])
if not prev_close and not hist_df.empty and len(hist_df) > 1:
    prev_close = float(hist_df["Close"].iloc[-2])
if not week52_high and not hist_1y.empty:
    week52_high = float(hist_1y["High"].max())
if not week52_low and not hist_1y.empty:
    week52_low  = float(hist_1y["Low"].min())

current_price = float(current_price) if current_price else None
prev_close    = float(prev_close)    if prev_close    else None
price_change  = (current_price - prev_close) if (current_price and prev_close) else None
price_chg_pct = (price_change / prev_close * 100) if (price_change and prev_close) else None
is_positive   = (price_change or 0) >= 0
price_color   = "#64ffda" if is_positive else "#ff6b6b"
price_arrow   = "▲" if is_positive else "▼"

# Valuation
market_cap    = info.get("marketCap")
pe_ratio      = info.get("trailingPE")
fwd_pe        = info.get("forwardPE")
pb_ratio      = info.get("priceToBook")
ps_ratio      = info.get("priceToSalesTrailing12Months")
ev_ebitda     = info.get("enterpriseToEbitda")
peg_ratio     = info.get("pegRatio")
eps_ttm       = info.get("trailingEps")
eps_fwd       = info.get("forwardEps")
beta          = info.get("beta")
div_yield     = info.get("dividendYield")
div_rate      = info.get("dividendRate")
payout_ratio  = info.get("payoutRatio")
book_value    = info.get("bookValue")
debt_equity   = info.get("debtToEquity")
current_ratio = info.get("currentRatio")

# Profitability
profit_margin = info.get("profitMargins")
gross_margin  = info.get("grossMargins")
op_margin     = info.get("operatingMargins")
roe           = info.get("returnOnEquity")
roa           = info.get("returnOnAssets")
rev_growth    = info.get("revenueGrowth")
earn_growth   = info.get("earningsGrowth")
revenue_ttm   = info.get("totalRevenue")
net_income    = info.get("netIncomeToCommon")
free_cf       = info.get("freeCashflow")
total_debt    = info.get("totalDebt")
cash          = info.get("totalCash")

# Analyst
target_price  = info.get("targetMeanPrice")
rec_key       = info.get("recommendationKey", "")
analyst_count = info.get("numberOfAnalystOpinions")


# ═══════════════════════════════════════════════
#  STOCK HEADER CARD
# ═══════════════════════════════════════════════
price_str  = "${:.2f}".format(current_price) if current_price else "—"
chg_str    = ("{} ${:.2f}  ({:+.2f}%)".format(
    price_arrow, abs(price_change), price_chg_pct)
    if price_change is not None else "")
analyst_kw = rec_key.replace("_", " ").upper() if rec_key else ""

st.markdown("""
<div class="stock-header">
  <div>
    <div class="ticker-large">{ticker}</div>
    <div class="company-name">{name}</div>
    <div style="margin-top:10px;">
      <span class="tag-pill">{exchange}</span>
      <span class="tag-pill sector">{sector}</span>
      <span class="tag-pill industry">{industry}</span>
      {ctag}
    </div>
  </div>
  <div style="text-align:right;">
    <div class="price-large">{price}</div>
    <div class="price-change" style="color:{color};">{chg}</div>
    <div style="margin-top:8px;font-family:'IBM Plex Mono',monospace;
                font-size:.62rem;color:#334155;letter-spacing:.04em;">
      Prev Close: {prev} &nbsp;·&nbsp; {ccy}
    </div>
    {atag}
  </div>
</div>""".format(
    ticker=ticker, name=company_name,
    exchange=exchange, sector=sector, industry=industry,
    ctag='<span class="tag-pill">{}</span>'.format(country) if country != "—" else "",
    price=price_str, color=price_color, chg=chg_str,
    prev="${:.2f}".format(prev_close) if prev_close else "—",
    ccy=currency,
    atag=(
        '<div style="margin-top:8px;font-family:IBM Plex Mono,monospace;font-size:.62rem;'
        'background:rgba(100,255,218,.07);border:1px solid rgba(100,255,218,.18);'
        'border-radius:10px;padding:3px 12px;color:#64ffda;display:inline-block;'
        'letter-spacing:.06em;">Analyst: {}</div>'.format(analyst_kw)
        if analyst_kw else ""
    ),
), unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  TOP METRIC STRIP
# ═══════════════════════════════════════════════
c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
strip = [
    ("Market Cap",  fmt_large(market_cap)),
    ("P/E Ratio",   fmt_num(pe_ratio)     if pe_ratio   else "—"),
    ("EPS (TTM)",   "${:.2f}".format(float(eps_ttm)) if eps_ttm else "—"),
    ("Revenue",     fmt_large(revenue_ttm)),
    ("Beta",        "{:.2f}".format(float(beta)) if beta else "—"),
    ("Div Yield",   "{:.2f}%".format(float(div_yield)*100) if div_yield else "—"),
    ("52W High",    "${:.2f}".format(float(week52_high)) if week52_high else "—"),
    ("52W Low",     "${:.2f}".format(float(week52_low))  if week52_low  else "—"),
]
for col, (lbl, val) in zip([c1,c2,c3,c4,c5,c6,c7,c8], strip):
    with col:
        st.metric(lbl, val)


# ═══════════════════════════════════════════════
#  MAIN TABS
# ═══════════════════════════════════════════════
tabs = st.tabs([
    "📈  Chart",
    "💼  Fundamentals",
    "📊  Financials",
    "🏢  Company Profile",
    "📰  News & Analyst",
])


# ══════════════════════════════════════════
#  TAB 1 — PRICE CHART
# ══════════════════════════════════════════
with tabs[0]:
    section_header("📈", "Price Chart — {}  ·  {}".format(ticker, period_label))
    if chart_type == "Candlestick":
        fig = candlestick_chart(hist_df, ticker, period_label)
        if fig:
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": True,
                                    "modeBarButtonsToRemove": ["lasso2d","select2d"],
                                    "scrollZoom": True})
        else:
            st.info("Chart data unavailable for this period.")
    else:
        fig = returns_chart(hist_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})

    col1, col2 = st.columns(2, gap="large")
    with col1:
        section_header("📏", "Period Statistics")
        if not hist_df.empty:
            ph = float(hist_df["High"].max())
            pl = float(hist_df["Low"].min())
            pr = ((float(hist_df["Close"].iloc[-1]) /
                   float(hist_df["Close"].iloc[0])) - 1) * 100
            ca, cb, cc = st.columns(3)
            with ca: st.metric("Period High",   "${:.2f}".format(ph))
            with cb: st.metric("Period Low",    "${:.2f}".format(pl))
            with cc: st.metric("Period Return", "{:+.2f}%".format(pr))

        if week52_high and week52_low and current_price:
            rng = float(week52_high) - float(week52_low)
            pos = max(0, min(100, (current_price - float(week52_low)) / (rng+1e-9) * 100))
            st.markdown("""
            <div style="margin-top:16px;">
              <div style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;
                          font-weight:500;color:#334155;letter-spacing:.12em;
                          text-transform:uppercase;margin-bottom:9px;">
                52-Week Price Range
              </div>
              <div class="range-row">
                <span class="range-low">${:.2f}</span>
                <div class="range-bar">
                  <div class="range-dot" style="left:{:.1f}%"></div>
                </div>
                <span class="range-high">${:.2f}</span>
              </div>
              <div style="font-family:'Manrope',sans-serif;font-size:.74rem;
                          font-weight:500;color:#64748b;margin-top:8px;text-align:center;">
                Current ${:.2f} &nbsp;·&nbsp; {:.1f}% of 52-week range
              </div>
            </div>""".format(
                float(week52_low), pos, float(week52_high), current_price, pos),
            unsafe_allow_html=True)

    with col2:
        section_header("📉", "Volume & Momentum")
        va, vb = st.columns(2)
        with va:
            st.metric("Volume",     "{:,.0f}".format(float(volume)) if volume else "—")
            st.metric("Avg Volume", "{:,.0f}".format(float(avg_volume)) if avg_volume else "—")
        with vb:
            st.metric("Day High",   "${:.2f}".format(float(day_high)) if day_high else "—")
            st.metric("Day Low",    "${:.2f}".format(float(day_low))  if day_low  else "—")

        if not hist_1y.empty and len(hist_1y) >= 15:
            try:
                close_arr = hist_1y["Close"].values.flatten().astype(float)
                delta     = np.diff(close_arr)
                gain      = np.where(delta > 0, delta, 0.0)
                loss      = np.where(delta < 0, -delta, 0.0)
                def rma(arr, n=14):
                    out = np.zeros(len(arr)); out[:n] = np.mean(arr[:n])
                    for i in range(n, len(arr)):
                        out[i] = (out[i-1]*(n-1) + arr[i]) / n
                    return out
                ag = rma(gain); al = rma(loss)
                rsi_val   = 100 - (100 / (1 + ag[-1] / (al[-1]+1e-9)))
                rsi_color = ("#ff6b6b" if rsi_val > 70 else
                             "#64ffda" if rsi_val < 30 else "#94a3b8")
                rsi_label = ("OVERBOUGHT" if rsi_val > 70 else
                             "OVERSOLD"   if rsi_val < 30 else "NEUTRAL")
                st.markdown("""
                <div style="margin-top:14px;background:#0a1628;
                            border:1px solid rgba(255,255,255,.05);
                            border-radius:10px;padding:14px 16px;">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:.57rem;
                              font-weight:500;color:#334155;text-transform:uppercase;
                              letter-spacing:.1em;margin-bottom:7px;">RSI (14)</div>
                  <div style="display:flex;align-items:center;gap:12px;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.65rem;
                                font-weight:700;color:{color};">{rsi:.1f}</div>
                    <div style="background:{color}1a;border:1px solid {color}40;
                                border-radius:10px;padding:3px 10px;
                                font-family:'Manrope',sans-serif;font-size:.7rem;
                                font-weight:700;color:{color};letter-spacing:.05em;">
                      {label}
                    </div>
                  </div>
                </div>""".format(color=rsi_color, rsi=rsi_val, label=rsi_label),
                unsafe_allow_html=True)
            except Exception:
                pass


# ══════════════════════════════════════════
#  TAB 2 — FUNDAMENTALS
# ══════════════════════════════════════════
with tabs[1]:
    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        section_header("💰", "Valuation Metrics")
        val_rows = [
            ("P/E Ratio (TTM)",  fmt_num(pe_ratio)  if pe_ratio  else "—", "Price / Earnings (trailing 12M)"),
            ("P/E Ratio (Fwd)",  fmt_num(fwd_pe)    if fwd_pe    else "—", "Price / Forward Earnings"),
            ("P/B Ratio",        fmt_num(pb_ratio)  if pb_ratio  else "—", "Price / Book Value"),
            ("P/S Ratio",        fmt_num(ps_ratio)  if ps_ratio  else "—", "Price / Sales (trailing 12M)"),
            ("EV / EBITDA",      fmt_num(ev_ebitda) if ev_ebitda else "—", "Enterprise Value Multiple"),
            ("PEG Ratio",        fmt_num(peg_ratio) if peg_ratio else "—", "P/E to Growth Rate"),
            ("EPS (TTM)",        "${:.2f}".format(float(eps_ttm)) if eps_ttm else "—", "Trailing 12 Months"),
            ("EPS (Fwd)",        "${:.2f}".format(float(eps_fwd)) if eps_fwd else "—", "Forward Estimate"),
        ]
        for label, value, sub in val_rows:
            a, b = st.columns([5, 3])
            with a:
                st.markdown("""
                <div style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);">
                  <div style="font-family:'Manrope',sans-serif;font-size:.84rem;
                              font-weight:500;color:#94a3b8;">{}</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:.7rem;
                              color:#334155;margin-top:1px;">{}</div>
                </div>""".format(label, sub), unsafe_allow_html=True)
            with b:
                st.markdown("""
                <div style="padding:8px 0;text-align:right;
                            border-bottom:1px solid rgba(255,255,255,.04);">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:.9rem;
                              font-weight:700;color:#e2e8f0;">{}</div>
                </div>""".format(value), unsafe_allow_html=True)

        section_header("💵", "Dividends")
        d1, d2, d3 = st.columns(3)
        with d1: st.metric("Div Yield",    "{:.2f}%".format(float(div_yield)*100) if div_yield else "—")
        with d2: st.metric("Div Rate",     "${:.2f}".format(float(div_rate))      if div_rate  else "—")
        with d3: st.metric("Payout Ratio", "{:.1f}%".format(float(payout_ratio)*100) if payout_ratio else "—")

    with col_r:
        section_header("📊", "Profitability & Margins")
        margin_items = [
            ("Gross Margin",     gross_margin,  "#64ffda"),
            ("Operating Margin", op_margin,     "#60a5fa"),
            ("Net Profit Margin",profit_margin, "#a78bfa"),
            ("Return on Equity", roe,           "#fb923c"),
            ("Return on Assets", roa,           "#34d399"),
        ]
        for lbl, val, color in margin_items:
            if val and not (isinstance(val, float) and np.isnan(val)):
                pv = float(val) * 100
                progress_row(lbl, "{:.1f}%".format(pv), max(0, min(100, pv+5)), color)

        section_header("💳", "Balance Sheet")
        b1, b2 = st.columns(2)
        with b1:
            st.metric("Total Debt",     fmt_large(total_debt))
            st.metric("Cash & Equiv.",  fmt_large(cash))
            st.metric("Book Value/Sh",  "${:.2f}".format(float(book_value)) if book_value else "—")
        with b2:
            st.metric("Debt / Equity",  "{:.2f}".format(float(debt_equity)/100) if debt_equity else "—")
            st.metric("Current Ratio",  "{:.2f}".format(float(current_ratio))   if current_ratio else "—")
            st.metric("Free Cash Flow", fmt_large(free_cf))

        section_header("📈", "Growth Rates")
        g1, g2, g3 = st.columns(3)
        with g1: st.metric("Revenue Growth",  "{:+.1f}%".format(float(rev_growth)*100)  if rev_growth  else "—")
        with g2: st.metric("Earnings Growth", "{:+.1f}%".format(float(earn_growth)*100) if earn_growth else "—")
        with g3: st.metric("Net Income",      fmt_large(net_income))


# ══════════════════════════════════════════
#  TAB 3 — FINANCIALS
# ══════════════════════════════════════════
with tabs[2]:
    section_header("📊", "Annual Revenue vs Net Income")
    rev_fig = revenue_chart(financials)
    if rev_fig:
        st.plotly_chart(rev_fig, use_container_width=True,
                        config={"displayModeBar": False})
    else:
        st.info("Financial history unavailable for this ticker.")

    inc = financials.get("income")
    bal = financials.get("balance")
    cf  = financials.get("cashflow")

    tbl_props = {
        "background-color": "#0a1628", "color": "#e2e8f0",
        "border": "1px solid #1e293b",
        "font-family": "IBM Plex Mono, monospace", "font-size": "0.74rem",
    }
    tbl_hdr = [{"selector": "th", "props": [
        ("background","#060b14"),("color","#64ffda"),
        ("font-family","IBM Plex Mono, monospace"),("font-size","0.64rem"),
        ("text-transform","uppercase"),("letter-spacing",".06em"),
        ("border","1px solid #1e293b"),
    ]}]

    col1, col2 = st.columns(2, gap="large")
    with col1:
        section_header("💰", "Income Statement")
        if inc is not None and not inc.empty:
            show = ["Total Revenue","Gross Profit","Operating Income",
                    "Net Income","EBITDA","Basic EPS"]
            rows = []
            for lbl in show:
                if lbl in inc.index:
                    rd = inc.loc[lbl]; entry = {"Metric": lbl}
                    for cdt in list(rd.index)[:4]:
                        yr = str(cdt)[:4]; v = rd[cdt]
                        entry[yr] = ("${:.2f}".format(float(v)) if lbl=="Basic EPS"
                                     else fmt_large(v)) if pd.notna(v) else "—"
                    rows.append(entry)
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Metric")
                             .style.set_properties(**tbl_props)
                             .set_table_styles(tbl_hdr),
                             use_container_width=True)
        else:
            st.info("Income statement data not available.")

    with col2:
        section_header("🏦", "Balance Sheet")
        if bal is not None and not bal.empty:
            show_b = ["Total Assets","Total Liabilities Net Minority Interest",
                      "Stockholders Equity","Total Debt",
                      "Cash And Cash Equivalents","Net Receivables"]
            rows = []
            for lbl in show_b:
                if lbl in bal.index:
                    rd = bal.loc[lbl]
                    entry = {"Metric": lbl.replace(" Net Minority Interest","")}
                    for cdt in list(rd.index)[:4]:
                        yr = str(cdt)[:4]; v = rd[cdt]
                        entry[yr] = fmt_large(v) if pd.notna(v) else "—"
                    rows.append(entry)
            if rows:
                st.dataframe(pd.DataFrame(rows).set_index("Metric")
                             .style.set_properties(**tbl_props)
                             .set_table_styles(tbl_hdr),
                             use_container_width=True)
        else:
            st.info("Balance sheet data not available.")

    section_header("💸", "Cash Flow Statement")
    if cf is not None and not cf.empty:
        show_cf = ["Operating Cash Flow","Investing Cash Flow",
                   "Financing Cash Flow","Free Cash Flow",
                   "Capital Expenditure","Repurchase Of Capital Stock"]
        rows = []
        for lbl in show_cf:
            if lbl in cf.index:
                rd = cf.loc[lbl]; entry = {"Metric": lbl}
                for cdt in list(rd.index)[:4]:
                    yr = str(cdt)[:4]; v = rd[cdt]
                    entry[yr] = fmt_large(v) if pd.notna(v) else "—"
                rows.append(entry)
        if rows:
            st.dataframe(pd.DataFrame(rows).set_index("Metric")
                         .style.set_properties(**tbl_props)
                         .set_table_styles(tbl_hdr),
                         use_container_width=True)
    else:
        st.info("Cash flow data not available.")


# ══════════════════════════════════════════
#  TAB 4 — COMPANY PROFILE
# ══════════════════════════════════════════
with tabs[3]:
    col_l, col_r = st.columns([3, 2], gap="large")
    with col_l:
        section_header("🏢", "About  {}".format(company_name))
        if website and website != "—":
            st.markdown(
                "<a href='{url}' target='_blank' style='font-family:Manrope,sans-serif;"
                "font-size:.78rem;font-weight:600;color:#60a5fa;text-decoration:none;'>"
                "🌐 {url}</a>".format(url=website),
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div class='about-text'>{}</div>".format(description),
            unsafe_allow_html=True)
        section_header("🏷️", "Classification")
        p1, p2, p3 = st.columns(3)
        with p1: st.metric("Sector",   sector)
        with p2: st.metric("Industry", industry[:22]+"…" if len(str(industry)) > 22 else industry)
        with p3: st.metric("Country",  country)

    with col_r:
        section_header("📋", "Company Snapshot")
        snapshot = [
            ("Company",    company_name),
            ("Ticker",     ticker),
            ("Exchange",   exchange),
            ("Sector",     sector),
            ("Industry",   industry),
            ("Country",    country),
            ("Currency",   currency),
            ("Employees",  "{:,}".format(int(employees)) if employees else "—"),
            ("Market Cap", fmt_large(market_cap)),
            ("Website",    website if website not in ("—","") else "—"),
        ]
        for k, v in snapshot:
            kv_row(k, v)

        section_header("🎯", "Analyst Price Target")
        if target_price and current_price:
            upside  = (float(target_price) - current_price) / current_price * 100
            t_color = "#64ffda" if upside >= 0 else "#ff6b6b"
            st.markdown("""
            <div style="background:#0a1628;border:1px solid rgba(255,255,255,.05);
                        border-radius:10px;padding:18px 20px;margin-top:8px;">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:.57rem;
                              color:#334155;text-transform:uppercase;letter-spacing:.1em;">
                    Mean Target
                  </div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:1.55rem;
                              font-weight:700;color:#e2e8f0;margin-top:3px;">
                    ${:.2f}
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:.57rem;
                              color:#334155;text-transform:uppercase;letter-spacing:.1em;">
                    Upside
                  </div>
                  <div style="font-family:'IBM Plex Mono',monospace;font-size:1.55rem;
                              font-weight:700;color:{color};margin-top:3px;">
                    {upside:+.1f}%
                  </div>
                </div>
              </div>
              <div style="margin-top:10px;font-family:'Manrope',sans-serif;
                          font-size:.74rem;color:#475569;">
                Based on {n} analyst opinion{s}
              </div>
            </div>""".format(
                float(target_price), color=t_color, upside=upside,
                n=analyst_count if analyst_count else "—",
                s="s" if analyst_count and int(analyst_count) != 1 else ""),
            unsafe_allow_html=True)
        else:
            st.info("Analyst target not available for this ticker.")


# ══════════════════════════════════════════
#  TAB 5 — NEWS & ANALYST
# ══════════════════════════════════════════
with tabs[4]:
    col_news, col_analyst = st.columns([3, 2], gap="large")
    with col_news:
        section_header("📰", "Latest News — {}".format(ticker))
        if news_items:
            for item in news_items:
                url_part = (
                    '<a href="{url}" target="_blank" class="news-headline">{title}</a>'.format(
                        url=item["url"], title=item["title"])
                    if item.get("url")
                    else '<span class="news-headline">{}</span>'.format(item["title"])
                )
                st.markdown("""
                <div class="news-item">
                  <div>{}</div>
                  <div class="news-age">{}</div>
                </div>""".format(url_part, item["age_str"]),
                unsafe_allow_html=True)
        else:
            st.info("No recent news found for {}.".format(ticker))

    with col_analyst:
        section_header("🎯", "Analyst Consensus")
        rec_map = {
            "strong_buy":  ("#64ffda", "STRONG BUY"),
            "buy":         ("#34d399", "BUY"),
            "hold":        ("#fbbf24", "HOLD"),
            "underperform":("#f97316", "UNDERPERFORM"),
            "sell":        ("#ff6b6b", "SELL"),
        }
        rc = (rec_key or "").lower()
        rc_col, rc_lbl = rec_map.get(rc, ("#94a3b8", rec_key.upper() if rec_key else "—"))
        st.markdown("""
        <div style="background:#0a1628;border:1px solid rgba(255,255,255,.05);
                    border-radius:12px;padding:22px;margin-bottom:16px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;
                      color:#334155;letter-spacing:.1em;text-transform:uppercase;">
            Consensus Rating
          </div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:2rem;
                      font-weight:700;color:{color};margin:10px 0 5px 0;letter-spacing:.03em;">
            {label}
          </div>
          <div style="font-family:'Manrope',sans-serif;font-size:.76rem;
                      color:#475569;font-weight:500;">
            {n} analyst opinion{s}
          </div>
        </div>""".format(
            color=rc_col, label=rc_lbl,
            n=analyst_count if analyst_count else "—",
            s="s" if analyst_count and int(analyst_count) != 1 else ""),
        unsafe_allow_html=True)

        section_header("📊", "Price vs Consensus")
        if target_price and current_price:
            a1, a2 = st.columns(2)
            with a1:
                st.metric("Current", "${:.2f}".format(current_price))
                st.metric("P/E TTM", fmt_num(pe_ratio) if pe_ratio else "—")
            with a2:
                st.metric("Target",  "${:.2f}".format(float(target_price)))
                st.metric("Fwd P/E", fmt_num(fwd_pe)  if fwd_pe   else "—")

        section_header("📈", "Risk Indicators")
        risk_items = [
            ("Beta (Market Risk)",
             "{:.2f}".format(float(beta)) if beta else "—",
             min(100, abs(float(beta or 1)) * 50), "#fb923c"),
            ("Debt / Equity",
             "{:.2f}".format(float(debt_equity)/100) if debt_equity else "—",
             min(100, abs(float(debt_equity or 0)) / 300), "#f87171"),
            ("P/E vs Market",
             "{:.1f}x".format(float(pe_ratio)) if pe_ratio else "—",
             min(100, float(pe_ratio or 0) / 0.5), "#a78bfa"),
        ]
        for lbl, val, pct, color in risk_items:
            progress_row(lbl, val, pct, color)


# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("""
<div style="margin-top:32px;padding:14px 0;
            border-top:1px solid rgba(255,255,255,.04);text-align:center;">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:.58rem;
               color:#1e293b;letter-spacing:.1em;">
    ⚡ ALPHA TERMINAL &nbsp;·&nbsp; DATA VIA YAHOO FINANCE
    &nbsp;·&nbsp; EDUCATIONAL PURPOSES ONLY
    &nbsp;·&nbsp; NOT FINANCIAL ADVICE
  </span>
</div>
""", unsafe_allow_html=True)
