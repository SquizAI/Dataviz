import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static


data = pd.read_csv("bank_customer_churn_data.csv")


data = data.replace([float('inf'), float('-inf')], pd.NA)
data = data.dropna()

# Sidebar
st.sidebar.title("Interactive Filters")
selected_country = st.sidebar.multiselect('Select Country', options=data['Geography'].unique(), default=data['Geography'].unique())
min_age, max_age = st.sidebar.slider('Select Age Range', min_value=int(data['Age'].min()), max_value=int(data['Age'].max()), value=(20, 60))
min_credit_score, max_credit_score = st.sidebar.slider('Select Credit Score Range', min_value=int(data['CreditScore'].min()), max_value=int(data['CreditScore'].max()), value=(400, 850))

# Filter 
filtered_data = data[(data['Geography'].isin(selected_country)) & 
                     (data['Age'].between(min_age, max_age)) & 
                     (data['CreditScore'].between(min_credit_score, max_credit_score))]


st.title("Enhanced Bank Customer Churn Dashboard")

# key metrics
st.subheader("Key Metrics")
avg_credit_score = filtered_data['CreditScore'].mean()
avg_age = filtered_data['Age'].mean()
avg_tenure = filtered_data['Tenure'].mean()
avg_balance = filtered_data['Balance'].mean()

# Display Metrics in Columns
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Credit Score", f"{avg_credit_score:.2f}")
col2.metric("Average Age", f"{avg_age:.2f}")
col3.metric("Average Tenure", f"{avg_tenure:.2f}")
col4.metric("Average Balance", f"${avg_balance:,.2f}")

# 2D Graph: Balance vs. Credit Score
st.subheader("Balance vs Credit Score (Interactive 2D)")
fig = px.scatter(filtered_data, x='Balance', y='CreditScore', color='Exited', 
                 title="Balance vs Credit Score",
                 labels={"CreditScore": "Credit Score", "Balance": "Balance"},
                 hover_data=["NumOfProducts", "Age", "Exited"])
st.plotly_chart(fig)

# 3D Graph: Credit Score vs Age vs Num of Products
st.subheader("3D Graph: Credit Score vs Age vs Num of Products")
fig_3d = px.scatter_3d(filtered_data, x='CreditScore', y='Age', z='NumOfProducts', color='Exited',
                       title="3D Plot: Credit Score vs Age vs Number of Products",
                       labels={"CreditScore": "Credit Score", "Age": "Age", "NumOfProducts": "Number of Products"})
st.plotly_chart(fig_3d)

# Map Visualization 
st.subheader("Layered Map: Customer Exit Rates, Credit Score, and Balance by Country")

# latitude and longitude 
country_coords = {
    'France': [46.603354, 1.888334],
    'Germany': [51.165691, 10.451526],
    'Spain': [40.463667, -3.74922]
}

# Aggregate data by country
country_data = filtered_data.groupby('Geography').agg({
    'Exited': 'mean',
    'CreditScore': 'mean',
    'Balance': 'mean'
}).reset_index()

# Create Folium Map
m = folium.Map(location=[46.603354, 1.888334], zoom_start=5)

# Create Layer Groups
layer_exit_rate = folium.FeatureGroup(name="Exit Rate").add_to(m)
layer_credit_score = folium.FeatureGroup(name="Average Credit Score").add_to(m)
layer_balance = folium.FeatureGroup(name="Average Balance").add_to(m)

# Add data to map with layers
for _, row in country_data.iterrows():
    coords = country_coords.get(row['Geography'], [0, 0])
    
    # Exit Rate 
    folium.CircleMarker(
        location=coords,
        radius=10 * row['Exited'],  # Size based on exit rate
        color='red',
        fill=True,
        fill_opacity=0.7,
        popup=f"Country: {row['Geography']}\nExit Rate: {row['Exited']:.2%}"
    ).add_to(layer_exit_rate)
    
    # Average Credit Score 
    folium.CircleMarker(
        location=coords,
        radius=10 * (row['CreditScore'] / 100),  # Size scaled by credit score
        color='blue',
        fill=True,
        fill_opacity=0.6,
        popup=f"Country: {row['Geography']}\nAvg Credit Score: {row['CreditScore']:.2f}"
    ).add_to(layer_credit_score)
    
    # Average Balance 
    folium.CircleMarker(
        location=coords,
        radius=10 * (row['Balance'] / 50000),  # Size scaled by balance
        color='green',
        fill=True,
        fill_opacity=0.6,
        popup=f"Country: {row['Geography']}\nAvg Balance: ${row['Balance']:,.2f}"
    ).add_to(layer_balance)


folium.LayerControl().add_to(m)


folium_static(m)

# Gender-based Analysis
st.subheader("Gender-Based Analysis of Customer Exit Rates")
gender_data = filtered_data.groupby(['Gender', 'Exited']).size().reset_index(name='Count')
fig_gender = px.bar(gender_data, x='Gender', y='Count', color='Exited', 
                    title="Exit Rates by Gender", barmode="group")
st.plotly_chart(fig_gender)

# IsActiveMember vs Exited
st.subheader("Exit Rates by Active/Inactive Membership")
active_data = filtered_data.groupby(['IsActiveMember', 'Exited']).size().reset_index(name='Count')
fig_active = px.bar(active_data, x='IsActiveMember', y='Count', color='Exited', 
                    title="Exit Rates for Active vs Inactive Members", barmode="group")
st.plotly_chart(fig_active)

# Estimated Salary vs Exited
st.subheader("Estimated Salary vs Exit Status")
fig_salary = px.box(filtered_data, x='Exited', y='EstimatedSalary', color='Exited',
                    title="Distribution of Estimated Salary by Exit Status")
st.plotly_chart(fig_salary)

# Show dynamic text based on user interaction
st.subheader(f"Data Overview for Selected Filters: {len(filtered_data)} customers")
st.write("Explore customer behavior with dynamic filtering and deeper insights.")
