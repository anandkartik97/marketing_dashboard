import pandas as pd
import datetime as dt

def get_month(x):
    return dt.datetime(x.year, x.month, 1)

def get_month_int(dframe, column):
    year = dframe[column].dt.year
    month = dframe[column].dt.month
    day = dframe[column].dt.day
    return year, month, day

def read_and_preprocess_data():
    df = pd.read_csv('./data/online_retail.csv')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d/%m/%Y %H:%M")
    df = df.dropna(subset=['CustomerID'])
    df = df.drop_duplicates()
    df = df[(df['Quantity']>0) & (df['UnitPrice']>0)]
    df['InvoiceMonth'] = df['InvoiceDate'].apply(get_month)
    grouping = df.groupby('CustomerID')['InvoiceMonth']
    df['CohortMonth'] = grouping.transform('min')

    invoice_year,invoice_month,_ = get_month_int(df,'InvoiceMonth')
    cohort_year,cohort_month,_ = get_month_int(df,'CohortMonth')

    year_diff = invoice_year - cohort_year
    month_diff = invoice_month - cohort_month

    df['CohortIndex'] = year_diff * 12 + month_diff + 1

    return df