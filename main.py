import os
import dotenv
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import html, dcc, dash_table
import dash as dash
import dash_bootstrap_components as dbc

dotenv.load_dotenv()

df = pd.read_csv('SOFI_JANtoMAY.csv')

df['Amount'] = df['Amount'].apply(lambda x: round(x, 2))

df['Category'] = 'other'

df['Category'] = np.where(df['Description'].str.contains(
    'bluebikes'), 'Transport', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    os.environ.get('EMPLOYER')) | df['Type'].str.contains('Direct Deposit'), 'Income', df['Category'])
df['Category'] = np.where(df['Amount'] == -1000, 'Rent&Bills', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'Xfinity'), 'Rent&Bills', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'Star Market|Trader Joe\'s|Whole Foods'), 'Groceries', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'Amelias|SUSHI|MARKET|GRUB|Shah|HEMENWAY|BEAN|McDonalds|REST|TST\*\*TST\*|TST\*'), 'Food', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'Amazon.com|AMZN|KLARNA|Klarna|AMAZON|AMAZON.COM.PAYMENTS|Prime Video'), 'Shopping', df['Category'])
df['Category'] = np.where(df['Type'].str.contains(
    'ATM'), 'Cash Withdrawal', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'hostinger.com|Criterion|Rocket Money'), 'Subscription', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'TEND|CVS'), 'Healthcare', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'VENMO|VENMO*ROCHA'), 'Venmo', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'GSBANK|CapitalOne'), 'Credit I/O', df['Category'])
df['Category'] = np.where(df['Description'].str.contains(
    'Interest earned'), 'Earned Interest', df['Category'])


# * Net Worth Over Time
Net_Worth_Table = df.groupby(
    'Date')['Amount'].sum().reset_index(name='Sum')
Net_Worth_Table['Cumulative Sum'] = Net_Worth_Table['Sum'].cumsum()
last_expenses = df.groupby(['Date', 'Category']).tail(
    1)  # get the last expenses for each category by date
# select relevant columns
last_expenses = last_expenses[['Date', 'Category', 'Amount']]
last_expenses = last_expenses.sort_values('Date')  # sort by date

tooltip_data = []
for index, row in last_expenses.iterrows():
    tooltip_data.append(
        f"Category: {row['Category']}<br>Cumulative Sum: ${row['Amount']:,.2f}")

Net_Worth_Chart = go.Figure(
    data=go.Scatter(x=Net_Worth_Table["Date"],
                    y=Net_Worth_Table["Cumulative Sum"],
                    mode='lines+markers',
                    hovertemplate='%{x}<br>%{y:$,.2f}<br>%{text}',
                    text=tooltip_data),
    layout=go.Layout(
        title=go.layout.Title(text="Net Worth Over Time")
    )
)


# * Total Monthly Expenses
df = df[df['Category'] != 'Income'].copy()
df.Amount = df.Amount.round(2)

Total_Monthly_Expenses_Table = df.groupby(
    'Date')['Amount'].sum().round(2).reset_index(name='Sum')


Total_Monthly_Expenses_Chart = px.bar(
    Total_Monthly_Expenses_Table,
    x="Date",
    y="Sum",
    title="Total Monthly Expenses",
)

Total_Monthly_Expenses_Chart.update_yaxes(
    title='Expenses ($)',
    visible=True,
    showticklabels=True
)

Total_Monthly_Expenses_Chart.update_xaxes(
    title='Date',
    visible=True,
    showticklabels=True
)


# * Expenses Breakdown by Category
df.Amount = df.Amount.round(2)
Expenses_Breakdown_Table = pd.pivot_table(df, values=['Amount'], index=[
                                          'Category', 'Date'], aggfunc=sum).round(2).reset_index()

Expenses_Breakdown_Table = Expenses_Breakdown_Table.sort_values(
    by=['Category', 'Date'], ascending=[True, False])

Expenses_Breakdown_Chart = px.line(
    Expenses_Breakdown_Table, x='Date', y="Amount", title="Expenses Breakdown", color='Category')

Expenses_Breakdown_Chart.update_yaxes(
    title='Expenses ($)', visible=True, showticklabels=True)

Expenses_Breakdown_Chart.update_xaxes(
    title='Date', visible=True, showticklabels=True)


# * Jupyter Dash App
app = JupyterDash(__name__)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1(f"Personal Finance Summary: Jan 2023 - {datetime.now().strftime('%b %Y')}", style={
                'font-family': 'Arial, Helvetica, sans-serif'}),
                width={'size': 12, 'offset': 0, 'order': 1}),
        html.H3(f"Net Worth: ${Net_Worth_Table['Cumulative Sum'].iloc[-1]:,.2f}", style={
                'font-family': 'Arial, Helvetica, sans-serif'}),
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure=Net_Worth_Chart)],
                width={'size': 6, 'offset': 0, 'order': 1}),
        dbc.Col([dcc.Graph(figure=Total_Monthly_Expenses_Chart),
                 dbc.Row(dbc.Col(dash_table.DataTable(Total_Monthly_Expenses_Table.to_dict('records'),
                                                      style_table={'maxHeight': '300px', 'overflowY': 'scroll'}),
                                 width={'size': 12})),
                 ],
                width={'size': 6, 'offset': 0, 'order': 2}),
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(figure=Expenses_Breakdown_Chart),
                 dbc.Row(dbc.Col(dash_table.DataTable(Expenses_Breakdown_Table.to_dict('records'),
                                                      style_table={'maxHeight': '300px', 'overflowY': 'scroll'}),
                                 width={'size': 12})),
                 ],
                width={'size': 12, 'offset': 0, 'order': 1})
    ])
])


@app.callback(
    dash.dependencies.Output("collapse", "is_open"),
    [dash.dependencies.Input("collapse-button", "n_clicks")],
    [dash.dependencies.State("collapse", "is_open")],
)
def toggle_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Run app and display result
app.run_server(mode='external')
