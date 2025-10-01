# 🔄 How GitHub Actions and Render Work Together

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (Free)                        │
│                  github.com/sandunMadhushan                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📅 Schedule: Twice Daily (1 AM & 1 PM UTC)                    │
│                                                                 │
│  1. Install Python, Chrome, ChromeDriver                       │
│  2. Run: python scraper.py --headless True                     │
│  3. Scrapes:                                                   │
│     • OUSL Moodle → Courses, Activities, Deadlines            │
│     • RUSL Moodle → Courses, Activities, Deadlines            │
│  4. Save to: lms_data.db                                       │
│  5. Commit lms_data.db back to GitHub repo ✅                  │
│                                                                 │
│  💾 Result: Database stored in GitHub repository              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Auto-deploy on push
                         │ (or manual redeploy)
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RENDER (Free Tier)                           │
│                lms-activity-monitor.onrender.com                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔨 Build Phase:                                               │
│     1. pip install -r requirements.txt                         │
│     2. Download lms_data.db from GitHub repo 📥                │
│                                                                 │
│  🚀 Runtime:                                                   │
│     • Flask app (app.py) runs with gunicorn                    │
│     • Reads from lms_data.db                                   │
│     • Serves web dashboard on port 10000                       │
│                                                                 │
│  🌐 Public Access:                                             │
│     https://lms-activity-monitor.onrender.com/                 │
│                                                                 │
│  ⚠️  Note: Free tier sleeps after 15 min inactivity           │
│     First request takes ~30 seconds to wake up                 │
└─────────────────────────────────────────────────────────────────┘
                         │
                         │ HTTP requests
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                         USERS                                   │
│                                                                 │
│  🌐 Access dashboard from anywhere via web browser             │
│  📊 View courses, deadlines, activities                         │
│  🔍 Filter by university (OUSL/RUSL)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

```
MOODLE SITES                    GITHUB                    RENDER WEB
────────────                    ──────                    ──────────

┌─────────┐                                              
│  OUSL   │                                              
│ Moodle  │                                              
└────┬────┘                                              
     │                                                   
     │ Scrape                                            
     │                                                   
┌────▼────┐                                              
│  RUSL   │                                              
│ Moodle  │                                              
└────┬────┘                                              
     │                                                   
     │                                                   
     ▼                                                   
┌─────────────┐        Push           ┌──────────────┐  
│   GitHub    │◄──────────────────────┤ lms_data.db  │  
│   Actions   │                       └──────────────┘  
│             │                                          
│ (Scraper)   │                                          
└─────┬───────┘                                          
      │                                                  
      │ Commit                                           
      │                                                  
      ▼                                                  
┌─────────────┐        Download       ┌──────────────┐  
│   GitHub    ├──────────────────────►│    Render    │  
│   Repo      │   on build/deploy     │  Web Server  │  
│             │                       │              │  
│ (Database)  │                       │  (Dashboard) │  
└─────────────┘                       └──────┬───────┘  
                                             │          
                                             │ Serve    
                                             │          
                                             ▼          
                                      ┌──────────────┐  
                                      │    Users     │  
                                      │  (Browser)   │  
                                      └──────────────┘  
```

---

## 🔄 Update Cycle

### When Data Gets Updated:

1. **GitHub Actions runs** (twice daily)
   - Scrapes fresh data
   - Updates `lms_data.db`
   - Commits to GitHub repo

2. **Render redeploys** (triggered by push)
   - Downloads latest `lms_data.db`
   - Restarts Flask app with new data
   - Users see updated dashboard

### Timeline Example:

```
Time         | GitHub Actions            | Render Dashboard
─────────────┼──────────────────────────┼─────────────────────────
1:00 AM UTC  | ✅ Scrape runs           | Shows old data
1:05 AM UTC  | Commits to repo          | Auto-redeploy triggered
1:08 AM UTC  | -                        | ✅ Shows NEW data
...
1:00 PM UTC  | ✅ Scrape runs           | Shows old data
1:05 PM UTC  | Commits to repo          | Auto-redeploy triggered
1:08 PM UTC  | -                        | ✅ Shows NEW data
```

---

## 🆚 Previous vs Current Setup

### ❌ Previous Setup (Both Running Separately)

```
GitHub Actions → Scrapes → Saves to GitHub repo
                              ↓
                         (NOT CONNECTED)
                              ↓
Render Cron Job → Scrapes → Saves to Render (ephemeral storage)
                              ↓
                         ⚠️ Data lost on restart!
```

**Problem:** 
- Double scraping (waste of resources)
- Render database resets on every restart
- Dashboard shows no data

---

### ✅ Current Setup (Integrated)

```
GitHub Actions → Scrapes → Commits to repo
                              ↓
                         (CONNECTED)
                              ↓
Render Dashboard → Downloads DB from repo → Displays data
```

**Benefits:**
- ✅ Single source of truth (GitHub repo)
- ✅ Database version controlled
- ✅ No scraping on Render (avoids ChromeDriver issues)
- ✅ Completely FREE
- ✅ Data persists

---

## 💰 Cost Breakdown

| Component | Service | Cost | Why Free? |
|-----------|---------|------|-----------|
| Scraping | GitHub Actions | **FREE** | 2,000 minutes/month free tier |
| Database Storage | GitHub Repo | **FREE** | Included in free repos |
| Web Hosting | Render | **FREE** | Free tier (with sleep) |
| **TOTAL** | - | **$0/month** 🎉 | All services on free tiers |

---

## ⚙️ Configuration Files

### 1. `.github/workflows/monitor.yml` (GitHub Actions)
```yaml
# Runs twice daily
# Scrapes OUSL & RUSL
# Commits lms_data.db to repo
```

### 2. `render.yaml` (Render)
```yaml
# Downloads lms_data.db from GitHub
# Runs Flask dashboard
# No scraping (removed Cron Job)
```

### 3. `app.py` (Flask Application)
```python
# Reads from lms_data.db
# Serves web dashboard
# No scraping (view only)
```

---

## 🔍 How to Verify It's Working

### Check GitHub Actions:
1. Go to: https://github.com/sandunMadhushan/LMS-Activity-Monitor/actions
2. Look for "LMS Activity Monitor" workflow
3. Should run twice daily (1 AM & 1 PM UTC)
4. Check if `lms_data.db` is committed to repo

### Check Render:
1. Go to: https://dashboard.render.com/
2. Find "LMS-Activity-Monitor" web service
3. Check deployment logs for: `Downloading lms_data.db`
4. Visit: https://lms-activity-monitor.onrender.com/

### Check Database in Repo:
1. Go to: https://github.com/sandunMadhushan/LMS-Activity-Monitor
2. Look for `lms_data.db` file in root
3. Check commit history for database updates

---

## 🚀 Deployment Process

### When You Push Code:

```
1. Push to GitHub
   ↓
2. Render detects changes
   ↓
3. Render builds:
   - Installs dependencies
   - Downloads latest lms_data.db
   ↓
4. Render deploys:
   - Starts Flask app
   - Dashboard live with new data
```

---

## 🛠️ Manual Redeploy (if needed)

If you want to update the dashboard without code changes:

1. Go to Render Dashboard
2. Select "LMS-Activity-Monitor" service
3. Click "Manual Deploy" → "Deploy latest commit"
4. Render will download the latest database from GitHub

---

## 📝 Summary

**Q: Are they interconnected?**
**A:** Yes! Now they are:
- GitHub Actions scrapes and stores in repo
- Render downloads from repo and displays
- Connected via GitHub repository

**Q: Does Render work solely?**
**A:** 
- Render only hosts the **dashboard** (Flask app)
- It does **NOT scrape** anymore (we removed Cron Job)
- It **displays data** from GitHub's database

**Q: How does the website update?**
**A:**
- GitHub Actions scrapes twice daily
- Commits new database to repo
- Render auto-redeploys (or manual redeploy)
- Website shows fresh data

---

## 🎯 Benefits of This Setup

1. ✅ **Free**: No costs at all
2. ✅ **Reliable**: GitHub Actions runs consistently
3. ✅ **Simple**: No Chrome setup on Render
4. ✅ **Backed up**: Database in version control
5. ✅ **Accessible**: Public web dashboard
6. ✅ **Maintainable**: Easy to debug and update

---

## 🔄 Alternative: If You Want Real-time Updates

If you need the dashboard to always show the absolute latest data without redeploying:

**Option 1:** Add a "Sync" button in the dashboard that downloads latest DB
**Option 2:** Use PostgreSQL instead of SQLite (shared database)
**Option 3:** Use Render's paid plan for persistent storage + Cron Job

But for most use cases, the current setup (updates twice daily) is perfect! 🎉
