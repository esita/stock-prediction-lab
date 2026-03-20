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
    padding: 12px 28px 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin: -1rem -1rem 0 -1rem;
    position: relative;
    min-height: 72px;
}
/* ── Logo strip (top-right) ─────────── */
.logo-strip {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}
.logo-pill {
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 10px;
    padding: 6px 8px;
    height: 56px;
    width: 56px;
    overflow: hidden;
    transition: border-color .2s;
}
.logo-pill:hover { border-color: rgba(100,255,218,.25); }
.logo-pill img {
    height: 44px;
    width: 44px;
    object-fit: contain;
}
.logo-sep {
    width: 1px;
    height: 32px;
    background: rgba(255,255,255,.08);
}
/* ── Centre title ───────────────────── */
.hero-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    pointer-events: none;
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
#  TOP NAV BAR — embedded VGSOM + IIT KGP logos
# ═══════════════════════════════════════════════
now_str = datetime.now().strftime("%d %b %Y  %H:%M")

# Logos are embedded as base64 — no external URL needed,
# works on Streamlit Cloud without any image hosting.
VGSOM_B64  = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAQABAADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiivRfA/wf17xpZ/bxJHp+nniOadSTL/uqOo96APOqK6Txv4QuvBHiSTR7qeOciNZUmQYDq3t25BH4VzdABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUU9EeSRURSzscBQMkmvoX4VfBcWvka/4pgzcD57ewccJ6NIPX/Z/OgDD+FXwafV/I17xLCU084eCzYYaf0Lei+3evcfE/iXSfAvhpr+82xQQqI4LeIAF2/hRR/nArR1nWLDw/pNxqWozrBawLuZm7+w9SfSvj/wCIHju+8d6817Puis4/ltbbdkRr6n1Y9zQBl+KfEt/4t8QXGsai4M0xwqD7saD7qj2FYtFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU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h6D/AJ5D+v5etdl8XPiQngvRvsVjIp1q8UiIf88U6GQ+/p/9avk+SV5pXlldnkclmZjkk+tAEdFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFeofCH4Zv4x1MalqUbLolq43ZGPtD/wBwe3rQB0/wU+Fq3Zh8Va7b5hU7rG3cfeI/5aMPT0/Ovoio4o0iiSONQkaAKqqMAAdqkoAK5rxv4xsfBPhybVLwhpMbLeDPzSydl+ncmtjVNTtNG0y41G/mWG1t0LyOx6Afzr48+Ifjm88deInvZd0dlFlLS3zxGnr/ALx6mgDC13XL7xHrVzquoymW6uG3Mew9APYDis2iigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiitfw54e1DxTrltpOmxb55jjPZF7s3oBQBr/D3wLe+OvEKWUO6Oyiw93cY/wBWnt/tHtX2HpOlWWiaXb6bp8CwWsC7ERR/nmsvwb4RsPBfh+HSrFc7fmmmI+aV+7GuioAKCcUV5D8bPiN/wjmlnQNMnA1W8T966nmCI/yZu3tz6UAeefGz4jf8JHqreH9LmzpVm/711PE8o/8AZV6D3z7V5DRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRSgEnA5NAE9naXGoXkNnaQvNcTOEjjQZLMegFfXPwu+Hdv4F0MGZVk1e6UNdSj+H0jX2H6muZ+C3wx/sC0TxHrEP8AxM7hP9Hhcf8AHvGe/wDvH9BXslABRRVe9vLfT7Ka8u5Vit4EMkkjHAVR1NAGB458Y2fgjw1Pqlzh5vuW0JPMsnYfT1r411fVbzXNVudT1CYzXVy5eRz6+g9BXTfEnx3ceOvEsl1lk0+AmOzhP8KZ+8f9o9f0ri6ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvcPgn8LzqU0XinWoP8AQ4mzZwOP9aw/jI/ujt6muO+FPw/k8ceIgblGGk2ZD3T/AN/0jHuf5Zr67ggitbeOCCNY4Y1CIijAVRwAKAJaKKKACvnD46fEb+0Lt/CmlTZtYG/02RT/AKyQfwfRe/v9K9H+L3xAXwZ4dNrZyY1i+UrBg8xL0aT/AA9/pXyU7tI7O5LMxySe5oAbRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABWr4e0G+8T65a6Tp0e+4nbaPRR3Y+gFZiqzsFUEsTgAd6+rvg58Ox4Q0P+0dQiA1i+QF8jmGPqE+vc/8A1qAOy8I+F7Hwf4cttIsF+WMZkkI5lkP3mNbtFFABWZr+uWXhzQ7vV9Qk2W1sm5vVj2Ue5PFafQV8sfGv4hf8JPrf9i6dNnSrByGZTxPL3b6DoPxoA4Pxb4mvfF3iO61i+PzytiOMHiNB91R9Kw6KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK7H4ceBrnxz4lS0AZLCDEl3MP4U/uj/aPQUAd78DPhyNTu18VarDmzt3xZxuOJZB1f6D+f0r6RqtY2VtptjBZWcSw20CCOKNRwqjoKs0AFFFY3ifxFZ+FfD13rF82IrdMhc8yN/Co9yaAPP8A42fEL/hGdE/sTTpcapfoQzKeYYuhP1PQfjXy11NaWv65e+JNcu9Xv333Fy5Y+ijso9gOKzKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKXqaALuk6Xea3qltpthCZrq4cJGg9a+yfAfg208EeGodMtwrzkb7mfHMsnc/QdB7Vw/wS+HP/CPaWviHU4caneR/uUYcwRH/wBmb+X417BQAUUUUAFfLHxv8e/8JJ4g/sWxm3aZpzlWKniWbozfQdB+PrXrnxl8eDwj4YNlZy41XUVaOLaeYk/if+g9/pXyYSScnkmgBKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK9S+CngL/hKfEn9qX0W7S9OYMwYcSy/wr9B1P4etee6LpF5r2s2mlWEZkubqQRoPTPc+w619p+EvDVn4S8NWmj2YBWBfnfHMjn7zH6mgDcooooAKpatqdpoulXWpX0oitraMySMewH9au184/Hzx79uvh4T0+XNvbMHvWU/fk7J9F6n3+lAHl3jPxTd+MfE93rF0SBI22GIniKMfdUf565rn6KKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK7r4WeB38beK4opkP9mWuJbt/VeyfVj+maAPWvgL4D/svS28U38WLu8Tbaqw5ji7t9W/l9a9rqOONIY0jjQIiKFVVGAoHQVJQAUUVFcTxWtvLcTuI4olLu7dFUDJNAHH/E7xvF4I8Jy3UbKdRuMxWcZ7v3b6L1/KvjmaaS4nknmdnlkYs7MclieprrfiT41m8b+K570MwsYSYrOM/wxg/e+rdT/wDWrjqACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKAJ7W1nvruG1to2lnmcJGijJZicAV9lfDrwZD4I8KW+nKFa8k/e3co/jkI5H0HQV5R8AfAfmyt4v1CH5EJjsFYdW6NJ+HQfj6V9C0AFFFFABXi/wAffGv9l6JH4aspMXd+N9wVPKwjt/wI/oD6161q+qWuiaRd6nevstrWMySN7DsPftXxP4p8QXXinxJe6zdk+ZcyFlXOdi9FUfQYFAGNRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABXReCfCtz4y8U2mkW+QjtvnkA/wBXGPvN/T6kVztfWHwV8DDwt4VGoXkW3U9SUSPkcxx/wp/U/X2oA9E07T7bStOt7CziEdtbxiONB2UVboooAKKKw/FviO28J+GL3WbrBW3T5Ez/AKxzwq/iaAPGf2hPGm5oPCVnLwMT3pU/98J/7N+VeBVc1TUbnV9UutRvJDJc3MjSyMe5JzVOgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKK+u/BeleAvFXguyNlo2k3ESwok6G2TzI5AOQ3G4NnPPfrXK+Kv2eNMvd9x4avXsJjk/ZrjMkR9g33l/8eoA+bqK6XxN4D8SeEZD/AGtpkscOeLhPniP/AAIcfgea5qgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiirFjZXGpX8FjaRtLcTyLHGi9WYnAFAHoXwa8Df8ACW+K1u7uLdpenESzZ6SP/Cn9T7D3r61rmvAnhO38GeFLTSYcNKo8y4kA/wBZKfvH+g9hXS0AFFFFABXzH8e/Gv8AbHiBPDlnLmz045nIPDz9/wDvkcfUmvafiZ40j8E+EZ71WH26fMNmh7yEfe+ijn8vWvjeaaS4nkmmdnlkYu7McliepoAjooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKANfw94l1bwrqiajo921vOvDY5WRf7rDuK+oPh38XdJ8aJHZXWyw1nHNuzfJL7xk9f8Ad6/Wvkino7xurxsVZTkMpwQaAPviWKOeJ4pUWSNwQyMMhh6EV5D40+Aej6x5l34dddLvW58k5MDn6dU/Dj2rmfhz8dZLfytJ8XSNJD92PUcZZfaQdx/tDn1z1r6Ct7mC7t47i2mSaGQbkkjbcrD1BoA+IvEvhLW/CN/9j1mxe3Y/ck6xyD1VuhrDr7w1XR9O1zT5LDU7OG7tZPvRyrkfUeh9xXgXjj9n+6tGkvvCchuYOWNlM37xfZG/i+h5+tAHhlFTXFvNa3ElvcRPDNG2145FIZT6EGoaACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvev2ffBAlll8W30Xyxkw2QYdW/if8A9lH41414c0K68S+ILLR7MZmupAgPZR3Y+wGTX21ouk2ug6NZ6VZJst7WIRoPXHf6nrQBoUUUUAFFFFAHl/xm+H99410a0udKw+oWDMVgZtolRsZAJ4zwP1r5g1TRdT0S6a21TT7m0mH8M8ZX8vWvu+q93Y2l/AYLy2huIW4McqB1P4GgD4Ior671v4KeCdZ3OunNYStzvsn2f+OnK/pXm2u/s46jAGk0PWIbodorpPLb/voZB/SgDw2iuk13wH4o8NEnVdFuoYx/y1Vd8f8A30uRXN0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABXf/Dz4p6t4GuFt2LXmju37y0dvuf7UZ/hPt0P61wFFAH3P4c8TaV4r0pNR0e7WeBuGHRo2/usOoNbFfDvhfxbrHg/Vl1DSLkxP0kjPMcq/3WXvX1V4A+Jmj+O7MJEy2uqIuZrKRvm+qH+Jf5d6ALXjL4deH/G1qy6harFeYxHewqBKvpz/ABD2NfNHjj4V+IPBLtPNF9s0zPy3kC/KP98fwn9PevsWo5Yo7iF4pY1kjdSrIwyGB6gigD4Eor6I8f8AwEjupJtS8JFIZDln09z8hP8A0zbt/unj6V8/XVpcWN3La3ULw3ETFJI5FwysOoIoAgooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK3vB3hq48W+KbHRrfI89/3rgf6uMcs35UAe3fs+eDBaadP4qvI8TXOYbQMPuxj7zfiePwPrXudVrCxt9M0+3sbSMR29vGscaD+FQMCrNABRRRQAV83fE34xa/a+MrrTfDuorbWVk3lM6RqxkkH3jlgeAePwr2D4meL08GeD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6x4vhIGQ8Wmnr7GX/wCJ/P0r36KKOCJIokVI0UKqKMBQOgAqSigAooooAKKKKAOK+Inw60/x7pPlyEW+pQAm2ugPu/7LeqmvkrxB4f1Lwxq82l6rbtBcxevKuvZlPcGvuquP+IHw/wBO8eaMba4AhvogTa3YXmNvQ+qnuKAPjCitXxB4f1LwxrM+larbmG5iP4OvZlPcGsqgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvpr9n7wj/ZnhybxFcx4udRO2HI5WFT/7M38hXgfg7w5N4s8VWGjQ5HnyDzHA+5GOWb8s19s2NnBp9jBZWyCOCCNYo1H8KqMCgCxRRRQAUUVk+Jdcg8NeHL/WLk/u7WFnx/eb+FfxOBQB8+ftB+K/7S8R2/h63kBg05d82D1mYdPwXH5mvGatajf3Gq6ldahdOXuLmVpZGPdmOTVWgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigArX8O+HdS8U61BpWlQGW5lPJ/hRe7MewFR6FoWo+JNXg0vS7dp7qZsKo6Ad2J7AetfXvgDwDp3gTRFtbYCW9lAN1dEcyt6D0UdhQA/wF4G0/wACaAlhbBZbp/nubooA0rf/ABI7CusoooAKKKKACuW8bePNH8C6YLrUnLzS5EFrH/rJT/QeprI+JHxR03wJaG3j2XesypmK1B4Qf3pPQe3U/rXynrmu6j4j1abU9VuXuLqY5LMeAOwA7AelAH0f4Q+POkeI9bj0zULBtLeY7YJnmDozf3WOBtz2r12vgEEggg4Ir6d+C/xOPiOyXw9rE+dWtk/cyuebmMep/vD9Rz60Aew0UUUAcn468BaV470g2t8nl3cYJtrtR88Tf1X1FfI/ijwvqfhHW5tK1SHZKnKOPuSr2ZT3Ffclct448DaZ450RrG+Xy50y1tdKPnhb+o9RQB8U0VreIvD2o+FtbuNJ1OBoriFsAkfLIvZlPcGsmgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoorW8NaHceJfEdho9tnzLqZY92M7V/ib8Bk0Ae9fs9eEfsWkXXia6jxNefubYkdI1PzH8WH/jte31U03T7bStMttPtE2W9tGsUa+igYq3QAUUUUAFfP8A+0V4r/48fC1tJ6XV0AfwRT+p/KvddRv7fS9Oub+6cJb20bSyMeyqMmviHxNrs/iXxJf6xc/6y6lL7f7q/wAK/gMCgDJooooAKKKKACiiigAooooAK19A8M6z4nvfsmjafNdy/wAWwYVf95jwPxrs/hd8K7jxxdfbr4yW+iQth5F4aZv7qf1NfUmj6JpugadHp+lWcVrbRjhIx19ye59zQB89aR+zlr1zGsmq6rZ2Of8AlnEpmYex6D9TW9/wzTaeVj/hJp/Mx1+yDH5bq94ooA+aNX/Zz1+1Rn0rVLO+x/yzkBhY/TqP1FeX6/4W1vwvdC21rTprSRvuFxlX/wB1hwfwr7nrP1fRdO17T5LDVLOK7tpOsci5/Eeh9xQB8IUV6n8TvhDd+DnfVNKEt3orH5jjc9t7N/s/7VeWUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABV/R9Jvte1a30zTbdp7u4bbGi/wAz6AdSaj07T7rVdRt7Cxgee5uHCRxoMlia+t/hr8NbHwHpe99lxrE6j7Tc4+7/ALCei/z6+gABY+Hfw80/wHo4ijCz6nOAbq7xyx/ur6KP1612tFFABRRRQAV5H8T/AIyWvhcT6NobJc60Pkkk6x2x9/7ze3bv6VU+LvxdXQUm8PeHpw2qMNtzcoci2H91f9v/ANB+vT5qd2dy7MWZjkknJJoAlvL251G8lu7yeS4uJm3SSyNuZj6k1XoooAKsWV7cadfQXtpK0NzA4kikXgqwOQar0UAfYvwx+IVt470FXdkj1W2ULdwA9T/fUf3T+nSu6r4a8L+JdQ8Ja/b6vpsm2aI/MhJ2yr3Vh3Br7J8KeKNP8X+H7fV9OfMcgw8bH5onHVW96ANyiiigDhfiX8PLTx5oZUBY9VtlJtJzxz/cb/ZP6V8jalp13pGoz6ffwPBdwOUljccqa+868v8Ai38MI/GWn/2npkcaa3bLx2+0IP4D7+h/D6AHyhRUksTwSvFKjJIjFWRhgqR1BFR0AFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAV73+zr4V33F94ouI/ljH2W1JH8R5dh+GB+Jrwq2t5bu6itoELzTOERB1ZicAV9ueD/D8Xhbwpp2jRYzbRASMP4nPLH8yaAN2iiigAoopCQASTgUAeMftB+K/7N8O2/h23fFxqJ8ybHaFT/Vv/QTXzRXX/EzxIfFPj3Ur9H3W6SeRb/8AXNOAfx5P41yFABRRRQAUUUUAFFFFABW94O8NXHi3xTY6NASvnyfvXA+5GOWb8qwa9+/Zu0VS2s646ZZdlpE3p/E//slAHuek6XZ6LpdtpthCIbW3jEcaL6D+tXqKKACiiigAooooAingiuYJIJ41kikUo6MMhgeoIr5R+LnwzPgfUY77Tyz6NeORGDyYH67Ce49D7e1fWdYfi3w3a+LPDN7o11wtwnyP3jccq34HFAHw5RV3VdMu9G1W60y9j8u6tZGikX3B7e1UqACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKXqaSvaPgX8O49cvj4m1WDfY2kmLWJxxNKP4iD1Vf5/QigDufgv8M/+Ea09fEGrwY1e6T91E6820Z9uznv6Dj1r16iigAooooAK8g+L/wAV4/DVrLoOiThtalXbLKh4tFP/ALOew7dfStD4s/FGLwXZHTNNKya5cx5XuLdT/G3v6D8T7/Kk00lxNJNNI0ksjFndzksT1JNADXdpHZ3YszHJJOSTTKKKACiiigAooooAK7j4ZfEC58CeIBK5aTS7khLuAen99f8AaH69K4eigD73sry21GygvbSVJredA8cinIZT0NWK+Z/gh8SW0bUI/DGqS/8AEuunxayMcCCU/wAP+6x/I/U19MUAFFFFAHhnxx+GYvreXxZo0H+lRLm+hQf6xB/y0A/vDv7D2r5zr79ZQylWAIPBBr5X+M3w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0Iv2gfBEkaux1GJj1R7bkfkxFAHqlFeYw/HnwLLIEa7vIgf43tWwPyya9A0nVrHXNMg1LTblLm0nXckiHg/4H2oAvUUUUAFFFFABRRRQAUUUUAFFQ3NxFaWs1zO4SKFGkdj2UDJNeD6r+0ko3JpOgZIf5ZLqfhl/3VHB/GgD36mlgoJJAA6k18qan8ffGt/GUgksbAEYzbW+T+blv8iuH1bxZ4g10n+1NZvrpTzskmbZ/wB89KAPsDV/iB4S0PcNQ1+xjYdY0k8xx/wFcn9K4DWv2ifDtmjLpFheahL2ZwIY/wAzk/pXzJRQB6R4i+N3jHXi0cF4ul256R2QKt+Ln5vyxXnk9xNdTNNcTSTSscs8jFmP1JqKigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK9s/Z18Rm08Q33h+aQ+VexedCpPAkTrj6qT/AN814nXR+AtU/sXx7od+W2rHdoHP+yx2t+hNAH25RRRQAUUUUAFFFFABRRRQByPxN1D+zPhrr9xu2k2jRKc45f5P/Zq+Lq+rPj/ffZPho0APN3eRRY9QMv8A+yCvlOgAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKUEqwI4I5pKKAPujwvqf9teFdJ1POTdWkcrf7xUZ/XNa9eZ/AnVP7R+GNrCWy1jPJbn894/RxXplABRRRQAUUUUAFFFFAHg/wC0peldO0CxB/1kssxGP7oUD/0I188V7H+0Zeibxvp9mCCLewDH2Znb+gWvHKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA99/Zr1TEmu6QzdRHcoPzVv/Za+gq+R/gdqv9mfE+xjZgsd7HJbN+K7l/8AHlWvrigAooooAKKKKACiiigD5A+NN99u+Kmr4bKweXCPmyBtRc/TnNef1ueMb46l401u9ySJr6ZlPX5d5x+mKw6ACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA0/D+pto3iLTdTUnNrcxzcdwrAkV90o6uiurBlYZBHQivgOvtj4e6r/bXw+0O/Lbne0RHOc5dPkb9VNAHT0UUUAFFFFABVLVrz+z9Hvb05At4JJeP9lSf6Vdrl/iNOtv8ADfxFI3ANhMg+rKVH6mgD4qdi7sx6scmm0UUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAV9ZfAW9+1fC21h/59LmaHp6tv/wDZ6+Ta+kf2bbsv4c1qzJ4iu0kHP95MdP8AgFAHt1FFFABRRRQAVwfxlna3+E2uspALJEnPo0qKf0JrvK8v+P06w/C+ZDnM13Cgx65Lf+y0AfKFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFe5fs2XoTXNdsSVzNbRzY7/IxH/tSvDa9J+BWofYfijZRlsLdwywH/vncP1UUAfW1FFFABRRRQAV5B+0XNs8AWUWcb9RTj1wj16/Xgn7St+gt9A04Md5eWdl7AAKo/m1AHz3RRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABVrTtQudK1K2v7OQx3NtKssTjsynIqrRQB9v8Ag3xVZeMvDVrq1m65dQs8QPMUgHzKf89MV0FfEfhDxrrXgrU/tmk3O1Wx51vJzHMB2Yf1HNfRPhb47eFtbt1XVZDo950KTZaNvdXA/wDQsUAep0Vzg8feDym7/hKtFx/1/wAf/wAVWFrPxm8EaPAzrq630o+7FZKZC34/d/WgDuLy8ttPs5ru7mSG3hUvJI7YVVHc18cfEvxgfGvjK51GPIsoh5FopGD5ak8n3JJP41f+IfxU1bx3ILbb9i0lG3JaI2dx/vO38R9ug/WuAoAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAru/BPwo8ReNlW5gjWy00n/AI/LgEK3+4vVv5e9X/g78P08aeIXudQjJ0iw2tMv/PZz91Ppxk+31r6whijt4Uii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RQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB//9k="
IITKGP_B64 = "data:image/png;base64,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9hxRmbJGHA+AsSeMnh20H9EgHofwFBvxE63d1rc8dWv6rU1WxYw1ad+LrS/IyEgOjP6vJxJJjLuy5x9+yT2rUxcu2bfrY3zlbny/o+IzU00uNxteeeR8zBIQ5zK7HgtiDu2j049D+CCam5p16bFnD5Kju0e665ZjlgxeUaHNezwkL5IJGP8A1RvBmD+j9iQEffQCukREBERAREQEREBERAREQEREBERAREQEREBERAREQEREHQ/BlrlDV9AxeTw3FWH3nWreSlvMfNiH3bNZ7XMikEZaf9Mn4WkEB3sAn66UAvXNhw2obTjrfH8mOs5SVv5/LW4bEdiOF08crYPFxDADJG32G+R9++lseBORsth90wuJy+75bBa42nbxzX15nthpmeKcRzOjYQHlk0wk7d7BAPfodTD8RWz5itxrV03NcuY3kS5byjLzH458ckdOvFHI0B8jR2XyOlB8ST18Y/n2HOyIiAiIgIiICIiC+adDh7NaJqOwci7znat2HFmgMNiqQklDIJ5QHfK4FjfIEHxIH2T77Wl5E2Lii/xvNrPHOt7PSfVyMWQdcycwlMrQx8T/ACawlsX9TD2PvoA/so1x3lNdhxL8dPosG0bRNkYm4mOaSYRPbI0tc17IntMhD2xeLe+j5v7/AIN7cpZ7PYXTK3A+u08de27OOjdsEWHx0UdbHtcWllSNsTfZHovkd2fv37HiHJ6LIyVKzjcjZx12J0NqrM+GaN32x7SWuB/2IKx0BERAREQEREBERAREQEREBERAREQEREBERAREQFmYOpDfzVGjYsNrQ2LMcUkzvqNrnAFx/wBge1hqa8PYHT8/sNuvu+zwa7jGUZfitSMdIfzDumRdMb+pwa53mfodMPZAKC2t25bxWpbVkdEyPBulS6/ibMlWtBboPivPiY7xbK6ck/qeB5eQb77+z9msOYs7x7mhg38f6oNbiNeWfI1XWHzuZYdIW+Hyv9uYGRscAPQ+R30e1cOS4955xGGptwlzC8paqWMFQmODJxtid/QAycGSMdHv/TPQ/kLn7kTMMzu438jFiqeJjJZCynUIMMLYo2xhrS30R0z799999nvtBH0REBERAREQEREEz4V3Oxx/yRjNpq061yesJWRxWAPDykjcxriSR105wPfY9A+wryl03m7PU7uR3zaMVxXq0073W3OfHRbYcSS4/FEQ+w4ns9yu7d32CVy0tztu0Zzar8N3O5Ce5NBWhqxGR5cGMjjbG3oE+uw0E9fZJP7oJPztDp3+cY72lbLNsNS1WYblueORksltv6ZpHCT9X+oR8nf8vcPXSr9EQEREBERAREQEREBERAREQEREBERAREQEREBERAVj8dcg63pWv/EOOtd2fMWJnPsWs/X/ADEUTB0I2RRggD/uLnH2ewPoKuEQdC5blTSJsR/4g0L2fp8lTYpuKmxtYCvjmuEXwiwPAAeDY+i2PvryDex12Tz0iICIiAiIgIiICIiAiIgnfFHEm88ntyT9PxcduPGtaZ3y2GRN8nd+LAXEduPif7D9yOwoRagmq2Za1mJ8U0LzHJG8dOa4Hogj+QVLeNuTt545/wAQ/wAm56XFjIMayy0RRyB/j34np7SA4eR6I6PtRGaWSaZ800jpJJHFz3uPZcT7JJ/coPwiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiIM7BYjKZ7L1sRhcfZyGQsu8IK1eMvkkPXfoD+wJ/sASvTZsBmtZzU+F2DF2sZka5Hy17MZY9vY7B6P2CCCCPRH0tnxjuuZ493bH7dgfy7r9Ev8GWGF0b2vYWOa4Ag9EOP0QVlcu8hZzk7dZ9q2BlWK1LGyFkNVhbHFG0fpaOyT+5PZJ9k/7IIgiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICD7W402PW5dirR7daydXDEP/ADEuOiZJO39B8fFryGn9XiD2frtXG7QuBhx4zeRtO/OxbsqcU5gx9b5WT/F8o7b59eJb30e/sFBCts4tFDVrW0aruGE3DFUXMGQOPEsc9MPPTHyRSNa4MJ9eQ79/fSrldY6tpvEfHnLOvYGLZtztZDY69WEVZaMDqlqteHh8M/TgfEhw76/pIBHZA6j+D4n4QzvJ1/j+htG8x5enPcilMlKv8INYPL+neXZH6HdHr36+kHNyK/tb494Jz+q7JslHaN+bS12GCa6JcfWD3Nlk+NvgA8gnv77I9KjctWigtyPpstf4fLI80pbEfi6WIPLQ49eu/XR67AIIQYaIiAiszi3XONthxn5fNy7/AD54Oe51bA4qK0wRDrp3t3l+/v119KcZnjLhTF6vrWwTZ7kWWHYzbFKvDi67p2mtL8Ugezy9Hy+uifX30g57Vl6nxOMlo1Lcdj3TA6njMnYkrYz8+JXvtujPT3ARsd4sB9Fx/f8A47muhcd8E7plbeLxOz7/ABWqdGxemFnH1mD44W+TgOnH9XX0P/wpDTxnDGxcC2/m2Ld5cDqGUZJFLJj67bUJuHxdGwB5a6NzmBx79gj0SD0g5lyFcVL9io2xBZEMroxNA4ujk8SR5NJAJaeuweh6Xgr4wejcDZnXNgz9LZuQfymAihmuNfjqoeWSytiaWjz99OcO++vXteO0cf8ADdHiSPe8Zsm6zNvTWaWNhno12+VqOPyAl6d+mMktBIJPXfpBRqIiAimPF2N0bK37FPcrO0RyyGNuPiwdOOxJK8k+Qc17gf8A5euu+/atc8V8NxalmtkuZjkmjDhrdepbq2sTBFZEkwJZ1GXfXQ/cj7H2gr3bOLRQ1e1s+q7fhNwxdBzBkP8ADxLHPTDz018kUjWuDCfXkO/f30q5XaWi8o6LlN5oa3ntg3PYbuXlbiBBntepxnws9RuY6SNzZQw+TewSR6B8SQOqWl4w0fNc/VuONVzubZVhsW4cnYv1o/ON1b5HPbAGk+fbYiG99Hsj0gpZF0Pq3DnGm07Bp8+J2HaoNe2wW6lMWa8Bt171dzO2ylp8PjcxziC3sggA/fqN3ML+Hitclpu2Tkd0sL3Rv8MZVIJaSD1+v+yCnEV/cece8E7znpMLhto35lmOpNbJsY+s1vhEwvd7Dz76HpfcHx7wRmtK2XbqW0b8MdrYqfnmyUKwkcbMhjZ4Dy6P6ge+yOh/KCgEV4bpoHD+K4npbvitj3Od2Xdar4uGxSrtBnh6BEvTv0sJI9js/wBlR6AiIgIiICIiAiIgIiICIiDKxL6MeUqSZOGeeg2ZhsxQSBkj4/IeTWuIIa4jsAkHo/sukN+0+huer4fD8XbHpGK46qyG8/8APZj4bcdl7Q2SS62T9Xm0DxAYCOvrvsLmVEHUHJ8ENX8XvFdWvaZbhhZr0cdhgIbK0SMAeAffRHv/AJWu0jZdH1H8Q3Kmf2q1cq5OrazH+DGP3FLK587HRPHiT5ODh4nto7B7+wqRu7ttF3ZcVslrLyyZbEtrto2SxgMIgIMQAA6Pj0PsH+/a1GXyFzL5a5lsjObF27O+xYlIAMkj3FznED17JJ9ILZ4X/wDcPzP/APb8Z/8AtqAbM3Y26trDstl2XMY6tMcVWF5sxqs+Zwe0xgkxdvBPsDv/AI9YOI2PNYnC5fC46++vQzEcceQhDWkTtjd5sBJHY6d79dLUoCIiC7vw8bTjKOj7dqQ3g6FncrLVnp5vp7WvZEX+cDpI/wBUYPl2CP7/AOxsPk7cM5ofDXF2H402kZezlJsow56CmWWrL/zgL44i/tzWOmeQf3f8bD9ejyctzc2jP28NhMPPlJjSwLpXYuNvTTVMsgkeWuADuy8A9knr9ukHYmNl42q/iJ5SyWfygqZenrwilhrzRww3JHVP/XFnY/6ocGjrv78yQ731WDrPH1j8LnIp0HGbBQjbkcV+bGWtRzF5+V3j4eDR0P6u+/7Lne7Zs3bk1y5YlsWZ5HSzTSvLnyPce3OcT7JJJJJWwo7HmqOtZLW6l98WJyckUtysGtIldESYySR2OiT9EIOlsVyHi5fws42DE8fYHYK9Hwx+6VD5wWRDGQ6tN5w+LvBxaCZCSA4ddHvtRLl7LYXM/he0+3r+swa3QbslyNlKK1JY6Iib250kn6nOPfv6H9lXnBrrI3Qx43cf8qZeWs+PG2pehWmnJHUE5PoRvHk3twc3vx7HSte5puS/8ved1rctJ2LVbGoRuylfKWbPdK9aklbGY2tLA0lzHADwe4djv130Q5sREQWf+GjasNqXI01vNZF+IZdxVvH1ssyEyOxs8rPFlgNHv9J7Hr9nH9u1dkWfn0XgneNlwvJFTfNnkylBsuVkryTCm7xcyNzHzd+coYD076b6/hciLa1NizVTWb2tV7748RfnjntVg1vjJJH34OJ67HXZ+ig6PyuTvZXbPw23tnnNrbrNuGzfsyAfNLVfkGflC/8An9AeQT/JUXxFXSX8+cgZLZORr+i5ihslibDXa9N07C/81L8nn4g/Q8R0SAQ499gdKmKmxZyrnMbm4sradkcW6F1GeV/yOg+Igxhvl2OmkDofX9liZfIXMtlrmVyM5sXbs77FiUgAySPcXOd0PXskn0g61kzmQtfjG0LXG4WviNexdmWbENrNj+K8ydj3vugx/oPzEd/p9N68fsFQbQNmyWocOcgZ3RRFDuEOyRx37rYWyT1cW4P6czyB6b8zfFx69eQ79+JFP4nfdvxT8C+hnLETtefK/Ekta41DL/WG+QPo/fR7AJPQHZWmr5bJ1rFyxWyFmvLdjkhtOikLPmjf/Wx3X20/uD6Qdh8fcpYnOcgP1XVYcTbgn1azYz2eZiWVrOVvCqS8nprfFjT0OugSQT2e+zAeE5uK8b+Fne59kvZK3eyFylFlMXVtRRWCyKwHQOgDmn129xcT3/QR6/eg9W2PNavk35LA330bb4JK7pGNa4mORvi9v6gR7BIWpQX9zjNq0/4cOOpNOp5SniDlcn8cWSmZLMHds8iXMAHXf16VAqZN3YW+Kv8AImZoOssoWjcwlqKQRuqySOHzMkHREjHD2PpwcB767ChqAiIgIiICIiAiIgIiICIiAiIgIiICIiAiIgIiICIiAtpe2PYb+Igw97O5S1ja5BgqTW5HwxdDoeLCfEev4CIg1aIiAiIgIiICIiAiIgIiICIiAiIgIiIP/9k="

st.markdown(
    """
<div class="hero-bar">

  <!-- ── Centre: App title & subtitle ──────────────── -->
  <div class="hero-title">
    <div class="brand">&#9889; Alpha<span> Terminal</span></div>
    <div class="brand-sub">Professional Stock Intelligence Platform</div>
  </div>

  <!-- ── Left: Live badge + timestamp ──────────────── -->
  <div style="display:flex;align-items:center;gap:12px;flex-shrink:0;">
    <div class="live-badge"><div class="live-dot"></div> LIVE DATA</div>
    <div style="font-family:IBM Plex Mono,monospace;font-size:.6rem;
                color:#334155;letter-spacing:.04em;">{nw}</div>
  </div>

  <!-- ── Right: Institution logos ───────────────────── -->
  <div class="logo-strip">

    <!-- VGSoM logo -->
    <div class="logo-pill" title="Vinod Gupta School of Management, IIT Kharagpur">
      <img src="{vg}" alt="VGSoM IIT KGP">
    </div>

    <div class="logo-sep"></div>

    <!-- IIT KGP logo -->
    <div class="logo-pill" title="Indian Institute of Technology Kharagpur">
      <img src="{kp}" alt="IIT Kharagpur">
    </div>

    <div style="display:flex;flex-direction:column;gap:2px;margin-left:4px;">
      <div style="font-family:IBM Plex Mono,monospace;font-size:.68rem;
                  font-weight:700;color:#e2e8f0;letter-spacing:.04em;">
        VGSoM
      </div>
      <div style="font-family:Manrope,sans-serif;font-size:.58rem;
                  font-weight:500;color:#475569;letter-spacing:.06em;">
        IIT Kharagpur
      </div>
    </div>

  </div>

</div>
""".format(nw=now_str, vg=VGSOM_B64, kp=IITKGP_B64),
    unsafe_allow_html=True)


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
