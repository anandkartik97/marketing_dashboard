import streamlit as st
import datetime as dt
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go

from pre_processing import read_and_preprocess_data

st.set_page_config(
    page_title="RFM Analysis",
    layout="wide"
)

st.write('# What is RFM ?')
st.write('RFM is an acronym of recency, frequency and monetary. '
         'Recency is about when was the last order of a customer. It means the number of days since a customer made the last purchase. \n')

st.write('Frequency is about the number of purchase in a given period. It could be 3 months, 6 months or 1 year. '
         'So we can understand this value as for how often or how many a customer used the product of a company. '
         'The bigger the value is, the more engaged the customers are. ')

st.write('Monetary is the total amount of money a customer spent in that given period.'
         'Therefore big spenders will be differentiated with other customers such as MVP or VIP.')


st.write('# Process of calculating percentiles')
st.write('1. Sort customers based on the metric')
st.write('2. Break customers into a pre-defined number of groups of equal size')
st.write('3. Assign a label to each group')

df = read_and_preprocess_data()
df['TotalSum'] = df['UnitPrice']* df['Quantity']
st.dataframe(df.head())

snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)


st.write('# Calculate RFM metrics')
rfm = df.groupby(['CustomerID']).agg({'InvoiceDate': lambda x : (snapshot_date - x.max()).days,
                                      'InvoiceNo':'count','TotalSum': 'sum'})

rfm.rename(columns={'InvoiceDate':'Recency','InvoiceNo':'Frequency','TotalSum':'MonetaryValue'} ,inplace= True)

st.dataframe(rfm.head())

st.write('We will rate "Recency" customer who have been active more recently better than the less recent customer,because each company wants its customers to be recent')
st.write('We will rate "Frequency" and "Monetary Value" higher label because we want Customer to spend more money and visit more often(that is different order than recency).')


r_labels =range(4,0,-1)
f_labels=range(1,5)
m_labels=range(1,5)
r_quartiles = pd.qcut(rfm['Recency'], q=4, labels = r_labels)
f_quartiles = pd.qcut(rfm['Frequency'],q=4, labels = f_labels)
m_quartiles = pd.qcut(rfm['MonetaryValue'],q=4,labels = m_labels)
rfm = rfm.assign(R=r_quartiles,F=f_quartiles,M=m_quartiles)


def add_rfm(x) : return str(x['R']) + str(x['F']) + str(x['M'])
rfm['RFM_Segment'] = rfm.apply(add_rfm,axis=1 )
rfm['RFM_Score'] = rfm[['R','F','M']].sum(axis=1)

st.write('# Build RFM Segment and RFM Score')
st.write(rfm.head())


st.write('# Use RFM score to group customers')

def segments(df):
    if df['RFM_Score'] > 9 :
        return 'High Value'
    elif (df['RFM_Score'] > 5) and (df['RFM_Score'] <= 9 ):
        return 'Mid Value'
    else:
        return 'Low Value'

rfm['Value Segment'] = rfm.apply(segments,axis=1)

segment_counts = rfm['Value Segment'].value_counts().reset_index()
segment_counts.columns = ['Value Segment', 'Count']
pastel_colors = px.colors.qualitative.Pastel

# Create the bar chart
fig_segment_dist = px.bar(segment_counts,
                          x='Value Segment',
                          y='Count',
                          color='Value Segment',
                          color_discrete_sequence=pastel_colors,
                          title='RFM Value Segment Distribution')

st.plotly_chart(fig_segment_dist)

rfm['RFM Customer Segments'] = ''


rfm.loc[rfm['RFM_Score'] >= 9, 'RFM Customer Segments'] = 'Champions'
rfm.loc[(rfm['RFM_Score'] >= 6) & (rfm['RFM_Score'] < 9), 'RFM Customer Segments'] = 'Potential Loyalists'
rfm.loc[(rfm['RFM_Score'] >= 5) & (rfm['RFM_Score'] < 6), 'RFM Customer Segments'] = 'At Risk Customers'
rfm.loc[(rfm['RFM_Score'] >= 4) & (rfm['RFM_Score'] < 5), 'RFM Customer Segments'] = "Can't Lose"
rfm.loc[(rfm['RFM_Score'] >= 3) & (rfm['RFM_Score'] < 4), 'RFM Customer Segments'] = "Lost"

segment_product_counts = rfm.groupby(['Value Segment', 'RFM Customer Segments']).size().reset_index(name='Count')

segment_product_counts = segment_product_counts.sort_values('Count', ascending=False)

fig_treemap_segment_product = px.treemap(segment_product_counts,
                                         path=['Value Segment', 'RFM Customer Segments'],
                                         values='Count',
                                         color='Value Segment', color_discrete_sequence=px.colors.qualitative.Pastel,
                                         title='RFM Customer Segments by Value')

st.plotly_chart(fig_treemap_segment_product)


segment_counts = rfm['RFM Customer Segments'].value_counts()

# Create a bar chart to compare segment counts
fig = go.Figure(data=[go.Bar(x=segment_counts.index, y=segment_counts.values,
                            marker=dict(color=pastel_colors))])

# Set the color of the Champions segment as a different color
champions_color = 'rgb(158, 202, 225)'
fig.update_traces(marker_color=[champions_color if segment == 'Champions' else pastel_colors[i]
                                for i, segment in enumerate(segment_counts.index)],
                  marker_line_color='rgb(8, 48, 107)',
                  marker_line_width=1.5)

# Update the layout
fig.update_layout(title='Comparison of RFM Segments',
                  xaxis_title='RFM Segments',
                  yaxis_title='Number of Customers',
                  showlegend=False)

st.plotly_chart(fig)




# # Calculate the average Recency, Frequency, and Monetary scores for each segment
# segment_scores = rfm.groupby(['RFM Customer Segments'])['Recency', 'Frequency', 'MonetaryValue'].mean().reset_index()
#
# # Create a grouped bar chart to compare segment scores
# fig = go.Figure()
#
# # Add bars for Recency score
# fig.add_trace(go.Bar(
#     x=segment_scores['RFM Customer Segments'],
#     y=segment_scores['Recency'],
#     name='Recency Score',
#     marker_color='rgb(158,202,225)'
# ))
#
# # Add bars for Frequency score
# fig.add_trace(go.Bar(
#     x=segment_scores['RFM Customer Segments'],
#     y=segment_scores['Frequency'],
#     name='Frequency Score',
#     marker_color='rgb(94,158,217)'
# ))
#
# # Add bars for Monetary score
# fig.add_trace(go.Bar(
#     x=segment_scores['RFM Customer Segments'],
#     y=segment_scores['MonetaryValue'],
#     name='Monetary Score',
#     marker_color='rgb(32,102,148)'
# ))
#
# # Update the layout
# fig.update_layout(
#     title='Comparison of RFM Segments based on Recency, Frequency, and Monetary Scores',
#     xaxis_title='RFM Segments',
#     yaxis_title='Score',
#     barmode='group',
#     showlegend=True
# )
#
# st.plotly_chart(fig)