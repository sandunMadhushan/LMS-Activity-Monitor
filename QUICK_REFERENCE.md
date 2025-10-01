# LMS Activity Monitor - Quick Reference

## 🚀 Quick Commands

### First Time Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Then edit .env with your credentials
```

### Running the System

```bash
# Run a scan with visible browser (for testing)
python scraper.py --headless False

# Run a headless scan (production)
python scraper.py

# Send test email
python scraper.py --test-email

# Start web dashboard
python app.py
# Then visit: http://localhost:5000
```

### Quick Start Scripts

**Windows:**

```bash
start.bat
```

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

## 🔑 Required Environment Variables

Create a `.env` file with:

```env
# OUSL Credentials
OUSL_USERNAME=your_username
OUSL_PASSWORD=your_password

# Rajarata Credentials
RUSL_USERNAME=your_username
RUSL_PASSWORD=your_password

# Email Settings
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=notifications@email.com

# SMTP (usually don't need to change)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 📧 Gmail App Password Setup

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Click **App passwords**
4. Select **Mail** → **Other** → Name it "LMS Monitor"
5. Copy the 16-character password
6. Paste in `.env` as `EMAIL_PASSWORD`

## 🤖 GitHub Actions Setup

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Add Secrets

Go to: **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

- `OUSL_USERNAME`
- `OUSL_PASSWORD`
- `RUSL_USERNAME`
- `RUSL_PASSWORD`
- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `EMAIL_RECIPIENT`

### 3. Run Workflow

Go to **Actions** tab → **LMS Monitor** → **Run workflow**

## 🕐 Schedule Times

Default: 9 AM and 9 PM UTC

To adjust for your timezone, edit `.github/workflows/monitor.yml`:

```yaml
schedule:
  - cron: "0 3 * * *" # 9 AM Sri Lanka Time (UTC+6)
  - cron: "0 15 * * *" # 9 PM Sri Lanka Time (UTC+6)
```

Use https://crontab.guru/ for help

## 📊 Web Dashboard Routes

| URL                 | Description               |
| ------------------- | ------------------------- |
| `/`                 | Main dashboard with stats |
| `/courses`          | All enrolled courses      |
| `/courses?lms=OUSL` | Filter by OUSL            |
| `/courses?lms=RUSL` | Filter by RUSL            |
| `/course/<id>`      | View single course        |
| `/activities`       | All activities timeline   |

## 🗄️ Database Schema

### Tables

- **courses**: All enrolled courses
- **activities**: All course activities
- **scan_history**: Scan logs
- **notifications**: Notification logs

### Important Queries

```sql
-- Get new activities
SELECT * FROM activities WHERE is_new = 1;

-- Get courses from OUSL
SELECT * FROM courses WHERE lms_name = 'OUSL';

-- Get recent scans
SELECT * FROM scan_history ORDER BY scan_time DESC LIMIT 10;
```

## 🎨 Activity Types Monitored

| Type       | Icon | Description    |
| ---------- | ---- | -------------- |
| `assign`   | 📄   | Assignments    |
| `quiz`     | ❓   | Quizzes/Tests  |
| `resource` | 📁   | Files/PDFs     |
| `forum`    | 💬   | Discussions    |
| `url`      | 🔗   | External links |
| `page`     | 📃   | Course pages   |
| `label`    | 🏷️   | Section labels |
| `book`     | 📖   | Course books   |

## 🔧 Troubleshooting Quick Fixes

### Login Failed

```bash
# Test with visible browser
python scraper.py --headless False
# Watch what happens
```

### Email Not Sending

```bash
# Test email configuration
python scraper.py --test-email
```

### Reset Database

```bash
# Delete and restart
rm lms_data.db
python scraper.py
```

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Clear Chrome Cache

```python
# In scraper.py, add to chrome_options:
chrome_options.add_argument('--disable-cache')
```

## 📱 Access from Mobile

### Local Network

1. Find your IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
2. Run: `python app.py`
3. Access from phone: `http://YOUR_IP:5000`

### Public Access (ngrok)

```bash
# Install ngrok
npm install -g ngrok

# Run app
python app.py

# In another terminal
ngrok http 5000

# Use the ngrok URL from your phone
```

## 🎯 Common Customizations

### Change Email Subject

Edit `notifier.py`, line with:

```python
msg['Subject'] = f'🔔 Your Custom Subject: {len(activities)} New'
```

### Add More LMS Instances

1. Copy `scrape_ousl()` method in `scraper.py`
2. Modify for new LMS
3. Add credentials to `.env`
4. Call in `run_full_scan()`

### Filter Specific Courses

In `scraper.py`, add after finding courses:

```python
if 'UNWANTED COURSE' in course_name:
    continue
```

### Change Notification Format

Edit `_create_html_email()` in `notifier.py`

## 📈 Performance Tips

### Faster Scans

- Reduce `time.sleep()` values
- Disable images: `chrome_options.add_argument('--blink-settings=imagesEnabled=false')`
- Use headless mode

### Lower Memory Usage

- Close driver between scans
- Limit database query results
- Clear old notifications

### Reduce Email Size

- Truncate descriptions
- Limit activity count per email
- Remove images from HTML

## 🔒 Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] GitHub Secrets configured
- [ ] Gmail App Password used (not main password)
- [ ] 2FA enabled on Moodle accounts
- [ ] Regular dependency updates
- [ ] Database backed up
- [ ] Credentials rotated periodically

## 📞 Need Help?

1. **Documentation**: Check `SETUP_GUIDE.md` and `PROJECT_OVERVIEW.md`
2. **Logs**: Look at console output or GitHub Actions logs
3. **Issues**: Create a GitHub issue with error details
4. **Email Test**: Always test with `--test-email` first

## 🎓 Best Practices

1. **First Run**: Everything will be "new" - that's normal
2. **Frequency**: Twice daily is optimal (not too spammy)
3. **Backup**: Save `lms_data.db` regularly
4. **Updates**: Pull latest code periodically
5. **Testing**: Use `--headless False` when debugging
6. **Monitoring**: Check GitHub Actions status weekly

---

**Quick Links:**

- [Setup Guide](SETUP_GUIDE.md)
- [Full Overview](PROJECT_OVERVIEW.md)
- [GitHub Issues](../../issues)

_Keep learning! 🚀_
