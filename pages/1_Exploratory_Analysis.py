import pandas as pd
import plotly_express as px
import streamlit as st

df = pd.read_csv('./data/online_retail.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d/%m/%Y %H:%M")

st.set_page_config(
    page_title="EDA",
    layout="wide"
)

st.write('# About the dataset')
st.write(' The dataset pertains to a UK-based online retail company that sells unique all-occasion gifts. It contains transactional data spanning from December 1, 2010, to December 9, 2011.')

st.write('# Objective')
st.write(' - Gain insights and perform exploratory analysis')
st.write(' - Uncover valuable patterns and trends to guide business decisions and strategies')

st.write('# Top 10 rows')
st.write(df.head(10))

df = df.drop_duplicates()
st.write('# Missing values composition')

for col in df.columns:
    pct_missing = df[col].isnull().mean()
    st.write(f'{col} - {pct_missing :.1%}')


df['Description'] = df['Description'].fillna('Unknown')
df['CustomerID']  = df['CustomerID'].fillna(0)
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['CustomerID'] = df['CustomerID'].astype('int64')
df  = df[df['UnitPrice'] > 0]
df['Checkout_Price'] = df['Quantity'] * df ['UnitPrice']
df['Year'] = df['InvoiceDate'].dt.year
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
df['YearMonth'] = df['YearMonth'].astype(str)
canceled = df[df['InvoiceNo'].str.contains('C')]
df = df[~df['InvoiceNo'].str.contains('C' ,na = False)]
df.loc[df['CustomerID'] == 0 , 'CustomerType'] = 'Normal'
df.loc[df['CustomerID'] > 0 , 'CustomerType'] = 'Member'

st.write('# Which Products have been sold by Highest Quantity ?')
product_quantity= df.groupby('Description').agg({'Quantity' : 'sum'}).sort_values(by = 'Quantity' , ascending = False).reset_index(drop= False).head(5)
fig = px.bar(product_quantity, y = 'Description' , x= 'Quantity', color='Quantity')
st.plotly_chart(fig)

st.write('# Which product has achieved the highest sales?')
product_sales= df.groupby('Description').agg({'Checkout_Price' : 'sum'}).sort_values(by = 'Checkout_Price' , ascending = False).reset_index(drop= False).head(5)
fig = px.bar(product_sales, x = 'Checkout_Price', y = 'Description', color = 'Checkout_Price')
st.plotly_chart(fig)


st.write('# In which Country do we have more customers?')
country = df['Country'].value_counts().reset_index(drop = False)
country.columns = ["Country","Counts"]
fig = px.bar(country, x='Country', y='Counts')
st.plotly_chart(fig)

st.write('#  In which month have we gained the highest sales?')
month_sales = df.groupby('YearMonth')['Checkout_Price'].sum().reset_index(drop = False)
fig = px.line(month_sales, x = 'YearMonth', y = 'Checkout_Price')
st.plotly_chart(fig)