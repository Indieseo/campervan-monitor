# Prompt for Claude Code - Dashboard Improvements

**Task:** Enhance the Streamlit Dashboard  
**Priority:** MEDIUM  
**Estimated Time:** 2-4 hours  
**No conflicts with scraper work**

---

## 🎯 OBJECTIVE

Improve the campervan intelligence dashboard to make it more user-friendly, visually appealing, and informative. This task is completely separate from the scraper improvements and won't cause any conflicts.

---

## 📁 FILES TO WORK WITH

### Main File
- **`dashboard/app.py`** - Streamlit dashboard application

### Reference Files (Read Only)
- **`database/models.py`** - Database schema
- **`data/daily_summaries/intelligence_2025-10-12.json`** - Sample data
- **`exports/`** - Example export files

---

## 🎨 ENHANCEMENT TASKS

### 1. Visual Improvements (Priority: HIGH)

**Current Issues:**
- Basic Streamlit styling
- No custom theming
- Charts could be more attractive
- No company logos

**Improvements to Make:**
- Add custom CSS styling
- Implement a professional color scheme (blues/greens for campervan theme)
- Add company icons/logos if available
- Improve chart aesthetics (colors, labels, tooltips)
- Add loading animations
- Responsive layout for mobile

**Example:**
```python
# Add custom CSS
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stMetric { 
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
```

---

### 2. Add More Visualizations (Priority: HIGH)

**Current State:**
- Basic price charts
- Simple metrics
- Limited comparisons

**Add These Charts:**
1. **Market Position Matrix**
   - X-axis: Price
   - Y-axis: Review Rating
   - Size: Fleet Size
   - Show competitive positioning

2. **Price Trend Line Chart**
   - Show price changes over time (if historical data exists)
   - Compare multiple competitors
   - Highlight seasonal patterns

3. **Completeness Dashboard**
   - Visual indicator of data quality per competitor
   - Show which fields are missing
   - Traffic light system (red/yellow/green)

4. **Geographic Coverage Map**
   - If location data available
   - Show where each competitor operates
   - Interactive map with plotly or folium

5. **Feature Comparison Table**
   - Compare vehicle types
   - Compare policies (cancellation, fuel, mileage)
   - Side-by-side view

---

### 3. Add Filtering & Interactivity (Priority: MEDIUM)

**Add These Features:**

1. **Date Range Selector**
   ```python
   date_range = st.date_input("Select Date Range", [start_date, end_date])
   ```

2. **Competitor Multi-Select**
   ```python
   selected_competitors = st.multiselect(
       "Select Competitors to Compare",
       options=all_competitors,
       default=top_5
   )
   ```

3. **Price Range Slider**
   ```python
   price_range = st.slider("Price Range (€/night)", 0, 500, (50, 200))
   ```

4. **Sort Options**
   - Sort by price (low to high / high to low)
   - Sort by rating
   - Sort by completeness
   - Sort by fleet size

---

### 4. Export Enhancements (Priority: LOW)

**Current State:**
- Basic export functionality

**Improvements:**
1. **Export Options in Sidebar**
   - PDF report button
   - Excel export button
   - CSV export button
   - JSON export button

2. **Custom Report Builder**
   - Let user select which metrics to include
   - Choose date range
   - Select competitors
   - Generate custom report

3. **Email Report Feature** (if time permits)
   - Schedule daily/weekly reports
   - Send to email address
   - Automated delivery

---

### 5. Performance Metrics Section (Priority: MEDIUM)

**Add a New Tab/Section:**

```python
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Pricing", "Performance", "Settings"])

with tab3:
    st.header("Scraper Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Scrapers Running", "5/5", "100%")
    with col2:
        st.metric("Avg Completeness", "23.9%", "-2.1%")
    with col3:
        st.metric("Last Run", "2 hours ago", "")
    
    # Show scraper health for each competitor
    for competitor in competitors:
        st.write(f"**{competitor.name}**")
        progress_bar = st.progress(competitor.completeness / 100)
        st.caption(f"{competitor.completeness}% complete")
```

---

### 6. Add Insights & Recommendations (Priority: LOW)

**Add AI-Generated Insights:**

```python
st.subheader("📊 Key Insights")

insights = [
    f"💰 **Roadsurfer** is {percent_diff}% cheaper than the market average",
    f"⭐ **Goboony** has the highest customer rating at {rating} stars",
    f"📍 **Roadsurfer** offers the most locations ({count})",
    f"⚠️ **McRent** data quality needs improvement ({completeness}% complete)"
]

for insight in insights:
    st.info(insight)
```

---

## 📋 REQUIREMENTS & CONSTRAINTS

### Must Keep
- ✅ All existing functionality
- ✅ Database connections
- ✅ Export features
- ✅ Current data models

### Don't Modify
- ❌ `database/models.py`
- ❌ Scraper files (`scrapers/`)
- ❌ Core configuration (`core_config.py`)

### Can Modify
- ✅ `dashboard/app.py` - Main focus
- ✅ Add new files in `dashboard/` folder
- ✅ Add custom CSS files
- ✅ Add assets (logos, images)

---

## 🧪 TESTING

### How to Test
```powershell
# Run dashboard
streamlit run dashboard\app.py

# Open browser to http://localhost:8501
# Test all features interactively
```

### What to Check
- [ ] All pages load without errors
- [ ] Charts render correctly
- [ ] Filters work as expected
- [ ] Export buttons functional
- [ ] Responsive on mobile (resize browser window)
- [ ] No console errors (F12 DevTools)

---

## 📚 HELPFUL RESOURCES

### Streamlit Documentation
- **Charts:** https://docs.streamlit.io/library/api-reference/charts
- **Widgets:** https://docs.streamlit.io/library/api-reference/widgets
- **Layout:** https://docs.streamlit.io/library/api-reference/layout
- **Theming:** https://docs.streamlit.io/library/advanced-features/theming

### Plotly Documentation
- **Getting Started:** https://plotly.com/python/getting-started/
- **Chart Types:** https://plotly.com/python/

### Color Schemes
- Use **Material Design** colors for professional look
- Primary: #1976D2 (blue)
- Secondary: #43A047 (green)
- Accent: #FF6F00 (orange)
- Background: #F5F5F5 (light gray)

---

## 💡 IMPLEMENTATION TIPS

### 1. Start with Quick Wins
- Add custom CSS first (immediate visual improvement)
- Add metrics cards
- Improve existing charts

### 2. Then Add New Features
- New chart types
- Filtering
- Interactivity

### 3. Test Frequently
- Streamlit has hot reloading
- Save file and see changes immediately
- Test with real database data

### 4. Keep It Simple
- Don't over-complicate
- User experience > feature count
- Fast loading > fancy animations

---

## 📊 SUCCESS CRITERIA

### Must Have
- ✅ Custom styling (CSS)
- ✅ At least 2 new chart types
- ✅ Filtering functionality
- ✅ Improved metrics display
- ✅ No errors on load

### Nice to Have
- ⭐ Mobile responsive
- ⭐ Export improvements
- ⭐ Automated insights
- ⭐ Performance metrics section

---

## 🚀 GETTING STARTED

### Step 1: Read Current Dashboard
```powershell
# Open and review
code dashboard\app.py
```

### Step 2: Set Up Test Environment
```powershell
# Ensure dependencies installed
pip install streamlit plotly pandas

# Run dashboard
streamlit run dashboard\app.py
```

### Step 3: Make Incremental Changes
- Start with CSS
- Test after each change
- Commit working changes
- Build features incrementally

### Step 4: Document Changes
- Add comments to new code
- Update docstrings
- Create DASHBOARD_IMPROVEMENTS.md summary

---

## 📝 DELIVERABLES

1. **Enhanced `dashboard/app.py`**
   - Custom styling
   - New visualizations
   - Better interactivity

2. **Optional: `dashboard/custom.css`**
   - Separated styling file

3. **Optional: `dashboard/utils.py`**
   - Helper functions for charts/metrics

4. **Documentation: `DASHBOARD_IMPROVEMENTS.md`**
   - Summary of changes
   - Screenshots (if possible)
   - Usage instructions

---

## ⚠️ IMPORTANT NOTES

1. **Database Schema**: Don't change it, but understand it
   - `CompetitorPrice` model has 35+ fields
   - Check `database/models.py` for field names
   - Use existing fields for charts

2. **Sample Data**: Available in multiple formats
   - Database: `database/campervan_intelligence.db`
   - JSON: `data/daily_summaries/intelligence_2025-10-12.json`
   - Exports: `exports/` folder

3. **Browser Testing**: Test in
   - Chrome/Edge
   - Firefox
   - Mobile view (resize window)

4. **Performance**: Keep it fast
   - Cache data with `@st.cache_data`
   - Lazy load heavy charts
   - Optimize queries

---

**Happy coding! This is a fun creative task with lots of room for improvement.** 🎨📊

**Estimated Time:** 2-4 hours  
**Difficulty:** Medium  
**Fun Factor:** High ⭐⭐⭐⭐⭐


