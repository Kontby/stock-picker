import datetime
import requests
import pathlib
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import colorlover as cl
import dash_table
import news



from dash.dependencies import Input, Output, State
from plotly import tools

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/dash-stock-ticker-demo.csv')
colorscale = cl.scales['9']['qual']['Paired']

df2 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv').iloc[:,:3]

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{'name':'viewport',
                            'content':'width=device-width'}])

app.title = "Stock Picking Helper"

server = app.server

#Style Components
text_style = {
    'textAlign':'center',
    'color':'#0074D9'
}
page = {
    'margin-left':'5%',
    'margin-right':'5%',
    'top':0,
    'padding':'20px 10px',
    'width':'40%'
}
panel = {
    'width':'25%',
    'padding':'20px 10px',
    'background-color':'#f8f9fa'
}

#Charts
first_graph = html.Div(
                    className="row",
                    children=[dcc.Graph()]
                )
second_graph = first_graph

# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Left Panel
        html.Div(
            className="three columns",
            children=[
                html.H6(className="title-header",children="Potentially undervalued", style=text_style),
                dcc.Markdown("This app does bla bla bla", style=text_style),
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df2.columns],
                    data=df2.to_dict('records'),
                    style_cell={'textAlign': 'center',
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'fontSize':14,
                                'font-family':'sans-serif'},
                    style_as_list_view=True,
                    style_header={
                            'backgroundColor': 'grey',
                            'fontWeight': 'bold'
                        }
                ),
                html.Hr(),
                html.H6(className="title-header", children="Potentially overvalued", style=text_style),
                dcc.Markdown("This app does bla bla bla", style=text_style),
                dash_table.DataTable(
                    id='table2',
                    columns=[{"name": i, "id": i} for i in df2.columns],
                    data=df2.to_dict('records'),
                    style_cell={'textAlign': 'center',
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'fontSize': 14,
                                'font-family': 'sans-serif'},
                    style_as_list_view=True,
                    style_header={
                        'backgroundColor': 'grey',
                        'fontWeight': 'bold'
                    }
                )
            ],
            style=panel
        ),
        # Middle Panel Div
        html.Div(
            className='six columns',
            children=[
                html.H2("Test", style=text_style),
                html.Hr(),
                dcc.Dropdown(
                        id='stock-ticker-input',
                        options=[{'label': s[0], 'value': str(s[1])}
                                 for s in zip(df.Stock.unique(), df.Stock.unique())],
                        value=['YHOO', 'GOOGL'],
                        multi=True
                    ),
                html.Br(),
                html.Div(id='graphs')
            ],
            style=page
        ),
        # Right Panel
        dbc.Col(
            className="three columns",
            children=[
                html.H6(className="title-header", children="News", style=text_style),
                dcc.Markdown("This app does bla bla bla", style=text_style),
                dcc.Dropdown(
                    id='news-input',
                    options=[{'label': s[0], 'value': str(s[1])}
                             for s in zip(df.Stock.unique(), df.Stock.unique())],
                    value=['TSLA'],
                    multi=False
                ),
                html.Br(),
                html.Div(id='news')
            ],
            style=panel
        )
    ]
)

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        for i, ticker in enumerate(tickers):

            dff = df[df['Stock'] == ticker]

            candlestick = {
                'x': dff['Date'],
                'open': dff['Open'],
                'high': dff['High'],
                'low': dff['Low'],
                'close': dff['Close'],
                'type': 'candlestick',
                'name': ticker,
                'legendgroup': ticker,
                'increasing': {'line': {'color': colorscale[0]}},
                'decreasing': {'line': {'color': colorscale[1]}}
            }
            bb_bands = bbands(dff.Close)
            bollinger_traces = [{
                'x': dff['Date'], 'y': y,
                'type': 'scatter', 'mode': 'lines',
                'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
                'hoverinfo': 'none',
                'legendgroup': ticker,
                'showlegend': True if i == 0 else False,
                'name': '{} - bollinger bands'.format(ticker)
            } for i, y in enumerate(bb_bands)]
            graphs.append(dcc.Graph(
                id=ticker,
                figure={
                    'data': [candlestick] + bollinger_traces,
                    'layout': {
                        'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                        'legend': {'x': 0}
                    }
                }
            ))

    return graphs

@app.callback(
    dash.dependencies.Output('news','children'),
    [dash.dependencies.Input('news-input', 'value')])
def update_news(ticker):
    news_table = []
    if not ticker:
        news_table.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        news_df = pd.DataFrame(news.get_news(ticker),columns=['News'])
        news_table.append(dash_table.DataTable(
            id='news-table',
            columns=[{"name": i, "id": i} for i in news_df.columns],
            data=news_df.to_dict('records'),
            style_cell={'textAlign': 'center',
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                        'fontSize': 14,
                        'font-family': 'sans-serif',
                        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                        'whiteSpace': 'normal'
                        },
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'grey',
                'fontWeight': 'bold'
            },
            style_data={'height':'auto'},
            style_table={'overflowX': 'auto'}
        ))
    return news_table



if __name__ == "__main__":
    app.run_server(debug=True)