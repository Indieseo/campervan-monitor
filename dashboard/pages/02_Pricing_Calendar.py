"""
Pricing Calendar Visualization
View price per night for each model, each date, each company
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta, date
from pathlib import Path

st.set_page_config(page_title="Pricing Calendar", page_icon="📅", layout="wide")

st.title("📅 Comprehensive Pricing Calendar")
st.markdown("**Model-specific pricing for every date across all competitors**")

# Load latest pricing calendar
calendar_files = list(Path("output").glob("pricing_calendar_*.json"))
if not calendar_files:
    st.warning("⚠️ No pricing calendar data found. Run comprehensive scraper first.")
    st.code("python scrapers/comprehensive_pricing_scraper.py")
    st.stop()

latest_calendar_file = max(calendar_files, key=lambda p: p.stat().st_mtime)

with open(latest_calendar_file, 'r') as f:
    calendar_data = json.load(f)

# Display metadata
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Companies", len(calendar_data['companies']))
with col2:
    total_models = sum(len(comp['models']) for comp in calendar_data['companies'].values())
    st.metric("Total Models", total_models)
with col3:
    st.metric("Date Range", f"{calendar_data['metadata']['total_days']} days")
with col4:
    st.metric("Data Points", total_models * calendar_data['metadata']['total_days'])

st.divider()

# Company selector
companies = list(calendar_data['companies'].keys())
selected_company = st.selectbox("🏢 Select Company", companies)

if selected_company:
    company_data = calendar_data['companies'][selected_company]
    
    # Display company info
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Country:** {company_data['country']}")
        st.info(f"**Currency:** {company_data['currency']}")
    with col2:
        st.info(f"**Search Location:** {company_data['search_location']}")
        st.info(f"**Models Available:** {len(company_data['models'])}")
    
    st.divider()
    
    # Model selector
    models = company_data['models']
    model_names = [m['model_name'] for m in models]
    
    view_mode = st.radio("View Mode", ["Single Model", "All Models Comparison", "Heatmap Calendar"])
    
    if view_mode == "Single Model":
        selected_model_name = st.selectbox("🚐 Select Model", model_names)
        selected_model = next(m for m in models if m['model_name'] == selected_model_name)
        
        # Display model details
        st.subheader(f"📊 {selected_model['model_name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Category", selected_model['category'])
        with col2:
            st.metric("Sleeps", f"{selected_model['sleeps']} people")
        with col3:
            features_str = ", ".join(selected_model.get('features', []))
            st.metric("Features", f"{len(selected_model.get('features', []))} total")
        
        if selected_model.get('features'):
            st.write("**Features:**", ", ".join(selected_model['features']))
        
        st.divider()
        
        # Create pricing dataframe
        pricing_cal = selected_model['pricing_calendar']
        df = pd.DataFrame([
            {'Date': date_str, 'Price': price}
            for date_str, price in pricing_cal.items()
        ])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        df['Day of Week'] = df['Date'].dt.day_name()
        df['Is Weekend'] = df['Date'].dt.dayofweek.isin([5, 6])
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min Price", f"{company_data['currency']} {df['Price'].min():.2f}/night")
        with col2:
            st.metric("Max Price", f"{company_data['currency']} {df['Price'].max():.2f}/night")
        with col3:
            st.metric("Average", f"{company_data['currency']} {df['Price'].mean():.2f}/night")
        with col4:
            price_range = df['Price'].max() - df['Price'].min()
            st.metric("Range", f"{company_data['currency']} {price_range:.2f}")
        
        # Line chart
        fig = px.line(df, x='Date', y='Price', 
                     title=f"{selected_model['model_name']} - Price Trend",
                     markers=True)
        fig.update_layout(height=400, hovermode='x unified')
        fig.update_traces(line_color='#667eea', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calendar table
        st.subheader("📅 Daily Pricing Table")
        
        # Add price category
        df['Price Category'] = pd.cut(df['Price'], bins=3, labels=['Low', 'Medium', 'High'])
        
        # Display table with formatting
        st.dataframe(
            df[['Date', 'Day of Week', 'Price', 'Price Category', 'Is Weekend']],
            use_container_width=True,
            height=400
        )
        
    elif view_mode == "All Models Comparison":
        st.subheader(f"📊 All Models Price Comparison - {selected_company}")
        
        # Create comparison dataframe
        all_data = []
        for model in models:
            for date_str, price in model['pricing_calendar'].items():
                all_data.append({
                    'Model': model['model_name'],
                    'Date': date_str,
                    'Price': price,
                    'Category': model['category'],
                    'Sleeps': model['sleeps']
                })
        
        df_all = pd.DataFrame(all_data)
        df_all['Date'] = pd.to_datetime(df_all['Date'])
        df_all = df_all.sort_values('Date')
        
        # Multi-line chart
        fig = px.line(df_all, x='Date', y='Price', color='Model',
                     title=f"{selected_company} - All Models Price Trends",
                     markers=True)
        fig.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Model comparison table
        st.subheader("📊 Model Statistics")
        model_stats = df_all.groupby('Model').agg({
            'Price': ['min', 'max', 'mean'],
            'Date': 'count'
        }).round(2)
        model_stats.columns = ['Min Price', 'Max Price', 'Avg Price', 'Days']
        st.dataframe(model_stats, use_container_width=True)
        
    elif view_mode == "Heatmap Calendar":
        st.subheader(f"🗓️ Pricing Heatmap - {selected_company}")
        
        # Create heatmap data
        selected_model_name = st.selectbox("Select Model for Heatmap", model_names)
        selected_model = next(m for m in models if m['model_name'] == selected_model_name)
        
        # Prepare data
        pricing_cal = selected_model['pricing_calendar']
        dates = sorted(pricing_cal.keys())
        prices = [pricing_cal[d] for d in dates]
        
        # Create calendar grid (weeks x days)
        df_cal = pd.DataFrame([
            {'Date': date_str, 'Price': pricing_cal[date_str]}
            for date_str in dates
        ])
        df_cal['Date'] = pd.to_datetime(df_cal['Date'])
        df_cal['Week'] = df_cal['Date'].dt.isocalendar().week
        df_cal['Day of Week'] = df_cal['Date'].dt.day_name()
        df_cal['Day Num'] = df_cal['Date'].dt.dayofweek
        
        # Pivot for heatmap
        heatmap_data = df_cal.pivot_table(
            values='Price',
            index='Week',
            columns='Day of Week',
            aggfunc='first'
        )
        
        # Reorder columns to start with Monday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(columns=[d for d in day_order if d in heatmap_data.columns])
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='RdYlGn_r',  # Red = expensive, Green = cheap
            text=heatmap_data.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10},
            colorbar=dict(title=f"Price ({company_data['currency']})")
        ))
        
        fig.update_layout(
            title=f"{selected_model['model_name']} - Price Heatmap",
            xaxis_title="Day of Week",
            yaxis_title="Week Number",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Download data
st.divider()
st.subheader("💾 Export Data")

if st.button("📥 Download Pricing Calendar JSON"):
    st.download_button(
        label="⬇️ Download JSON",
        data=json.dumps(calendar_data, indent=2),
        file_name=f"pricing_calendar_{selected_company}_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

# Show raw data structure
with st.expander("🔍 View Raw Data Structure"):
    st.json(calendar_data['companies'][selected_company])




