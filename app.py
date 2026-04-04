import dash
from dash import html
from dash import dcc
from datetime import datetime as dt
import requests
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import dash_bootstrap_components as dbc
# model
from model import prediction
from utils import get_company_info, get_stock_data

cached_data = {}

def get_stock_price_fig(df):
    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Opening Price"
                  )
    fig.update_layout(
        template="plotly_dark",
        title_font_size=22,
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Price",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.line(
        df,
        x="Date",
        y=["Close", "EWA_20"],
        title="EMA Indicator"
    )

    fig.update_layout(
        template="plotly_dark",
        title_font_size=22,
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified"
    )
    return fig


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
    ])
app.title = 'Stock price prediction'
server = app.server

spinners = html.Div([
    dbc.Spinner(color='primary')
])

# html layout of site
app.layout = html.Div([

    html.Div([html.H1("Stock Price Prediction Site", className="start")],style={"textAlign": "center", "marginTop": "50px"}),
    html.Div([
    html.Div(
    [
        html.Div([
            # Search
            html.Div([
                dcc.Input(
                    id="dropdown_tickers",
                    type="search",
                    placeholder="Search stock (e.g., AAPL, TCS, INFY)",
                    debounce=True,
                    className="search-bar"
                )
            ]),

            html.Div([
                dcc.DatePickerSingle(
                    id='start-date',
                    date=dt.now().date(),
                    display_format='YYYY-MM-DD',
                    className="date-single"
                ),

                html.Span("→", className="date-arrow"),

                dcc.DatePickerSingle(
                    id='end-date',
                    date=dt.now().date(),
                    display_format='YYYY-MM-DD',
                    className="date-single"
                ),
            ], className="date-container"),

            #  Days Input
            html.Div([
                dcc.Input(
                    id="n_days",
                    type="number",
                    placeholder="Days",
                    className="days-input"
                )
            ]),

             # Buttons
            html.Div([
                html.Button("Submit", id='submit', className="btn"),
                html.Button("Stock", id="stock", className="btn"),
                html.Button("Indicators", id="indicators", className="btn"),
                html.Button("Forecast", id="forecast", className="btn"),
                ], className="button-group"),
        ],className="toolbar"), 

        # content
        html.Div(
            [
                html.Div(
                    [  # header
                        html.Img(id="logo"),
                        html.P(id="ticker")
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
            ],
            className="content"),
    ],
    className="container"),
    html.Div([
            html.Div([], id="graphs-content"),
            html.Div([], id="main-content"),
            html.Div([], id="forecast-content")
            ], className="graphs")
    ]),
])


# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])

def update_data(n, val):
    if n is None:
        return (
            "Enter a stock code (e.g., TCS.BSE)",
            None,
            None,
            None, None, None
        )

    if not val:
        raise PreventUpdate

    # Validate using stock data (reliable)
    global cached_data

    if val not in cached_data:
        df = get_stock_data(val)
        cached_data[val] = df
    else:
        df = cached_data[val]

    # Try to get company info (optional)
    try:
        info = get_company_info(val)
        description = info.get("finnhubIndustry", "No description available")
        name = info.get("name", val)
    except:
        description = "Company info not available"
        name = val

    return (
        description,
        None,
        name,
        None, None, None
    )


# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('start-date', 'date'),
    Input('end-date', 'date')
], [State("dropdown_tickers", "value")])

def stock_price(n, start_date, end_date, val):
    if n is None or val is None:
        return [""]

    global cached_data

    df = cached_data.get(val)

    if df is None:
        df = get_stock_data(val)
        cached_data[val] = df

    # Prevent crash if API limit is reached or invalid stock
    if df.empty or "Date" not in df.columns:
        return [html.Div("API limit reached or invalid stock. Try again.")]

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

    if df.empty:
        return [html.Div(" No data in selected range")]

    fig = get_stock_price_fig(df)
    return [dcc.Loading(children=[dcc.Graph(figure=fig)],type="circle")]


# callback for indicators
@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('start-date', 'date'),
    Input('end-date', 'date')
], [State("dropdown_tickers", "value")])

def indicators(n, start_date, end_date, val):
    if n is None or val is None:
        return [""]

    """if not any(x in val for x in [".NS", ".BO"]) and val.isalpha():
        val = val + ".NS"""

    global cached_data

    df_more = cached_data.get(val)

    if df_more is None:
        df_more = get_stock_data(val)
        cached_data[val] = df_more

    if df_more.empty or "Date" not in df_more.columns:
        return [html.Div(" API limit or invalid stock")]

    df_more["Date"] = pd.to_datetime(df_more["Date"])

    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        df_more = df_more[
            (df_more["Date"] >= start_date) &
            (df_more["Date"] <= end_date)
        ]

    if df_more.empty:
        return [html.Div(" No data in selected range")]

    fig = get_more(df_more)

    return [dcc.Graph(
        figure=fig,
        config={
            'scrollZoom': True,
            'doubleClick': 'autosize'
        }
    )]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])

def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    if n_days == None:
        raise PreventUpdate
    try:
        df = cached_data.get(val)
        fig = prediction(val, int(n_days) + 1, df)
    except Exception as e:
        return [html.Div(f"Error: {str(e)}")]
    return [dcc.Graph(figure=fig, 
    config={
        'doubleClick': 'autosize'
    })]

if __name__ == '__main__':
    app.run(debug=True)
