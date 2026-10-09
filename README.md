# Stock Price Prediction Using LSTM

A machine learning web application that uses Long Short-Term Memory (LSTM) neural networks to analyze historical stock market data and generate stock price predictions.

## Overview

This project explores the application of deep learning to time-series forecasting. It combines an LSTM-based prediction model with a Python web application to present stock price information and predicted trends.

The project was developed to understand time-series data processing, neural network models, and the integration of machine learning into a web application.

<img width="1848" height="894" alt="image" src="https://github.com/user-attachments/assets/9debaef6-6dfc-42c4-ad99-2ea0b2acf1fe" />

<img width="1755" height="499" alt="image" src="https://github.com/user-attachments/assets/8de84536-8e0d-414c-913f-3da1022f26d4" />

<img width="1746" height="485" alt="image" src="https://github.com/user-attachments/assets/49523418-af0e-4dc1-bef6-f624b1669088" />

## Features

- **LSTM-based forecasting:** Uses a recurrent neural network architecture designed for sequential data.
- **Stock price visualization:** Presents stock market information and prediction results through the web interface.
- **Model integration:** Uses a saved machine learning model for prediction.
- **Web application:** Provides an interface for interacting with the prediction functionality.
- **Deployment support:** Includes configuration files for running the application in a hosted environment.

## Tech Stack

- **Programming Language:** Python
- **Machine Learning:** TensorFlow / Keras, LSTM
- **Data Processing:** NumPy, Pandas
- **Web Application:** Python web framework used in the project
- **Model Deployment:** TensorFlow Lite
- **Version Control:** Git and GitHub

## Project Structure

```text
Stock-Price-Prediction/
├── assets/                   # Application assets
├── app.py                    # Main application
├── model.py                  # Model-related logic
├── utils.py                  # Helper functions
├── lstm_model.h5             # Saved LSTM model
├── lstm_model_float16.tflite # Optimized TensorFlow Lite model
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python runtime configuration
├── Procfile                  # Deployment configuration
└── README.md                 # Project documentation
```

## How It Works

1. **Data preparation:** Historical stock price data is prepared for time-series analysis.
2. **Preprocessing:** Input data is transformed into the format required by the trained model.
3. **Prediction:** The LSTM model processes sequential data to generate price predictions.
4. **Visualization:** The application presents the available stock information and prediction results.

## Installation and Setup

### Prerequisites

- Python version compatible with the project dependencies
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/AjayKumar366/Stock-Price-Prediction.git
cd Stock-Price-Prediction
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Follow the application output to determine how to access the locally running web application.

## Model Details

The project uses an LSTM (Long Short-Term Memory) neural network, a type of recurrent neural network commonly applied to sequential data and time-series forecasting.

The repository also includes a TensorFlow Lite model in float16 format, providing an alternative model representation for supported inference workflows.

## Limitations

- Stock prices are affected by market conditions, economic events, and other unpredictable factors.
- Historical patterns do not guarantee future price movements.
- Prediction quality depends on the training data, preprocessing, and model configuration.
- Model predictions should not be treated as financial advice.

## Future Improvements

- Add quantitative evaluation using MAE, RMSE, and other appropriate forecasting metrics.
- Compare LSTM predictions with baseline forecasting models.
- Improve error handling and data validation.
- Add interactive historical-versus-predicted price charts.
- Expand automated testing and deployment documentation.

## Disclaimer

This project is intended for educational and experimental purposes. It does not provide financial advice or guarantee future stock market performance.

## Author

**Ajay Kumar Kosuru**

GitHub: [AjayKumar366](https://github.com/AjayKumar366)
