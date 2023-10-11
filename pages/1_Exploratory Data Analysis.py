import pandas as pd
import streamlit as st

df = pd.read_csv('./data/online_retail.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d/%m/%Y %H:%M")

st.set_page_config(
    page_title="EDA",
    layout="wide"
)

st.write('# Top 10 rows')
st.write(df.head(10))

st.write('# Check Null Records')
st.write(df.isnull().sum())

df= df.dropna(subset=['CustomerID'])

st.write('# Check & Clean Duplicate Data')
st.write('Duplicate record count before cleaning: ', df.duplicated().sum())

df = df.drop_duplicates()
st.write('Duplicate record count after cleaning: ', df.duplicated().sum())

st.write('# Checking Statistics')
st.write(df.describe())

st.write('# Cleaning data (Minimum UnitPrice > 0, Minimum Qty > 0)')
df=df[(df['Quantity']>0) & (df['UnitPrice']>0)]
st.write(df.describe())

st.write('# Checking shape of the dataset')
st.write('Row count', df.shape[0])
st.write('Column count', df.shape[1])