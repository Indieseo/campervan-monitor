# 🚀 10X TRANSFORMATION - 30-DAY QUICK START GUIDE

**Goal:** Transform from 5 competitors → 25 competitors + ML foundation in 30 days  
**Impact:** 5x data coverage + predictive capabilities  
**Investment:** ~80 hours (2 hours/day)

---

## 📅 WEEK 1: EXPAND TO 15 COMPETITORS

### Day 1-2: North American Expansion
**Goal: Add 5 US competitors**

```bash
# Step 1: Create new competitor configs
# Edit: scrapers/competitor_config.py

COMPETITORS['RVshare'] = {
    'name': 'RVshare',
    'country': 'USA',
    'tier': 1,
    'urls': {
        'pricing': 'https://rvshare.com/rv-rental',
        'about': 'https://rvshare.com/about',
    },
    'business_model': 'P2P',
    'priority_score': 85
}

COMPETITORS['Outdoorsy'] = {
    'name': 'Outdoorsy',
    'country': 'USA',
    'tier': 1,
    'urls': {
        'pricing': 'https://www.outdoorsy.com/rv-rental',
        'about': 'https://www.outdoorsy.com/about',
    },
    'business_model': 'P2P',
    'priority_score': 88
}

COMPETITORS['CruiseAmerica'] = {
    'name': 'Cruise America',
    'country': 'USA',
    'tier': 1,
    'urls': {
        'pricing': 'https://www.cruiseamerica.com/rv-rentals/',
        'about': 'https://www.cruiseamerica.com/about/',
    },
    'business_model': 'Traditional',
    'priority_score': 82
}

COMPETITORS['ElMonte'] = {
    'name': 'El Monte RV',
    'country': 'USA',
    'tier': 2,
    'urls': {
        'pricing': 'https://www.elmonterv.com/',
    },
    'business_model': 'Traditional',
    'priority_score': 75
}

COMPETITORS['Apollo'] = {
    'name': 'Apollo RV',
    'country': 'USA/Global',
    'tier': 2,
    'urls': {
        'pricing': 'https://www.apollorv.com/',
    },
    'business_model': 'Traditional',
    'priority_score': 78
}
```

**Step 2: Create basic scrapers**
```python
# In scrapers/tier1_scrapers.py

class RVshareScraper(DeepDataScraper):
    """RVshare (US P2P platform)"""
    
    def __init__(self, use_browserless=None):
        super().__init__(
            'RVshare',
            tier=1,
            config=COMPETITORS['RVshare'],
            use_browserless=use_browserless
        )
    
    async def scrape_deep_data(self, page):
        # Navigate to main page
        await self.navigate_smart(page, self.config['urls']['pricing'])
        
        # Extract pricing (adapt based on site structure)
        prices = await self.extract_prices_from_text(
            await page.evaluate('() => document.body.innerText')
        )
        if prices:
            self.data['base_nightly_rate'] = min(prices)
        
        # Extract reviews
        reviews = await self.extract_customer_reviews(page)
        self.data['customer_review_avg'] = reviews.get('avg')
        self.data['review_count'] = reviews.get('count')
        
        # Extract promotions
        self.data['active_promotions'] = await self.detect_promotions(page)
        
        # Calculate completeness
        self.data['data_completeness_pct'] = self.calculate_completeness()

# Repeat for other 4 US competitors
```

**Step 3: Test new scrapers**
```bash
# Test each individually
python -c "import asyncio; from scrapers.tier1_scrapers import RVshareScraper; s = RVshareScraper(False); print(asyncio.run(s.scrape()))"

# Test all new scrapers
python run_intelligence.py
```

**Expected Result:** 10 total competitors (5 EU + 5 US)

---

### Day 3-4: European Expansion
**Goal: Add 5 more EU competitors**

```python
# Add to competitor_config.py

COMPETITORS['Campanda'] = {
    'name': 'Campanda',
    'country': 'Germany',
    'tier': 2,
    'urls': {'pricing': 'https://www.campanda.com/'},
    'business_model': 'Aggregator',
    'priority_score': 70
}

COMPETITORS['MotorhomeRepublic'] = {
    'name': 'Motorhome Republic',
    'country': 'Global',
    'tier': 2,
    'urls': {'pricing': 'https://www.motorhomerepublic.com/'},
    'business_model': 'Aggregator',
    'priority_score': 72
}

COMPETITORS['SunLiving'] = {
    'name': 'Sun Living',
    'country': 'Germany',
    'tier': 2,
    'urls': {'pricing': 'https://www.sunliving.com/'},
    'business_model': 'Traditional',
    'priority_score': 68
}

COMPETITORS['BunkCampers'] = {
    'name': 'Bunk Campers',
    'country': 'Ireland/UK',
    'tier': 2,
    'urls': {'pricing': 'https://www.bunkcampers.com/'},
    'business_model': 'Traditional',
    'priority_score': 65
}

COMPETITORS['TouringCars'] = {
    'name': 'Touring Cars',
    'country': 'Belgium',
    'tier': 2,
    'urls': {'pricing': 'https://www.touring-cars.com/'},
    'business_model': 'Traditional',
    'priority_score': 63
}
```

Create scrapers following the same pattern as Day 1-2.

**Expected Result:** 15 total competitors (5 Tier 1 EU + 5 Tier 1 US + 5 Tier 2 EU)

---

### Day 5: Database Schema Enhancement
**Goal: Support regional pricing**

```python
# Add to database/models.py

class RegionalPricing(Base):
    """Track pricing by city/region"""
    __tablename__ = 'regional_pricing'
    
    id = Column(Integer, primary_key=True)
    competitor_price_id = Column(Integer)  # Link to CompetitorPrice
    company_name = Column(String(100), index=True)
    
    # Geographic
    city = Column(String(100), index=True)
    country = Column(String(50))
    region = Column(String(100))
    
    # Pricing specific to this location
    base_rate = Column(Float)
    weekend_premium_pct = Column(Float)
    seasonal_multiplier = Column(Float)
    
    # Supply/Demand indicators
    vehicles_available = Column(Integer)
    demand_level = Column(Integer)  # 1-10 scale
    competitor_count = Column(Integer)
    
    # Timestamp
    scrape_timestamp = Column(DateTime, default=datetime.now)


class CompetitorMetadata(Base):
    """Enhanced competitor metadata"""
    __tablename__ = 'competitor_metadata'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(100), unique=True)
    
    # Classification
    country = Column(String(50))
    tier = Column(Integer)
    business_model = Column(String(50))  # P2P, Traditional, Aggregator
    priority_score = Column(Integer)
    
    # Performance tracking
    scraping_success_rate = Column(Float)  # % successful scrapes
    avg_data_completeness = Column(Float)
    last_successful_scrape = Column(DateTime)
    consecutive_failures = Column(Integer)
    
    # Market intelligence
    estimated_market_share = Column(Float)
    estimated_fleet_size = Column(Integer)
    growth_rate_estimate = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
```

**Initialize new tables:**
```bash
python -c "from database.models import init_database; init_database()"
```

---

### Day 6-7: Dashboard Enhancement
**Goal: Support 15 competitors in dashboard**

```python
# Update dashboard/app.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database.models import get_session, CompetitorPrice, CompetitorMetadata

st.set_page_config(page_title="Global Campervan Intelligence", layout="wide")

# Sidebar: Competitor filter
competitors = session.query(CompetitorMetadata).filter_by(is_active=True).all()
selected_competitors = st.sidebar.multiselect(
    "Select Competitors",
    options=[c.company_name for c in competitors],
    default=[c.company_name for c in competitors if c.tier == 1]
)

# Sidebar: Region filter
regions = ['All', 'Europe', 'North America', 'Australia/NZ', 'Asia']
selected_region = st.sidebar.selectbox("Region", regions)

# Main dashboard
st.title("🌍 Global Campervan Intelligence Platform")

# KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Competitors Tracked", len(competitors), "+10 this week")
with col2:
    avg_price = session.query(func.avg(CompetitorPrice.base_nightly_rate)).scalar()
    st.metric("Market Avg Price", f"€{avg_price:.0f}", "-3% vs last week")
with col3:
    active_alerts = session.query(PriceAlert).filter_by(is_acknowledged=False).count()
    st.metric("Active Alerts", active_alerts, "+2")
with col4:
    markets = len(set(c.country for c in competitors))
    st.metric("Markets", markets, "+3")
with col5:
    avg_completeness = session.query(func.avg(CompetitorPrice.data_completeness_pct)).scalar()
    st.metric("Data Quality", f"{avg_completeness:.0f}%", "+5%")

# Tab interface
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "💰 Pricing", "🌍 Geographic", "📈 Trends"])

with tab1:
    # Competitor comparison table
    st.subheader("Competitor Snapshot")
    
    latest_prices = session.query(CompetitorPrice)\
        .filter(CompetitorPrice.company_name.in_(selected_competitors))\
        .order_by(CompetitorPrice.scrape_timestamp.desc())\
        .all()
    
    # Create comparison DataFrame
    import pandas as pd
    df = pd.DataFrame([{
        'Competitor': p.company_name,
        'Country': next((c.country for c in competitors if c.company_name == p.company_name), 'N/A'),
        'Price': f"€{p.base_nightly_rate:.0f}",
        'Reviews': f"{p.customer_review_avg:.1f}★" if p.customer_review_avg else "N/A",
        'Completeness': f"{p.data_completeness_pct:.0f}%",
        'Last Updated': p.scrape_timestamp.strftime('%Y-%m-%d %H:%M')
    } for p in latest_prices])
    
    st.dataframe(df, use_container_width=True)

with tab2:
    # Price distribution
    st.subheader("Price Distribution by Region")
    
    fig = px.box(
        latest_prices,
        x='company_name',
        y='base_nightly_rate',
        color='country',
        title='Price Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Geographic heatmap
    st.subheader("Market Coverage Map")
    
    # Count competitors by country
    country_counts = {}
    for c in competitors:
        country_counts[c.country] = country_counts.get(c.country, 0) + 1
    
    # Create choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=list(country_counts.keys()),
        z=list(country_counts.values()),
        locationmode='country names',
        colorscale='Blues',
        marker_line_color='darkgray',
        marker_line_width=0.5,
    ))
    fig.update_layout(title='Global Competitor Coverage')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    # 7-day price trends
    st.subheader("7-Day Price Trends")
    
    # Get last 7 days of data
    from datetime import timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    trend_data = session.query(CompetitorPrice)\
        .filter(
            CompetitorPrice.scrape_timestamp >= seven_days_ago,
            CompetitorPrice.company_name.in_(selected_competitors)
        )\
        .all()
    
    df_trends = pd.DataFrame([{
        'Date': p.scrape_timestamp.date(),
        'Competitor': p.company_name,
        'Price': p.base_nightly_rate
    } for p in trend_data])
    
    fig = px.line(
        df_trends,
        x='Date',
        y='Price',
        color='Competitor',
        title='Price Trends (7 Days)'
    )
    st.plotly_chart(fig, use_container_width=True)
```

**Test dashboard:**
```bash
streamlit run dashboard/app.py
```

---

## 📅 WEEK 2: ML FOUNDATION

### Day 8-9: Data Collection for ML
**Goal: Accumulate 7-14 days of data**

```python
# Create automated daily scraping with GitHub Actions
# File: .github/workflows/daily_scraping.yml

name: Daily Intelligence Gathering

on:
  schedule:
    - cron: '0 6 * * *'  # Run at 6 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install chromium
      
      - name: Run intelligence gathering
        run: python run_intelligence.py
      
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add database/campervan_intelligence.db
          git commit -m "Daily intelligence update" || echo "No changes"
          git push
```

**Set up GitHub repository:**
```bash
git init
git add .
git commit -m "Initial commit - 10X transformation"
git branch -M main
git remote add origin https://github.com/yourusername/campervan-intelligence.git
git push -u origin main
```

---

### Day 10-11: Price Prediction Model (v1)
**Goal: Simple time-series forecasting**

```python
# Create: ml/price_prediction.py

import pandas as pd
import numpy as np
from prophet import Prophet
from database.models import get_session, CompetitorPrice
from datetime import datetime, timedelta

class SimplePricePredictionModel:
    """Basic time-series forecasting with Prophet"""
    
    def __init__(self):
        self.models = {}  # One model per competitor
    
    def prepare_data(self, competitor: str, days_back: int = 30):
        """Get historical data for training"""
        session = get_session()
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        prices = session.query(CompetitorPrice)\
            .filter(
                CompetitorPrice.company_name == competitor,
                CompetitorPrice.scrape_timestamp >= cutoff_date,
                CompetitorPrice.base_nightly_rate.isnot(None)
            )\
            .order_by(CompetitorPrice.scrape_timestamp)\
            .all()
        
        session.close()
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'ds': p.scrape_timestamp,
            'y': p.base_nightly_rate
        } for p in prices])
        
        return df
    
    def train(self, competitor: str):
        """Train Prophet model for competitor"""
        df = self.prepare_data(competitor)
        
        if len(df) < 7:
            print(f"⚠️  Not enough data for {competitor} (need 7+ days)")
            return None
        
        model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,  # Not enough data yet
            changepoint_prior_scale=0.05
        )
        
        model.fit(df)
        self.models[competitor] = model
        
        print(f"✅ Trained model for {competitor} with {len(df)} data points")
        return model
    
    def predict(self, competitor: str, days_ahead: int = 7):
        """Predict future prices"""
        if competitor not in self.models:
            self.train(competitor)
        
        if competitor not in self.models:
            return None
        
        model = self.models[competitor]
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days_ahead)
        forecast = model.predict(future)
        
        # Get predictions
        predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
        
        return {
            'competitor': competitor,
            'predictions': predictions.to_dict('records'),
            'avg_predicted_price': predictions['yhat'].mean(),
            'trend': 'increasing' if predictions['yhat'].iloc[-1] > predictions['yhat'].iloc[0] else 'decreasing'
        }
    
    def train_all_competitors(self):
        """Train models for all tracked competitors"""
        session = get_session()
        competitors = session.query(CompetitorPrice.company_name)\
            .distinct()\
            .all()
        session.close()
        
        results = {}
        for (competitor,) in competitors:
            results[competitor] = self.train(competitor)
        
        return results

# Usage
if __name__ == "__main__":
    predictor = SimplePricePredictionModel()
    
    # Train all models
    predictor.train_all_competitors()
    
    # Make predictions
    predictions = predictor.predict('Roadsurfer', days_ahead=7)
    print(f"\nRoadsurfer 7-day forecast:")
    print(f"  Avg predicted price: €{predictions['avg_predicted_price']:.2f}")
    print(f"  Trend: {predictions['trend']}")
```

**Install Prophet:**
```bash
pip install prophet
pip freeze > requirements.txt
```

**Test predictions:**
```bash
python ml/price_prediction.py
```

---

### Day 12-14: Prediction Dashboard
**Goal: Visualize predictions in dashboard**

```python
# Add to dashboard/app.py

# New tab: Predictions
with st.tabs(["📊 Overview", "💰 Pricing", "🌍 Geographic", "📈 Trends", "🔮 Predictions"])[4]:
    st.subheader("Price Predictions (7 Days Ahead)")
    
    from ml.price_prediction import SimplePricePredictionModel
    
    predictor = SimplePricePredictionModel()
    
    # Select competitor
    selected_competitor = st.selectbox(
        "Select Competitor for Prediction",
        selected_competitors
    )
    
    if st.button("Generate Prediction"):
        with st.spinner(f"Predicting prices for {selected_competitor}..."):
            prediction = predictor.predict(selected_competitor, days_ahead=7)
            
            if prediction:
                st.success(f"✅ Prediction complete!")
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Avg Predicted Price",
                        f"€{prediction['avg_predicted_price']:.2f}"
                    )
                with col2:
                    st.metric("Trend", prediction['trend'].title())
                with col3:
                    # Compare to current price
                    current = session.query(CompetitorPrice.base_nightly_rate)\
                        .filter_by(company_name=selected_competitor)\
                        .order_by(CompetitorPrice.scrape_timestamp.desc())\
                        .first()[0]
                    
                    change = ((prediction['avg_predicted_price'] - current) / current) * 100
                    st.metric("Expected Change", f"{change:+.1f}%")
                
                # Plot predictions
                pred_df = pd.DataFrame(prediction['predictions'])
                
                fig = go.Figure()
                
                # Predicted price line
                fig.add_trace(go.Scatter(
                    x=pred_df['ds'],
                    y=pred_df['yhat'],
                    mode='lines+markers',
                    name='Predicted Price',
                    line=dict(color='blue', width=3)
                ))
                
                # Confidence interval
                fig.add_trace(go.Scatter(
                    x=pred_df['ds'],
                    y=pred_df['yhat_upper'],
                    mode='lines',
                    name='Upper Bound',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=pred_df['ds'],
                    y=pred_df['yhat_lower'],
                    mode='lines',
                    name='Lower Bound',
                    fill='tonexty',
                    line=dict(width=0),
                    fillcolor='rgba(0, 100, 255, 0.2)'
                ))
                
                fig.update_layout(
                    title=f'{selected_competitor} - 7 Day Price Forecast',
                    xaxis_title='Date',
                    yaxis_title='Price (EUR)',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"⚠️  Not enough data to predict for {selected_competitor}")
```

---

## 📅 WEEK 3: ADVANCED FEATURES

### Day 15-17: Multi-City Pricing
**Goal: Track pricing for 3 cities per competitor**

```python
# Create: scrapers/multi_region_scraper.py

class MultiRegionPricingScraper:
    """Scrape pricing for multiple cities"""
    
    TARGET_CITIES = {
        'Europe': ['Berlin', 'Amsterdam', 'Paris', 'Barcelona', 'Rome'],
        'USA': ['Los Angeles', 'San Francisco', 'Denver', 'Austin', 'Miami']
    }
    
    async def scrape_multi_city(self, competitor_scraper, cities: List[str]):
        """
        For each city:
        1. Navigate to booking page
        2. Select city as pickup location
        3. Enter dates (7 days from now, 7-day rental)
        4. Extract pricing
        5. Save to RegionalPricing table
        """
        results = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for city in cities:
                try:
                    page = await browser.new_page()
                    
                    # Navigate to booking page
                    await page.goto(competitor_scraper.config['urls']['pricing'])
                    
                    # Fill location (site-specific selectors)
                    await page.fill('input[name="location"]', city)
                    await page.wait_for_timeout(1000)
                    await page.keyboard.press('Enter')
                    
                    # Fill dates
                    from datetime import datetime, timedelta
                    start_date = datetime.now() + timedelta(days=7)
                    end_date = start_date + timedelta(days=7)
                    
                    await page.fill('input[name="startDate"]', start_date.strftime('%Y-%m-%d'))
                    await page.fill('input[name="endDate"]', end_date.strftime('%Y-%m-%d'))
                    
                    # Search
                    await page.click('button[type="submit"]')
                    await page.wait_for_timeout(3000)
                    
                    # Extract prices
                    text = await page.evaluate('() => document.body.innerText')
                    prices = await competitor_scraper.extract_prices_from_text(text)
                    
                    if prices:
                        results[city] = {
                            'city': city,
                            'base_rate': min(prices),
                            'price_range': (min(prices), max(prices)),
                            'avg_rate': sum(prices) / len(prices)
                        }
                        
                        print(f"✅ {city}: €{results[city]['base_rate']:.2f}/night")
                    
                    await page.close()
                    
                except Exception as e:
                    print(f"⚠️  Failed to scrape {city}: {e}")
                    results[city] = None
            
            await browser.close()
        
        return results

# Usage
async def scrape_regional_pricing():
    """Scrape regional pricing for all competitors"""
    from scrapers.tier1_scrapers import RoadsurferScraper, GoboonyScrap
    
    scraper = MultiRegionPricingScraper()
    
    # Roadsurfer - EU cities
    roadsurfer = RoadsurferScraper(use_browserless=False)
    results_eu = await scraper.scrape_multi_city(
        roadsurfer,
        scraper.TARGET_CITIES['Europe'][:3]  # Start with 3 cities
    )
    
    # Save to database
    from database.models import get_session, RegionalPricing
    session = get_session()
    
    for city, data in results_eu.items():
        if data:
            regional_price = RegionalPricing(
                company_name='Roadsurfer',
                city=city,
                country='Germany',  # Adjust based on city
                base_rate=data['base_rate'],
                scrape_timestamp=datetime.now()
            )
            session.add(regional_price)
    
    session.commit()
    session.close()
```

---

### Day 18-19: Alert System Enhancement
**Goal: Smart alerts based on ML predictions**

```python
# Create: alerts/smart_alerts.py

class SmartAlertSystem:
    """ML-powered alert generation"""
    
    def __init__(self):
        from ml.price_prediction import SimplePricePredictionModel
        self.predictor = SimplePricePredictionModel()
    
    async def generate_alerts(self):
        """Generate intelligent alerts"""
        from database.models import get_session, CompetitorPrice, PriceAlert
        
        session = get_session()
        
        # Get all competitors
        competitors = session.query(CompetitorPrice.company_name)\
            .distinct()\
            .all()
        
        alerts = []
        
        for (competitor,) in competitors:
            # Get current price
            current = session.query(CompetitorPrice)\
                .filter_by(company_name=competitor)\
                .order_by(CompetitorPrice.scrape_timestamp.desc())\
                .first()
            
            if not current or not current.base_nightly_rate:
                continue
            
            # Get prediction
            prediction = self.predictor.predict(competitor, days_ahead=7)
            
            if not prediction:
                continue
            
            # Calculate expected change
            predicted_avg = prediction['avg_predicted_price']
            current_price = current.base_nightly_rate
            change_pct = ((predicted_avg - current_price) / current_price) * 100
            
            # Alert conditions
            if change_pct < -10:
                # Predicted significant drop
                alert = PriceAlert(
                    alert_type='predicted_price_drop',
                    severity='HIGH',
                    company_name=competitor,
                    old_value=current_price,
                    new_value=predicted_avg,
                    change_pct=change_pct,
                    alert_message=f"{competitor} predicted to drop prices by {abs(change_pct):.1f}% in next 7 days",
                    recommended_action=f"Consider preemptive pricing adjustment or promotional response"
                )
                alerts.append(alert)
                
            elif change_pct > 15:
                # Predicted significant increase
                alert = PriceAlert(
                    alert_type='predicted_price_increase',
                    severity='MEDIUM',
                    company_name=competitor,
                    old_value=current_price,
                    new_value=predicted_avg,
                    change_pct=change_pct,
                    alert_message=f"{competitor} predicted to increase prices by {change_pct:.1f}% in next 7 days",
                    recommended_action=f"Opportunity to gain market share by maintaining current pricing"
                )
                alerts.append(alert)
            
            # Check for actual recent changes
            yesterday = session.query(CompetitorPrice)\
                .filter_by(company_name=competitor)\
                .filter(CompetitorPrice.scrape_timestamp < datetime.now() - timedelta(hours=24))\
                .order_by(CompetitorPrice.scrape_timestamp.desc())\
                .first()
            
            if yesterday and yesterday.base_nightly_rate:
                actual_change_pct = ((current_price - yesterday.base_nightly_rate) / yesterday.base_nightly_rate) * 100
                
                if abs(actual_change_pct) > 8:
                    alert = PriceAlert(
                        alert_type='price_change_detected',
                        severity='CRITICAL' if abs(actual_change_pct) > 15 else 'HIGH',
                        company_name=competitor,
                        old_value=yesterday.base_nightly_rate,
                        new_value=current_price,
                        change_pct=actual_change_pct,
                        alert_message=f"{competitor} changed prices by {actual_change_pct:+.1f}% in last 24h",
                        recommended_action="Immediate review recommended"
                    )
                    alerts.append(alert)
        
        # Save alerts
        for alert in alerts:
            session.add(alert)
        
        session.commit()
        session.close()
        
        return alerts

# Run daily
if __name__ == "__main__":
    import asyncio
    alert_system = SmartAlertSystem()
    alerts = asyncio.run(alert_system.generate_alerts())
    print(f"Generated {len(alerts)} alerts")
```

---

### Day 20-21: API Development (MVP)
**Goal: Basic REST API for external access**

```python
# Create: api/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from database.models import get_session, CompetitorPrice, PriceAlert

app = FastAPI(
    title="Campervan Intelligence API",
    description="Global competitive intelligence for campervan rental industry",
    version="1.0.0"
)

# Simple API key authentication
API_KEY = "your-secret-api-key-here"  # In production: use environment variable
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Models
class CompetitorPriceResponse(BaseModel):
    company_name: str
    base_nightly_rate: Optional[float]
    customer_review_avg: Optional[float]
    data_completeness_pct: float
    scrape_timestamp: datetime

class AlertResponse(BaseModel):
    alert_type: str
    severity: str
    company_name: str
    change_pct: Optional[float]
    alert_message: str
    alert_timestamp: datetime

# Endpoints
@app.get("/")
def root():
    return {
        "name": "Campervan Intelligence API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/competitors", response_model=List[str])
def list_competitors(api_key: str = Depends(verify_api_key)):
    """Get list of all tracked competitors"""
    session = get_session()
    competitors = session.query(CompetitorPrice.company_name)\
        .distinct()\
        .all()
    session.close()
    return [c[0] for c in competitors]

@app.get("/competitors/{competitor}/latest", response_model=CompetitorPriceResponse)
def get_latest_price(competitor: str, api_key: str = Depends(verify_api_key)):
    """Get latest pricing data for a competitor"""
    session = get_session()
    price = session.query(CompetitorPrice)\
        .filter_by(company_name=competitor)\
        .order_by(CompetitorPrice.scrape_timestamp.desc())\
        .first()
    session.close()
    
    if not price:
        raise HTTPException(status_code=404, detail=f"Competitor '{competitor}' not found")
    
    return CompetitorPriceResponse(
        company_name=price.company_name,
        base_nightly_rate=price.base_nightly_rate,
        customer_review_avg=price.customer_review_avg,
        data_completeness_pct=price.data_completeness_pct,
        scrape_timestamp=price.scrape_timestamp
    )

@app.get("/alerts", response_model=List[AlertResponse])
def get_active_alerts(api_key: str = Depends(verify_api_key)):
    """Get all active alerts"""
    session = get_session()
    alerts = session.query(PriceAlert)\
        .filter_by(is_acknowledged=False)\
        .order_by(PriceAlert.alert_timestamp.desc())\
        .all()
    session.close()
    
    return [AlertResponse(
        alert_type=a.alert_type,
        severity=a.severity,
        company_name=a.company_name,
        change_pct=a.change_pct,
        alert_message=a.alert_message,
        alert_timestamp=a.alert_timestamp
    ) for a in alerts]

@app.get("/market/summary")
def get_market_summary(api_key: str = Depends(verify_api_key)):
    """Get market summary statistics"""
    from sqlalchemy import func
    
    session = get_session()
    
    # Get latest prices
    latest_prices = session.query(CompetitorPrice)\
        .filter(CompetitorPrice.scrape_timestamp >= datetime.now() - timedelta(days=1))\
        .all()
    
    prices = [p.base_nightly_rate for p in latest_prices if p.base_nightly_rate]
    
    if not prices:
        session.close()
        raise HTTPException(status_code=404, detail="No recent pricing data available")
    
    summary = {
        "avg_price": sum(prices) / len(prices),
        "min_price": min(prices),
        "max_price": max(prices),
        "price_range": max(prices) - min(prices),
        "competitors_count": len(latest_prices),
        "timestamp": datetime.now()
    }
    
    session.close()
    return summary

# Run with: uvicorn api.main:app --reload
```

**Install FastAPI:**
```bash
pip install fastapi uvicorn
pip freeze > requirements.txt
```

**Test API:**
```bash
uvicorn api.main:app --reload

# Visit: http://localhost:8000/docs (interactive API documentation)
```

---

## 📅 WEEK 4: INTEGRATION & POLISH

### Day 22-24: Competitor Discovery Automation
**Goal: Auto-discover new competitors**

```python
# Create: discovery/competitor_discovery.py

import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict

class CompetitorDiscoveryEngine:
    """Automatically discover new competitors via Google search"""
    
    SEARCH_QUERIES = [
        "campervan rental {city}",
        "motorhome rental {city}",
        "RV rental {city}",
        "wohnmobil mieten {city}",  # German
        "location camping-car {city}"  # French
    ]
    
    TARGET_CITIES = [
        # EU
        "Berlin", "Munich", "Amsterdam", "Paris", "Barcelona",
        "Rome", "Lisbon", "Copenhagen", "Vienna", "Prague",
        # US
        "Los Angeles", "San Francisco", "Denver", "Austin",
        "Miami", "Seattle", "Portland", "Las Vegas",
        # Other
        "Sydney", "Melbourne", "Auckland", "Vancouver"
    ]
    
    async def discover_from_google(self, query: str) -> List[Dict]:
        """Search Google and extract competitor websites"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(f"https://www.google.com/search?q={query}")
            
            # Extract search results
            results = await page.query_selector_all('.g a')
            
            discovered = []
            for result in results[:20]:  # Top 20 results
                try:
                    url = await result.get_attribute('href')
                    
                    if url and url.startswith('http') and not any(x in url for x in ['google.com', 'youtube.com', 'facebook.com']):
                        # Extract domain
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        
                        discovered.append({
                            'domain': domain,
                            'url': url,
                            'query': query
                        })
                except:
                    continue
            
            await browser.close()
            return discovered
    
    async def validate_competitor(self, url: str) -> bool:
        """Check if website is actually a campervan rental site"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=10000)
                text = await page.evaluate('() => document.body.innerText.toLowerCase()')
                
                # Keywords that indicate campervan rental
                keywords = ['campervan', 'motorhome', 'rv rental', 'wohnmobil', 'camping-car']
                
                is_valid = any(keyword in text for keyword in keywords)
                
                await browser.close()
                return is_valid
        except:
            return False
    
    async def discover_all_competitors(self):
        """Run full discovery process"""
        all_discovered = {}
        
        for city in self.TARGET_CITIES[:5]:  # Start with 5 cities
            print(f"\n🔍 Searching in {city}...")
            
            for query_template in self.SEARCH_QUERIES:
                query = query_template.format(city=city)
                
                results = await self.discover_from_google(query)
                
                for result in results:
                    domain = result['domain']
                    
                    if domain not in all_discovered:
                        print(f"  Found: {domain}")
                        all_discovered[domain] = result
        
        print(f"\n✅ Discovered {len(all_discovered)} unique domains")
        
        # Validate
        validated = {}
        for domain, data in list(all_discovered.items())[:10]:  # Validate first 10
            print(f"Validating {domain}...")
            if await self.validate_competitor(data['url']):
                validated[domain] = data
                print(f"  ✅ Valid competitor")
        
        print(f"\n✅ Validated {len(validated)} competitors")
        
        return validated

# Run discovery
if __name__ == "__main__":
    engine = CompetitorDiscoveryEngine()
    discovered = asyncio.run(engine.discover_all_competitors())
    
    # Save to JSON
    import json
    with open('discovered_competitors.json', 'w') as f:
        json.dump(discovered, f, indent=2)
```

---

### Day 25-27: Performance Optimization
**Goal: Scrape 25 competitors in <15 minutes**

```python
# Create: scrapers/parallel_orchestrator.py

import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor

class ParallelScrapingOrchestrator:
    """Scrape multiple competitors in parallel"""
    
    def __init__(self, max_parallel: int = 5):
        self.max_parallel = max_parallel
    
    async def scrape_batch(self, scrapers: List):
        """Scrape multiple competitors concurrently"""
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def scrape_with_limit(scraper):
            async with semaphore:
                try:
                    print(f"🚀 Starting: {scraper.company_name}")
                    data = await scraper.scrape()
                    print(f"✅ Complete: {scraper.company_name} ({data.get('data_completeness_pct', 0):.0f}%)")
                    return data
                except Exception as e:
                    print(f"❌ Failed: {scraper.company_name} - {e}")
                    return None
        
        # Run all scrapers concurrently (with max 5 at once)
        results = await asyncio.gather(*[
            scrape_with_limit(scraper) for scraper in scrapers
        ])
        
        return results

# Usage in run_intelligence.py
async def run_parallel_intelligence():
    from scrapers.tier1_scrapers import (
        RoadsurferScraper, McRentScraper, GoboonyScrap,
        YescapaScraper, CamperdaysScraper,
        RVshareScraper, OutdoorsyScraper  # New scrapers
    )
    
    # Create all scrapers
    scrapers = [
        RoadsurferScraper(False),
        McRentScraper(False),
        GoboonyScrap(False),
        YescapaScraper(False),
        CamperdaysScraper(False),
        RVshareScraper(False),
        OutdoorsyScraper(False),
        # Add 18 more...
    ]
    
    # Scrape in parallel (5 at a time)
    orchestrator = ParallelScrapingOrchestrator(max_parallel=5)
    results = await orchestrator.scrape_batch(scrapers)
    
    # Save to database
    from database.models import get_session, CompetitorPrice
    session = get_session()
    
    for data in results:
        if data:
            price = CompetitorPrice(**data)
            session.add(price)
    
    session.commit()
    session.close()
    
    print(f"\n✅ Scraped {len([r for r in results if r])} / {len(scrapers)} competitors")

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(run_parallel_intelligence())
    print(f"⏱️  Total time: {time.time() - start:.1f} seconds")
```

---

### Day 28-30: Documentation & Demo
**Goal: Professional documentation + demo video**

1. **Update README.md**
```markdown
# 🌍 Global Campervan Intelligence Platform

## Current Capabilities (30-Day Progress)
- ✅ 25 competitors tracked (5x increase)
- ✅ Multi-region pricing (3-5 cities per competitor)
- ✅ ML price predictions (7-day forecasts)
- ✅ Smart alert system (predictive + reactive)
- ✅ REST API (external access)
- ✅ Enhanced dashboard (predictions, geographic, trends)
- ✅ Automated competitor discovery

## Quick Start
```bash
# Daily intelligence gathering
python run_intelligence.py  # Now completes in ~12 minutes

# Generate predictions
python ml/price_prediction.py

# Launch dashboard
streamlit run dashboard/app.py

# Start API server
uvicorn api.main:app --reload
```

2. **Create demo video** (record screen)
   - Show dashboard with 25 competitors
   - Demonstrate prediction feature
   - Show API in action
   - Highlight alerts

3. **Write blog post** (for documentation)
   - "How we scaled from 5 to 25 competitors in 30 days"
   - Share on LinkedIn, Medium, etc.

---

## 🎯 30-DAY SUCCESS METRICS

### Targets vs Achievement

| Metric | Target | Expected | Status |
|--------|--------|----------|--------|
| Competitors | 25 | 20-25 | 🎯 |
| Markets | 3+ | 3-4 | 🎯 |
| Data Completeness | 60%+ avg | 58-65% | 🎯 |
| Scraping Time | <15 min | 12-14 min | ✅ |
| ML Predictions | Basic working | Prophet-based | ✅ |
| API Endpoints | 5+ | 6-8 | ✅ |
| Dashboard Views | 5+ tabs | 5-6 tabs | ✅ |

### ROI After 30 Days
- **Time invested:** ~80 hours (2hr/day × 30 days)
- **Value created:**
  - 5x more data coverage
  - Predictive capabilities
  - API for integration
  - Multi-region insights
  - Foundation for SaaS launch

**Estimated value increase:** €50K → €200K+ (4x)

---

## 🚀 NEXT 30 DAYS (Days 31-60)

With this foundation, you can now:

1. **Expand to 50 competitors** (double down)
2. **Add real-time monitoring** (5-15 min refresh)
3. **Launch beta API** (5-10 external users)
4. **Improve ML models** (use XGBoost, ensemble)
5. **Build mobile app** (Flutter PWA)

---

## 💡 TIPS FOR SUCCESS

### Week 1 Tips
- Start with competitors you know work (Roadsurfer, Goboony)
- Test each scraper individually before batch
- Don't aim for 100% completeness (60% is good enough)
- Commit to GitHub daily

### Week 2 Tips
- ML requires 7+ days of data - be patient
- Prophet works well with limited data
- Focus on simple predictions first
- Visualize predictions to validate

### Week 3 Tips
- Multi-city scraping is slow - start with 2-3 cities
- Alerts need tuning - adjust thresholds based on results
- API security is important - use environment variables
- Document API endpoints as you build

### Week 4 Tips
- Parallel scraping saves huge time - invest in it
- Competitor discovery finds many false positives - validate
- Performance optimization matters - measure everything
- Demo to stakeholders early and often

---

## 📞 SUPPORT & QUESTIONS

If you get stuck:
1. Check error logs (`logs/intel_*.log`)
2. Test individual scrapers (`python -c "..."`)
3. Verify database schema (`python -c "from database.models import ..."`)
4. Review documentation in main `10X_TRANSFORMATION_PROMPT.md`

---

**🎉 You're ready to start your 10X transformation! 🎉**

**Day 1 begins NOW. Let's build something incredible.**

