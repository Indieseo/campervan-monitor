# 🚐 QUICK START - Campervan Monitor

**Copy this for instant context in new chats:**

---

## 📍 Status: 70% Complete

**Location:** `C:\Projects\campervan-monitor\`  
**What Works:** ✅ Roadsurfer (10 prices), Database, Infrastructure  
**What's Broken:** ❌ Cruise America (0 prices), Apollo (0 prices)

---

## 🚀 Next Commands (30 min to finish)

```powershell
cd C:\Projects\campervan-monitor
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING='utf-8'

# 1. Check status (1 min)
python check_database.py

# 2. Fix 2 scrapers (5 min)
python test_fixed_scrapers.py

# 3. Test 12 companies (10 min)
python test_static_scrapers.py

# 4. Launch dashboard (1 min)
streamlit run dashboard\app.py
```

**Dashboard:** http://localhost:8501

---

## 🔑 Quick Facts

- **API Key:** `2TCc50QWZiy4pBP861f1918aafa2f44e82c5b138727723ec2`
- **Region:** production-sfo
- **Companies Configured:** 30 total (1 working, 2 need fixes, 12 ready to test)
- **Database:** SQLite at `database\campervan_prices.db`
- **Strategy:** Static pricing easiest → Booking forms → Complex engines

---

## 📋 Ask Claude To:

"Complete the Campervan Monitor project by running the 4 commands above. Debug any failures and get 7-10 companies scraped with 30-50 total prices showing in the dashboard."

---

**Full details in:** `CONTINUATION_PROMPT.md`
