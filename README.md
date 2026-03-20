# 📈 Stock Prediction Lab

A professional multi-model stock forecasting dashboard built with Streamlit.
Compares 8 prediction algorithms from classical statistics to modern deep learning.

---

## 🚀 Quick Start

### 1. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note on TensorFlow:** If you don't have a GPU, use `tensorflow-cpu` instead:
> ```bash
> pip install tensorflow-cpu
> ```

> **Note on Prophet:** If installation fails, try:
> ```bash
> pip install pystan==2.19.1.1
> pip install prophet
> ```

### 3. Run the app
```bash
streamlit run stock_prediction_app.py
```

---

## 📦 Models Included

| # | Model | Era | Notes |
|---|-------|-----|-------|
| 1 | Simple Moving Average (SMA-20) | 1950s | Baseline classical |
| 2 | Linear Regression | 1960s | With 14 technical features |
| 3 | ARIMA (5,1,2) | 1970s | Walk-forward validation |
| 4 | Random Forest (200 trees) | 2001 | Non-linear ensemble |
| 5 | XGBoost | 2014 | Gradient boosted trees |
| 6 | Bidirectional LSTM | 2010s | Deep learning (requires TF) |
| 7 | Facebook Prophet | 2017 | Seasonality-aware (requires prophet) |
| 8 | Weighted Ensemble | 2020s | 1/RMSE weighted blend |

---

## 🎛 Features

- **Left sidebar:** Stock selector (12 assets), analysis period pickers
- **Top right panel:** Best model name, RMSE score, tomorrow's forecast
- **15-day table:** Predicted close, daily change ($), daily change (%), trend direction
- **RMSE bar chart:** Compare all models at a glance
- **Model tabs:** Deep-dive into each algorithm — chart, metrics, forecast table
- **Confidence bands:** Shaded uncertainty region on forecasts
- **Dark theme:** Fully styled, professional dark dashboard

---

## 📁 File Structure

```
stock_prediction_app.py    ← Main Streamlit application
requirements.txt           ← Python dependencies
README.md                  ← This file
```

---

## 💡 Tips

- Set a **2-year date range** for best LSTM results (needs enough training data)
- All model results are **cached** — re-running the same ticker/dates is instant
- LSTM training takes ~30–60 seconds on first run (cached after)
- The **Ensemble** tab usually has the lowest RMSE

---

## ⚠️ Disclaimer

For educational purposes only. Not financial advice. Past performance does not guarantee future results.
