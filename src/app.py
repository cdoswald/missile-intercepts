"""Dash application for missile intercept model."""

import dash
from dash import dcc, dash_table, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from config import init_data

# Initialize the Dash app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define initial data and columns for the table
init_data = init_data()
columns = [
    {'name': col, 'id': col, 'editable': index >= 3} 
    for index, col in enumerate(init_data[0].keys())
]

app.layout = html.Div([
    html.H1("Simulation Parameters:"),
    dash_table.DataTable(
        id='config-table',
        columns=columns,
        data=init_data,
        editable=True,
        row_deletable=False,
        style_table={'overflowX': 'scroll'},
    ),
    # html.Div(id='output-container')
])

# # Callback to capture changes in the table
# @app.callback(
#     Output('output-container', 'children'),
#     [Input('config-table', 'data')]
# )
# def display_output(data):
#     return html.Div([
#         html.H3('Table Data:'),
#         html.Pre(f'{data}')
#     ])

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
