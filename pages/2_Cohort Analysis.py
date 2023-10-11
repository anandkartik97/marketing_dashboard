import pandas as pd
import plotly_express as px
import streamlit as st

from pre_processing import read_and_preprocess_data

st.set_page_config(
    page_title="Cohort Analysis",
    layout="wide"
)

st.markdown("<h1 style='text-align: center;'>What is Cohort Analysis ?</h1>", unsafe_allow_html=True)
st.write('- A Cohort Analysis breaks the data up in related groups rather than looking at all the customers as one unit within a defined time-span.')
st.write('- A Cohort Analysis is needed when calculating Customer Churn since it takes into account the natural customer lifecycle. In other words, a person that is your customer for 3 years behaves differently than a person that is a customer since 1 month.')

st.write('For cohort analysis, there are a few labels that we have to create:')
st.write('- Invoice period: A string representation of the year and month of a single transaction/invoice.')
st.write('- Cohort group: A string representation of the the year and month of a customer’s first purchase. This label is common across all invoices for a particular customer.')
st.write('- Cohort period / Cohort Index: A integer representation a customer’s stage in its “lifetime”. The number represents the number of months passed since the first purchase.')

df = read_and_preprocess_data()

# Count monthly active customers from each cohort
grouping = df.groupby(['CohortMonth', 'CohortIndex'])
cohort_data = grouping['CustomerID'].apply(pd.Series.nunique)

st.write('# Cohort Counts')
cohort_data = cohort_data.reset_index()
cohort_counts = cohort_data.pivot(index='CohortMonth',columns='CohortIndex',values='CustomerID')
cohort_counts.index = cohort_counts.index.date
st.write(cohort_counts)


cohort_size = cohort_counts.iloc[:,0]
retention = cohort_counts.divide(cohort_size, axis=0)
retention = retention.round(3) * 100
retention = retention.sort_index()
st.write('# Retention Table')
st.write(retention)


fig = px.imshow(retention,
                labels=dict(x="CohortIndex", y="CohortMonth", color="Retention Rate"),
                x=retention.columns,
                y=retention.index,
                color_continuous_scale="BuPu",
                zmin=0.0,
                zmax=50,
                color_continuous_midpoint=None,
                origin='upper')

fig.update_layout(
    title='Retention Rates Heatmap',
    xaxis_title='Cohort Index',
    yaxis_title='Cohort Month',
    # coloraxis=dict(colorbar=dict(title="Retention Rate (%)"))
)

st.write('# Retention rates heatmap')
st.plotly_chart(fig)

grouping = df.groupby(['CohortMonth', 'CohortIndex'])
cohort_data = grouping['Quantity'].mean()
cohort_data = cohort_data.reset_index()
average_quantity = cohort_data.pivot(index='CohortMonth',columns='CohortIndex',values='Quantity')

average_quantity = average_quantity.round(1)

fig = px.imshow(average_quantity,
                labels=dict(x="CohortIndex", y="CohortMonth", color="Quantity"),
                x=average_quantity.columns,
                y=average_quantity.index,
                color_continuous_scale="BuGn",
                zmin=0.0,
                zmax=20,
                color_continuous_midpoint=None,
                origin='upper')

# Customize the layout
fig.update_layout(
    title='Average Quantity for Each Cohort',
    xaxis_title='Cohort Index',
    yaxis_title='Cohort Month',
)
# Display the Plotly figure in Streamlit
st.write('# Average quantity for each cohort')
st.plotly_chart(fig)