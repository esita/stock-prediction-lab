from time import strftime
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.tsa.arima.model import  ARIMA
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pandas as pd

# ---------------- Fetch Data ----------------
def get_data(ticker):
    stock_data = yf.download(ticker, start= '2025-01-01')
    return stock_data[['Close']]
# ---------------- Stationarity Test ----------------
def stationary_check(close_price):
    adf_test = adfuller(close_price)
    p_value = round(adf_test[1],3)
    return p_value
# ---------------- Rolling Mean ----------------
def get_rolling_mean(close_price):
    rolling_price = close_price.rolling(window=7).mean().dropna()
    return rolling_price
# ---------------- Differencing Order ----------------
def get_differencing_order(close_price):
    p_value = stationary_check(close_price['Close'])
    d = 0
    temp_series = close_price['Close'].copy()
    while True:
        if p_value > 0.05:
            d += 1
            #close_price = close_price.diff().dropna()    
            #p_value =  stationary_check(close_price)
            temp_series = temp_series.diff().dropna()
            p_value = stationary_check(temp_series)
        else:
            break
    return d
# ---------------- Fit ARIMA ----------------
def fit_model(data, d):
    #model = ARIMA(data, order=(5,differencing_order,5))
    #model_fit = model.fit()

    #forecast_steps = 30
    #forecast = model_fit.get_forecast(steps=forecast_steps)

    #predictions = forecast.predicted_mean
    #return predictions

    model = ARIMA(data, order=(5, d, 5))
    model_fit = model.fit()

    forecast = model_fit.get_forecast(steps=30)
    return forecast.predicted_mean
# ---------------- Evaluate Model ----------------    
def evaluate_model(price_df, d):
    #train_data, test_data = original_price[:-30], original_price[-30:]
    #predictions = fit_model(train_data,differencing_order)
    #rmse = np.sqrt(mean_squared_error(test_data, predictions))    
    #return round(rmse,2)
    series = price_df['Close']

    train, test = series[:-30], series[-30:]
    predictions = fit_model(train, d)

    rmse = np.sqrt(mean_squared_error(test, predictions))
    return round(rmse, 2)

def scaling(close_price):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(np.array(close_price).reshape(-1,1))
    return scaled_data,scaler
# ---------------- Forecast ----------------
def get_forecast(price_df, d):
    series = price_df['Close']

    predictions = fit_model(series, d)

    last_date = price_df.index[-1]
    forecast_index = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=30,
        freq='D'
    )

    forecast_df = pd.DataFrame(
        predictions.values,
        index=forecast_index,
        columns=['Close']
    )

    return forecast_df

    
def inverse_scaling(scaler,scaled_data):
    close_price = scaler.inverse_transform(np.array(scaled_data).reshape(-1,1))
    return close_price
