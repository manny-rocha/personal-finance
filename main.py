import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import html, dcc

df = pd.read_csv('SOFI_JANtoMAY.csv')

df['Category'] = 'other'

df['Category'] = np.where(df['Description'].str.contains('bluebikes'), 'Transport', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('LTI INFORMATION') | df['Type'].str.contains('Direct Deposit'), 'Income', df['Category'] )
df['Category'] = np.where(df['Amount'] == -1000, 'Rent&Bills', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('Xfinity'), 'Rent&Bills', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('Star Market|Trader Joe\'s|Whole Foods'), 'Groceries', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('Amelias|SUSHI|MARKET|GRUB|Shah|HEMENWAY|BEAN|McDonalds|REST|TST\*\*TST\*|TST\*'), 'Food', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('Amazon.com|AMZN|KLARNA|Klarna|AMAZON|AMAZON.COM.PAYMENTS|Prime Video'), 'Shopping', df['Category'] )
df['Category'] = np.where(df['Type'].str.contains('ATM'), 'Cash Withdrawal', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('hostinger.com|Criterion|Rocket Money'), 'Subscription', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('TEND|CVS'), 'Healthcare', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('VENMO|VENMO*ROCHA'), 'Venmo', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('GSBANK|CapitalOne'), 'Credit Payments', df['Category'] )
df['Category'] = np.where(df['Description'].str.contains('Interest earned'), 'Earned Interest', df['Category'] )

def Net_Worth():
    Net_Worth_Table = df.groupby('Date')['Current balance'].sum().reset_index(name ='Sum')
    Net_Worth_Table['Cumulative Sum'] = Net_Worth_Table['Sum'].cumsum()
    Net_Worth_Chart = go.Figure(
        data = go.Scatter(x = Net_Worth_Table["Date"], y = Net_Worth_Table["Cumulative Sum"]),
        layout = go.Layout(
            title = go.layout.Title(text = "Net Worth Over Time")
        )
    )
    Net_Worth_Chart.update_layout(
        xaxis_title = "Date",
        yaxis_title = "Net Worth ($)",
        hovermode = 'x unified'
        )
    Net_Worth_Chart.update_xaxes(
        tickangle = 45)
    Net_Worth_Chart.show()

def Total_Monthly_Expenses():
    df = df[df['Category'] != 'Income'].copy()
    df.Amount = df.Amount.astype(float)
    Total_Monthly_Expenses_Table = df.groupby('Date')['Amount'].sum().reset_index(name = 'Sum')
    Total_Monthly_Expenses_Chart = px.bar(Total_Monthly_Expenses_Table, x = "Date", y = "Sum", title = "Total Monthly Expenses")
    Total_Monthly_Expenses_Chart.update_yaxes(title = 'Expenses ($)', visible = True, showticklabels = True)
    Total_Monthly_Expenses_Chart.update_xaxes(title = 'Date', visible = True, showticklabels = True)
    Total_Monthly_Expenses_Chart.show()

Expenses_Breakdown_Table = pd.pivot_table(df, values = ['Amount'], index = ['Category', 'Date'], aggfunc=sum).reset_index()
Expenses_Breakdown_Table.columns = [x.upper() for x in Expenses_Breakdown_Table.columns]
Expenses_Breakdown_Chart = px.line(Expenses_Breakdown_Table, x='Date', y="Amount", title="Expenses Breakdown", color = 'Category')
Expenses_Breakdown_Chart.update_yaxes(title='Expenses (£)', visible=True, showticklabels=True)
Expenses_Breakdown_Chart.update_xaxes(title='Date', visible=True, showticklabels=True)
Expenses_Breakdown_Chart.show()