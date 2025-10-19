"""
Comprehensive Calendar Display
Shows ALL competitors with real-time pricing data in calendar format
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
    page_title="Comprehensive Pricing Calendar - ALL Competitors",
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
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7em;
        margin-left: 5px;
    }
    .failed-badge {
        background-color: #dc3545;
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7em;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)


def load_comprehensive_data():
    """Load the comprehensive scraping results"""
    output_dir = Path("output")
    comprehensive_file = output_dir / "comprehensive_results_all_competitors.json"
    
    if not comprehensive_file.exists():
        return []
    
    with open(comprehensive_file, 'r') as f:
        return json.load(f)


def group_by_company(data):
    """Group results by company and show best result per company"""
    companies = {}
    
    for result in data:
        company = result['company_name']
        
        if company not in companies:
            companies[company] = {
                'company_name': company,
                'currency': result['currency'],
                'working': result['working'],
                'best_result': None,
                'all_results': []
            }
        
        companies[company]['all_results'].append(result)
        
        # Keep the best (most successful) result
        if result['success'] and (companies[company]['best_result'] is None or 
                                 result['total_results'] > companies[company]['best_result']['total_results']):
            companies[company]['best_result'] = result
    
    return companies


def create_comprehensive_heatmap(companies):
    """Create a heatmap showing prices across all companies"""
    heatmap_data = []
    
    for company_name, company_data in companies.items():
        if company_data['best_result'] and company_data['best_result']['success']:
            for daily_price in company_data['best_result']['daily_prices']:
                heatmap_data.append({
                    'Company': company_name,
                    'Date': daily_price['date'],
                    'Price': daily_price['price'],
                    'Currency': daily_price['currency'],
                    'Location': company_data['best_result']['location'],
                    'Strategy': company_data['best_result']['strategy_used']
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
        title="Comprehensive Pricing Calendar - ALL Competitors",
        labels={'x': 'Date', 'y': 'Company', 'color': 'Price per Night'}
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Company"
    )
    
    return fig


def display_company_comprehensive(company_name, company_data):
    """Display comprehensive company information"""
    if not company_data['best_result'] or not company_data['best_result']['success']:
        # Show failed company
        st.markdown(f"""
        <div class="company-header">
            <h3>{company_name}</h3>
            <span class="status-not-working">❌ NOT WORKING</span>
        </div>
        <p><strong>Issue:</strong> {company_data['all_results'][0].get('notes', 'Unknown issue')}</p>
        <p><strong>Attempts:</strong> {len(company_data['all_results'])} strategies tried</p>
        """, unsafe_allow_html=True)
        return
    
    # Show successful company
    best_result = company_data['best_result']
    
    st.markdown(f"""
    <div class="company-header">
        <h3>{company_name}</h3>
        <span class="status-working">✅ WORKING</span>
        <p>{best_result['location']} | {best_result['currency']}{best_result['min_price']}-{best_result['max_price']}/night | Avg: {best_result['currency']}{best_result['avg_price']}</p>
        <p>Strategy: {best_result['strategy_used']} | {best_result['total_results']} days</p>
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
    for i, daily_price in enumerate(best_result['daily_prices']):
        with columns[i % 7]:
            price = daily_price['price']
            currency = daily_price['currency']
            
            # Determine price category
            if price <= best_result['min_price'] * 1.1:  # Within 10% of minimum
                price_class = "price-low"
            elif price <= best_result['avg_price'] * 1.1:  # Within 10% of average
                price_class = "price-medium"
            else:
                price_class = "price-high"
            
            st.markdown(f"""
            <div class="price-cell {price_class}">
                {currency}{price}
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main comprehensive calendar display function"""
    
    st.title("📅 Comprehensive Pricing Calendar - ALL Competitors")
    st.markdown("**Real-time pricing data from ALL competitors with multiple strategies**")
    
    # Load comprehensive data
    data = load_comprehensive_data()
    
    if not data:
        st.warning("No comprehensive data available. Please run the comprehensive scraper first.")
        st.info("Run: `python scrapers/comprehensive_calendar_scraper.py`")
        return
    
    # Group by company
    companies = group_by_company(data)
    
    # Summary metrics
    successful_companies = [name for name, data in companies.items() if data['best_result'] and data['best_result']['success']]
    failed_companies = [name for name, data in companies.items() if not data['best_result'] or not data['best_result']['success']]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(companies))
    
    with col2:
        st.metric("Working", len(successful_companies), delta=f"{len(successful_companies)/len(companies)*100:.1f}%")
    
    with col3:
        st.metric("Not Working", len(failed_companies), delta=f"{len(failed_companies)/len(companies)*100:.1f}%")
    
    with col4:
        if successful_companies:
            all_prices = []
            for company_name in successful_companies:
                best_result = companies[company_name]['best_result']
                all_prices.extend([dp['price'] for dp in best_result['daily_prices']])
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
        st.subheader("📊 Comprehensive Pricing Overview")
        
        # Price heatmap
        heatmap_fig = create_comprehensive_heatmap(companies)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.warning("No data available for heatmap")
        
        # Summary table
        if successful_companies:
            summary_data = []
            for company_name in successful_companies:
                best_result = companies[company_name]['best_result']
                summary_data.append({
                    'Company': company_name,
                    'Location': best_result['location'],
                    'Currency': best_result['currency'],
                    'Min Price': best_result['min_price'],
                    'Max Price': best_result['max_price'],
                    'Avg Price': best_result['avg_price'],
                    'Days Available': best_result['total_results'],
                    'Strategy': best_result['strategy_used']
                })
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
    
    with tabs[1]:
        st.subheader("📅 Individual Company Calendars")
        
        # Show all companies (working and not working)
        for company_name, company_data in companies.items():
            display_company_comprehensive(company_name, company_data)
            st.markdown("---")
    
    with tabs[2]:
        st.subheader("📈 Price Trends")
        
        # Create trend chart
        if successful_companies:
            trend_data = []
            for company_name in successful_companies:
                best_result = companies[company_name]['best_result']
                for daily_price in best_result['daily_prices']:
                    trend_data.append({
                        'Company': company_name,
                        'Date': daily_price['date'],
                        'Price': daily_price['price'],
                        'Currency': daily_price['currency'],
                        'Location': best_result['location']
                    })
            
            if trend_data:
                df = pd.DataFrame(trend_data)
                df['Date'] = pd.to_datetime(df['Date'])
                
                fig = px.line(
                    df, 
                    x='Date', 
                    y='Price', 
                    color='Company',
                    title="Comprehensive Price Trends - ALL Working Competitors",
                    labels={'Date': 'Date', 'Price': 'Price per Night'},
                    hover_data=['Currency', 'Location']
                )
                
                fig.update_layout(
                    height=500,
                    xaxis_title="Date",
                    yaxis_title="Price per Night"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No successful data available for trend chart")
    
    with tabs[3]:
        st.subheader("🔍 Detailed Data")
        
        # Show raw data
        st.json(data)
        
        # Show screenshots
        st.subheader("📸 Screenshots")
        screenshot_dir = Path("data/screenshots")
        if screenshot_dir.exists():
            screenshots = list(screenshot_dir.glob("*COMPREHENSIVE*.png"))
            if screenshots:
                for screenshot in screenshots[-20:]:  # Show last 20
                    st.write(f"• {screenshot.name}")
            else:
                st.write("No comprehensive screenshots found.")


if __name__ == "__main__":
    main()
