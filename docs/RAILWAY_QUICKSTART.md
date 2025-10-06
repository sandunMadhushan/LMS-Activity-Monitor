# Quick Start: Deploy to Railway

## Prerequisites
- GitHub account
- LMS-Activity-Monitor repository pushed to GitHub
- Gmail App Password for notifications

---

## 5-Minute Deployment

### 1. Open Railway
Go to: **https://railway.app**

### 2. Sign In with GitHub
Click **"Login"** → **"Login with GitHub"**

### 3. Create New Project
- Click **"New Project"**
- Select **"Deploy from GitHub repo"**
- Choose **`LMS-Activity-Monitor`** repository
- Click **"Deploy Now"**

Railway will automatically:
- ✅ Detect Python project
- ✅ Install dependencies from `requirements.txt`
- ✅ Start app using `Procfile`

### 4. Add Environment Variables

Click on your project → **Variables** tab:

```bash
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_RECIPIENTS=recipient1@example.com
SECRET_KEY=random-secret-key-123
NTFY_TOPIC=your-unique-topic-name
NTFY_SERVER=https://ntfy.sh
```

Click **"Add"** after each variable.

### 5. Generate Public URL

- Click **Settings** tab
- Under **Networking** → Click **"Generate Domain"**
- Copy your URL: `https://your-app.up.railway.app`

### 6. Verify Deployment

Visit your Railway URL and check:
- ✅ Dashboard loads
- ✅ Statistics show
- ✅ Scan button is disabled (correct - GitHub Actions handles this)
- ✅ Test Email button works
- ✅ Test Mobile button works

---

## Done! 🎉

You now have **TWO deployments**:
1. **Render** (Primary): `https://lms-activity-monitor.onrender.com`
2. **Railway** (Backup): `https://your-app.up.railway.app`

Both use the same database from GitHub!

---

## Auto-Deploy on Push

Every time you `git push`, Railway automatically redeploys:

```bash
git add .
git commit -m "your changes"
git push
```

Railway detects the push → Builds → Deploys (takes ~2 minutes)

---

## Troubleshooting

### Check Logs
Railway Dashboard → Your Service → **Deployments** → Latest → **View Logs**

### Port Issues
Railway sets `PORT` automatically. Our app detects it:
```python
port = int(os.getenv('PORT', 5000))
```

### App Sleeping
Railway free tier doesn't sleep like Render! It stays active.

---

## Next Steps

1. Update README with Railway URL
2. Test both deployments
3. Use whichever loads faster!
