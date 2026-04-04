import joblib
import os
from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import warnings
from utils import get_stock_data
MODEL_PATH = "lstm_model.pkl"


def prediction(stock, n_days, df=None):
    warnings.filterwarnings('ignore')

    if df is None:
        df = get_stock_data(stock)

    if df.empty:
        raise ValueError("No data found")

    data = df['Close'].values.reshape(-1, 1)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    lookback = 10
    X, y = [], []

    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    #  Load or train model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            tf.keras.layers.LSTM(50),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        model.fit(X, y, epochs=10, batch_size=16, verbose=0)

        joblib.dump(model, MODEL_PATH)

    # prediction
    last_sequence = scaled_data[-lookback:, 0]
    predictions = []

    for _ in range(n_days - 1):
        pred = model.predict(last_sequence.reshape(1, lookback, 1), verbose=0)
        predictions.append(pred[0, 0])
        last_sequence = np.append(last_sequence[1:], pred[0, 0])

    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

    dates = [date.today() + timedelta(days=i) for i in range(1, n_days)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=predictions.flatten(), mode='lines+markers'))
    fig.update_layout(template="plotly_dark",title_x=0.5,hovermode="x unified")

    return fig