# Railway.app Deployment Guide

## Why Railway?

Railway is similar to Render but often more reliable:
- ✅ Free tier with 500 hours/month
- ✅ Supports Python + Flask
- ✅ Easy GitHub integration
- ✅ Faster cold starts than Render
- ✅ Better uptime

---

## Deployment Steps

### 1. Sign Up for Railway

1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign in with GitHub

### 2. Deploy from GitHub

1. **Connect Repository**:
   - Click "Deploy from GitHub repo"
   - Select your `LMS-Activity-Monitor` repository
   - Click "Deploy Now"

2. **Railway Auto-Detects**:
   - Python runtime
   - Installs from `requirements.txt`
   - Uses `Procfile` for start command

### 3. Configure Environment Variables

Click on your project → **Variables** tab → Add these:

```bash
# Email Configuration
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_RECIPIENTS=recipient@example.com

# Secret Key
SECRET_KEY=random-secret-key-here

# Mobile Notifications (Optional)
NTFY_TOPIC=your-unique-topic-name
NTFY_SERVER=https://ntfy.sh

# Calendar (Optional)
CALENDAR_CREDENTIALS_FILE=credentials.json
CALENDAR_TOKEN_FILE=token.json

# Railway Detection (Auto-set)
PORT=${{PORT}}
```

**Important**: Railway automatically provides the `PORT` variable.

### 4. Enable Public Domain

1. Go to **Settings** tab
2. Under "Networking" → Click "Generate Domain"
3. You'll get a URL like: `https://your-app.up.railway.app`

### 5. Disable Scanning (Important!)

Railway (like Render) doesn't support Chrome/Selenium, so:

1. The scan button will be **disabled automatically** (app detects Railway)
2. All scanning happens via **GitHub Actions** (twice daily)
3. Railway only serves the web dashboard

---

## Verification

After deployment:

1. ✅ Visit your Railway URL: `https://your-app.up.railway.app`
2. ✅ Check dashboard loads
3. ✅ Verify scan button is disabled
4. ✅ Test "Test Email" button
5. ✅ Test "Test Mobile" button (if configured)
6. ✅ Check calendar sync works

---

## Cost & Limits

**Free Tier:**
- 500 execution hours/month
- $5 credit/month
- Enough for 24/7 operation

**After Free Tier:**
- ~$5/month for small apps
- Pay-as-you-go pricing

---

## Updating Your App

Railway auto-deploys on every GitHub push:

1. Make changes locally
2. `git add .`
3. `git commit -m "update"`
4. `git push`
5. Railway detects push and redeploys automatically

---

## Troubleshooting

### App Not Starting

**Check Logs:**
1. Go to Railway dashboard
2. Click on your service
3. View "Deployments" → Click latest → "View Logs"

### Port Issues

Railway uses dynamic ports. Our app automatically detects:
```python
port = int(os.getenv('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### Database Not Found

The SQLite database (`lms_data.db`) is in your GitHub repo, so it should work automatically.

---

## Comparison: Railway vs Render

| Feature | Railway | Render |
|---------|---------|--------|
| Free Tier | 500 hrs/month | 750 hrs/month |
| Cold Starts | Faster ⚡ | Slower 🐢 |
| Uptime | Better ✅ | Sometimes slow |
| Setup | Easier 🎯 | Easy |
| Auto-Deploy | Yes | Yes |
| Custom Domain | Yes (paid) | Yes (paid) |

---

## Important Notes

1. **GitHub Actions Still Required**: Railway only hosts the web dashboard. All LMS scanning happens via GitHub Actions (9 AM & 9 PM SLT).

2. **Database Updates**: The database in Railway won't update automatically. GitHub Actions commits the updated database to your repo, and Railway will use the latest version on the next deployment.

3. **Two Deployments Strategy**:
   - **Render**: Primary deployment
   - **Railway**: Backup when Render is slow
   - Both use the same database from GitHub

---

## Next Steps

After deploying to Railway:

1. ✅ Add Railway URL to README
2. ✅ Update `notifier.py` Click URLs to point to Railway
3. ✅ Test all functionality
4. ✅ Keep both Render and Railway running

---

**You now have TWO live deployments! 🎉**
- Render: `https://lms-activity-monitor.onrender.com`
- Railway: `https://your-app.up.railway.app`
