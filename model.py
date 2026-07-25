import os
from datetime import date, timedelta
import numpy as np
import plotly.graph_objs as go
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import warnings
from utils import get_stock_data

MODEL_PATH = "lstm_model.h5"
TFLITE_MODEL_PATH = "lstm_model_float16.tflite"


def build_lstm_model(lookback, unroll=False):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(
            50,
            return_sequences=True,
            input_shape=(lookback, 1),
            unroll=unroll,
        ),
        tf.keras.layers.LSTM(50, unroll=unroll),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def tflite_uses_select_tf_ops(model_path=TFLITE_MODEL_PATH):
    if not os.path.exists(model_path):
        return False

    with open(model_path, "rb") as file:
        return b"Flex" in file.read()


def convert_to_float16_tflite(model, lookback, output_path=TFLITE_MODEL_PATH):
    # Unrolled LSTMs convert to built-in TFLite ops and avoid FlexTensorList ops.
    tflite_ready_model = build_lstm_model(lookback, unroll=True)
    tflite_ready_model.set_weights(model.get_weights())

    converter = tf.lite.TFLiteConverter.from_keras_model(tflite_ready_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]

    tflite_model = converter.convert()

    with open(output_path, "wb") as file:
        file.write(tflite_model)


def ensure_model_artifacts(X, y, lookback):
    if os.path.exists(TFLITE_MODEL_PATH) and not tflite_uses_select_tf_ops():
        return None

    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        model.compile(optimizer='adam', loss='mean_squared_error')
    else:
        model = build_lstm_model(lookback)
        model.fit(X, y, epochs=10, batch_size=16, verbose=0)
        model.save(MODEL_PATH)

    convert_to_float16_tflite(model, lookback)
    return model


def create_tflite_predictor(model_path=TFLITE_MODEL_PATH):
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_index = input_details[0]["index"]
    output_index = output_details[0]["index"]
    input_dtype = input_details[0]["dtype"]

    def predict(input_sequence):
        interpreter.set_tensor(input_index, input_sequence.astype(input_dtype))
        interpreter.invoke()
        return interpreter.get_tensor(output_index)

    return predict


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

    # Create or replace the compact float16 TFLite model when needed.
    model = ensure_model_artifacts(X, y, lookback)
    tflite_predict = create_tflite_predictor() if os.path.exists(TFLITE_MODEL_PATH) else None

    # prediction
    last_sequence = scaled_data[-lookback:, 0]
    predictions = []

    for _ in range(n_days - 1):
        model_input = last_sequence.reshape(1, lookback, 1).astype(np.float32)
        if tflite_predict is not None:
            pred = tflite_predict(model_input)
        else:
            pred = model.predict(model_input, verbose=0)
        predictions.append(pred[0, 0])
        last_sequence = np.append(last_sequence[1:], pred[0, 0])

    predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

    dates = [date.today() + timedelta(days=i) for i in range(1, n_days)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=predictions.flatten(), mode='lines+markers'))
    fig.update_layout(template="plotly_dark", title_x=0.5, hovermode="x unified")

    return fig
