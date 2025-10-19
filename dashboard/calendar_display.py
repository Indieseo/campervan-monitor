"""
Live Pricing Calendar Display
Shows real-time pricing data in calendar format for all competitors
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Live Pricing Calendar",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for calendar display
st.markdown("""
<style>
    .calendar-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .price-cell {
        text-align: center;
        padding: 8px;
        border-radius: 5px;
        margin: 2px;
        font-weight: bold;
    }
    .price-low {
        background-color: #d4edda;
        color: #155724;
    }
    .price-medium {
        background-color: #fff3cd;
        color: #856404;
    }
    .price-high {
        background-color: #f8d7da;
        color: #721c24;
    }
    .company-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .status-working {
        background-color: #d4edda;
        color: #155724;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
    }
    .status-not-working {
        background-color: #f8d7da;
        color: #721c24;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)


def load_calendar_data():
    """Load the latest calendar scraping results"""
    output_dir = Path("output")
    calendar_files = sorted(output_dir.glob("calendar_scraping_results_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not calendar_files:
        return []
    
    with open(calendar_files[0], 'r') as f:
        return json.load(f)


def create_price_heatmap(calendar_data):
    """Create a heatmap showing prices across competitors and dates"""
    if not calendar_data:
        return None
    
    # Prepare data for heatmap
    heatmap_data = []
    for result in calendar_data:
        if result['success']:
            for daily_price in result['daily_prices']:
                heatmap_data.append({
                    'Company': result['company_name'],
                    'Date': daily_price['date'],
                    'Price': daily_price['price'],
                    'Currency': daily_price['currency'],
                    'Location': result['location']
                })
    
    if not heatmap_data:
        return None
    
    df = pd.DataFrame(heatmap_data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Create pivot table for heatmap
    pivot_df = df.pivot_table(
        index='Company', 
        columns='Date', 
        values='Price', 
        aggfunc='mean'
    )
    
    # Create heatmap
    fig = px.imshow(
        pivot_df.values,
        x=pivot_df.columns.strftime('%m/%d'),
        y=pivot_df.index,
        color_continuous_scale='RdYlGn_r',  # Red-Yellow-Green (reversed so green = low price)
        title="Live Pricing Calendar - Heatmap View",
        labels={'x': 'Date', 'y': 'Company', 'color': 'Price per Night'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Company"
    )
    
    return fig


def create_price_trend_chart(calendar_data):
    """Create a line chart showing price trends over time"""
    if not calendar_data:
        return None
    
    # Prepare data for trend chart
    trend_data = []
    for result in calendar_data:
        if result['success']:
            for daily_price in result['daily_prices']:
                trend_data.append({
                    'Company': result['company_name'],
                    'Date': daily_price['date'],
                    'Price': daily_price['price'],
                    'Currency': daily_price['currency'],
                    'Location': result['location']
                })
    
    if not trend_data:
        return None
    
    df = pd.DataFrame(trend_data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Create line chart
    fig = px.line(
        df, 
        x='Date', 
        y='Price', 
        color='Company',
        title="Live Pricing Trends - 7 Day View",
        labels={'Date': 'Date', 'Price': 'Price per Night'},
        hover_data=['Currency', 'Location']
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Price per Night"
    )
    
    return fig


def display_company_calendar(result):
    """Display individual company calendar"""
    if not result['success']:
        st.markdown(f"""
        <div class="company-header">
            <h3>{result['company_name']}</h3>
            <span class="status-not-working">❌ NOT WORKING</span>
        </div>
        <p><strong>Issue:</strong> {result['notes']}</p>
        """, unsafe_allow_html=True)
        return
    
    # Company header
    st.markdown(f"""
    <div class="company-header">
        <h3>{result['company_name']}</h3>
        <span class="status-working">✅ WORKING</span>
        <p>{result['location']} | {result['currency']}{result['min_price']}-{result['max_price']}/night | Avg: {result['currency']}{result['avg_price']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create calendar grid
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    columns = [col1, col2, col3, col4, col5, col6, col7]
    
    # Header row
    for i, (col, day) in enumerate(zip(columns, days)):
        with col:
            st.markdown(f"**{day}**")
    
    # Price rows
    for i, daily_price in enumerate(result['daily_prices']):
        with columns[i % 7]:
            price = daily_price['price']
            currency = daily_price['currency']
            
            # Determine price category
            if price <= result['min_price'] * 1.1:  # Within 10% of minimum
                price_class = "price-low"
            elif price <= result['avg_price'] * 1.1:  # Within 10% of average
                price_class = "price-medium"
            else:
                price_class = "price-high"
            
            st.markdown(f"""
            <div class="price-cell {price_class}">
                {currency}{price}
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main calendar display function"""
    
    st.title("📅 Live Pricing Calendar")
    st.markdown("**Real-time pricing data from all competitors**")
    
    # Load calendar data
    calendar_data = load_calendar_data()
    
    if not calendar_data:
        st.warning("No calendar data available. Please run the calendar scraper first.")
        st.info("Run: `python scrapers/live_pricing_calendar_scraper.py`")
        return
    
    # Summary metrics
    successful_results = [r for r in calendar_data if r['success']]
    failed_results = [r for r in calendar_data if not r['success']]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(calendar_data))
    
    with col2:
        st.metric("Working", len(successful_results), delta=f"{len(successful_results)/len(calendar_data)*100:.1f}%")
    
    with col3:
        st.metric("Not Working", len(failed_results), delta=f"{len(failed_results)/len(calendar_data)*100:.1f}%")
    
    with col4:
        if successful_results:
            all_prices = []
            for result in successful_results:
                all_prices.extend([dp['price'] for dp in result['daily_prices']])
            if all_prices:
                st.metric("Market Range", f"${min(all_prices):.0f}-${max(all_prices):.0f}")
    
    st.markdown("---")
    
    # Tabs for different views
    tabs = st.tabs([
        "📊 Overview Charts",
        "📅 Individual Calendars",
        "📈 Price Trends",
        "🔍 Detailed Data"
    ])
    
    with tabs[0]:
        st.subheader("📊 Pricing Overview")
        
        # Price heatmap
        heatmap_fig = create_price_heatmap(calendar_data)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.warning("No data available for heatmap")
        
        # Summary table
        if successful_results:
            summary_data = []
            for result in successful_results:
                summary_data.append({
                    'Company': result['company_name'],
                    'Location': result['location'],
                    'Currency': result['currency'],
                    'Min Price': result['min_price'],
                    'Max Price': result['max_price'],
                    'Avg Price': result['avg_price'],
                    'Days Available': result['total_results']
                })
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
    
    with tabs[1]:
        st.subheader("📅 Individual Company Calendars")
        
        for result in calendar_data:
            display_company_calendar(result)
            st.markdown("---")
    
    with tabs[2]:
        st.subheader("📈 Price Trends")
        
        trend_fig = create_price_trend_chart(calendar_data)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.warning("No data available for trend chart")
    
    with tabs[3]:
        st.subheader("🔍 Detailed Data")
        
        # Show raw data
        st.json(calendar_data)
        
        # Show screenshots
        st.subheader("📸 Screenshots")
        screenshot_dir = Path("data/screenshots")
        if screenshot_dir.exists():
            screenshots = list(screenshot_dir.glob("*CALENDAR*.png"))
            if screenshots:
                for screenshot in screenshots[-10:]:  # Show last 10
                    st.write(f"• {screenshot.name}")
            else:
                st.write("No calendar screenshots found.")


if __name__ == "__main__":
    main()



