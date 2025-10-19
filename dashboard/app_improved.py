"""
Improved Competitive Intelligence Dashboard
Clearly distinguishes between real and estimated data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import (
    get_session, CompetitorPrice, MarketIntelligence,
    PriceAlert, CompetitorIntelligence
)

# Page config
st.set_page_config(
    page_title="Indie Campers Intelligence - Real Data",
    page_icon="🚐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with real/estimated indicators
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .real-data {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 5px 0;
    }
    .estimated-data {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
    }
    .error-data {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
    }
    .data-status {
        font-size: 0.8em;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 3px;
        margin-left: 5px;
    }
    .status-real {
        background-color: #28a745;
        color: white;
    }
    .status-estimated {
        background-color: #ffc107;
        color: black;
    }
    .status-error {
        background-color: #dc3545;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_latest_data():
    """Load latest intelligence data with caching"""
    session = get_session()

    # Get latest price for each competitor
    from sqlalchemy import func
    subquery = session.query(
        CompetitorPrice.company_name,
        func.max(CompetitorPrice.scrape_timestamp).label('max_timestamp')
    ).group_by(CompetitorPrice.company_name).subquery()

    prices = session.query(CompetitorPrice).join(
        subquery,
        (CompetitorPrice.company_name == subquery.c.company_name) &
        (CompetitorPrice.scrape_timestamp == subquery.c.max_timestamp)
    ).all()

    # Convert to dict format
    price_data = []
    for price in prices:
        price_dict = {
            'company_name': price.company_name,
            'base_nightly_rate': price.base_nightly_rate,
            'currency': price.currency,
            'data_completeness_pct': price.data_completeness_pct,
            'is_estimated': price.is_estimated,
            'scraping_strategy_used': price.scraping_strategy_used,
            'notes': price.notes,
            'scrape_timestamp': price.scrape_timestamp,
            'data_source_url': price.data_source_url
        }
        price_data.append(price_dict)

    session.close()
    return price_data


def get_data_status(price_record):
    """Determine data status based on record"""
    if price_record.get('is_estimated', True):
        return 'estimated'
    elif price_record.get('notes') and ('error' in price_record.get('notes', '').lower() or '404' in price_record.get('notes', '').lower()):
        return 'error'
    else:
        return 'real'


def show_data_quality_summary(prices):
    """Show summary of data quality"""
    st.header("📊 Data Quality Summary")
    
    real_data = [p for p in prices if get_data_status(p) == 'real']
    estimated_data = [p for p in prices if get_data_status(p) == 'estimated']
    error_data = [p for p in prices if get_data_status(p) == 'error']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(prices))
    
    with col2:
        st.metric("Real Data", len(real_data), delta=f"{len(real_data)/len(prices)*100:.1f}%")
    
    with col3:
        st.metric("Estimated Data", len(estimated_data), delta=f"{len(estimated_data)/len(prices)*100:.1f}%")
    
    with col4:
        st.metric("Error/No Data", len(error_data), delta=f"{len(error_data)/len(prices)*100:.1f}%")
    
    # Data quality breakdown
    st.subheader("📈 Data Quality Breakdown")
    
    if real_data:
        st.markdown("### ✅ Real Data Sources")
        for price in real_data:
            status_badge = '<span class="data-status status-real">REAL</span>'
            st.markdown(f"""
            <div class="real-data">
                <strong>{price['company_name']}</strong> {status_badge}<br/>
                Price: {price['currency']}{price['base_nightly_rate']}/night<br/>
                Strategy: {price['scraping_strategy_used']}<br/>
                <small>Last updated: {price['scrape_timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    if estimated_data:
        st.markdown("### ⚠️ Estimated Data Sources")
        for price in estimated_data:
            status_badge = '<span class="data-status status-estimated">ESTIMATED</span>'
            st.markdown(f"""
            <div class="estimated-data">
                <strong>{price['company_name']}</strong> {status_badge}<br/>
                Price: {price['currency']}{price['base_nightly_rate']}/night (estimated)<br/>
                Strategy: {price['scraping_strategy_used']}<br/>
                <small>Note: {price.get('notes', 'No additional notes')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    if error_data:
        st.markdown("### ❌ Error/No Data Sources")
        for price in error_data:
            status_badge = '<span class="data-status status-error">ERROR</span>'
            st.markdown(f"""
            <div class="error-data">
                <strong>{price['company_name']}</strong> {status_badge}<br/>
                Issue: {price.get('notes', 'Unknown error')}<br/>
                Strategy: {price['scraping_strategy_used']}<br/>
                <small>Last attempted: {price['scrape_timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)


def show_price_comparison(prices):
    """Show price comparison with real vs estimated indicators"""
    st.header("💰 Price Comparison")
    
    if not prices:
        st.warning("No pricing data available.")
        return
    
    # Separate real and estimated data
    real_prices = [p for p in prices if get_data_status(p) == 'real' and p.get('base_nightly_rate')]
    estimated_prices = [p for p in prices if get_data_status(p) == 'estimated' and p.get('base_nightly_rate')]
    
    if not real_prices and not estimated_prices:
        st.warning("No valid pricing data available.")
        return
    
    # Create comparison chart
    fig = go.Figure()
    
    # Add real data
    if real_prices:
        real_companies = [p['company_name'] for p in real_prices]
        real_price_values = [p['base_nightly_rate'] for p in real_prices]
        real_currencies = [p['currency'] for p in real_prices]
        
        fig.add_trace(go.Bar(
            name='Real Data',
            x=real_companies,
            y=real_price_values,
            marker_color='#28a745',
            text=[f"{curr}{price}" for curr, price in zip(real_currencies, real_price_values)],
            textposition='auto',
        ))
    
    # Add estimated data
    if estimated_prices:
        est_companies = [p['company_name'] for p in estimated_prices]
        est_price_values = [p['base_nightly_rate'] for p in estimated_prices]
        est_currencies = [p['currency'] for p in estimated_prices]
        
        fig.add_trace(go.Bar(
            name='Estimated Data',
            x=est_companies,
            y=est_price_values,
            marker_color='#ffc107',
            text=[f"{curr}{price} (est)" for curr, price in zip(est_currencies, est_price_values)],
            textposition='auto',
        ))
    
    fig.update_layout(
        title="Competitor Pricing - Real vs Estimated Data",
        xaxis_title="Company",
        yaxis_title="Price per Night",
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if real_prices:
            real_avg = sum(p['base_nightly_rate'] for p in real_prices) / len(real_prices)
            st.metric("Real Data Average", f"€{real_avg:.2f}/night", help="Average of verified real prices")
        else:
            st.metric("Real Data Average", "N/A", help="No real data available")
    
    with col2:
        if estimated_prices:
            est_avg = sum(p['base_nightly_rate'] for p in estimated_prices) / len(estimated_prices)
            st.metric("Estimated Average", f"€{est_avg:.2f}/night", help="Average of estimated prices")
        else:
            st.metric("Estimated Average", "N/A", help="No estimated data")
    
    with col3:
        total_companies = len([p for p in prices if p.get('base_nightly_rate')])
        real_count = len(real_prices)
        st.metric("Data Quality", f"{real_count}/{total_companies}", help="Real data / Total companies")


def show_competitor_details(prices):
    """Show detailed competitor information"""
    st.header("🔍 Competitor Details")
    
    if not prices:
        st.warning("No competitor data available.")
        return
    
    # Create DataFrame for better display
    df_data = []
    for price in prices:
        status = get_data_status(price)
        df_data.append({
            'Company': price['company_name'],
            'Price': f"{price['currency']}{price['base_nightly_rate']}/night" if price.get('base_nightly_rate') else 'N/A',
            'Status': status.upper(),
            'Strategy': price['scraping_strategy_used'],
            'Completeness': f"{price['data_completeness_pct']:.1f}%" if price.get('data_completeness_pct') else 'N/A',
            'Last Updated': price['scrape_timestamp'].strftime('%Y-%m-%d %H:%M'),
            'Notes': price.get('notes', '')[:100] + '...' if price.get('notes') and len(price.get('notes', '')) > 100 else price.get('notes', '')
        })
    
    df = pd.DataFrame(df_data)
    
    # Color code the status column
    def color_status(val):
        if val == 'REAL':
            return 'background-color: #d4edda'
        elif val == 'ESTIMATED':
            return 'background-color: #fff3cd'
        elif val == 'ERROR':
            return 'background-color: #f8d7da'
        return ''
    
    styled_df = df.style.applymap(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)


def main():
    """Main dashboard function"""
    
    st.title("🚐 Indie Campers Competitive Intelligence")
    st.markdown("**Real vs Estimated Data Dashboard**")
    
    # Load data
    prices = load_latest_data()
    
    if not prices:
        st.error("No data available. Please run the intelligence gathering first.")
        return
    
    # Main tabs
    tabs = st.tabs([
        "📊 Data Quality",
        "💰 Price Comparison", 
        "🔍 Competitor Details",
        "📸 Screenshots"
    ])
    
    with tabs[0]:
        show_data_quality_summary(prices)
    
    with tabs[1]:
        show_price_comparison(prices)
    
    with tabs[2]:
        show_competitor_details(prices)
    
    with tabs[3]:
        st.header("📸 Screenshot Evidence")
        st.info("Screenshots are saved in the data/screenshots/ directory")
        
        # List available screenshots
        screenshot_dir = Path("data/screenshots")
        if screenshot_dir.exists():
            screenshots = list(screenshot_dir.glob("*.png"))
            if screenshots:
                st.write(f"Found {len(screenshots)} screenshots:")
                for screenshot in screenshots[-10:]:  # Show last 10
                    st.write(f"• {screenshot.name}")
            else:
                st.write("No screenshots found.")
        else:
            st.write("Screenshots directory not found.")


if __name__ == "__main__":
    main()
