# LMS Activity Monitor - Setup Guide

This guide will help you set up the LMS Activity Monitor system step by step.

## Prerequisites

- Python 3.9 or higher
- Git
- Gmail account (for notifications)
- GitHub account (for automated scanning)

## Step 1: Local Setup

### 1.1 Install Python Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:

   **For OUSL (Open University):**

   - `OUSL_USERNAME`: Your OUSL username
   - `OUSL_PASSWORD`: Your OUSL password

   **For RUSL (Rajarata University):**

   - `RUSL_USERNAME`: Your Rajarata username
   - `RUSL_PASSWORD`: Your Rajarata password

   **For Email Notifications:**

   - `EMAIL_SENDER`: Your Gmail address
   - `EMAIL_PASSWORD`: Gmail App Password (see Step 2)
   - `EMAIL_RECIPIENT`: Email where you want to receive notifications

### 1.3 Test the System

Run a test scan:

```bash
python scraper.py --headless False
```

This will open a browser window so you can see what's happening.

## Step 2: Gmail Setup

To send email notifications, you need a Gmail App Password:

1. Go to your Google Account: https://myaccount.google.com/
2. Select **Security** from the left menu
3. Enable **2-Step Verification** (if not already enabled)
4. Under "Signing in to Google", select **App passwords**
5. Select app: **Mail**
6. Select device: **Other (Custom name)** → Enter "LMS Monitor"
7. Click **Generate**
8. Copy the 16-character password
9. Paste it in your `.env` file as `EMAIL_PASSWORD`

## Step 3: Test Email Notifications

```bash
python scraper.py --test-email
```

You should receive a test email within a few seconds.

## Step 4: GitHub Actions Setup (Automated Scanning)

### 4.1 Push to GitHub

1. Initialize git repository (if not already done):

   ```bash
   git init
   git add .
   git commit -m "Initial commit - LMS Activity Monitor"
   ```

2. Create a new repository on GitHub

3. Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/lms-scraper.git
   git branch -M main
   git push -u origin main
   ```

### 4.2 Add GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets (one by one):

   | Secret Name       | Value                          |
   | ----------------- | ------------------------------ |
   | `OUSL_USERNAME`   | Your OUSL username             |
   | `OUSL_PASSWORD`   | Your OUSL password             |
   | `RUSL_USERNAME`   | Your Rajarata username         |
   | `RUSL_PASSWORD`   | Your Rajarata password         |
   | `EMAIL_SENDER`    | Your Gmail address             |
   | `EMAIL_PASSWORD`  | Your Gmail App Password        |
   | `EMAIL_RECIPIENT` | Email to receive notifications |

### 4.3 Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will automatically run at 9 AM and 9 PM UTC
4. You can also manually trigger it by clicking "Run workflow"

### 4.4 Adjust Schedule (Optional)

To change scan times, edit `.github/workflows/monitor.yml`:

```yaml
schedule:
  - cron: "0 3 * * *" # 3 AM UTC = 9 AM Sri Lanka Time (UTC+6)
  - cron: "0 15 * * *" # 3 PM UTC = 9 PM Sri Lanka Time (UTC+6)
```

Use https://crontab.guru/ to help with cron syntax.

## Step 5: Web Dashboard (Optional)

Run the web dashboard locally:

```bash
python app.py
```

Then open: http://localhost:5000

### Features:

- View all courses from both universities
- See new activities and assignments
- Check scan history
- Manually trigger scans
- Test email notifications

## Step 6: Deploy Web Dashboard (Optional)

You can deploy the dashboard to:

- **Heroku** (free tier)
- **Railway** (free tier with GitHub Student Pack)
- **Render** (free tier)
- **PythonAnywhere** (free tier)

Example for Railway:

1. Install Railway CLI: https://docs.railway.app/
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`

## Troubleshooting

### Issue: Selenium/Chrome errors

**Solution:** Install Google Chrome:

- Windows: Download from google.com/chrome
- Linux: Already included in GitHub Actions
- Mac: Download from google.com/chrome

### Issue: Login fails

**Solution:**

- Double-check your credentials
- Make sure you can login manually to both Moodle sites
- Check if there are any captchas or additional security measures

### Issue: Email not sending

**Solution:**

- Verify Gmail App Password is correct (16 characters, no spaces)
- Ensure 2-Factor Authentication is enabled on your Google account
- Check if "Less secure app access" is not blocking it

### Issue: GitHub Actions failing

**Solution:**

- Check the Actions tab for error logs
- Verify all secrets are set correctly
- Make sure the workflow file has correct indentation

## What Gets Monitored?

The system monitors:

- ✅ New assignments (with deadlines)
- ✅ New resources (PDFs, files, links)
- ✅ New forum discussions
- ✅ New quizzes and tests
- ✅ Course announcements
- ✅ Any new activity added to courses

## Notification Format

You'll receive an email with:

- Subject: "🔔 LMS Update: X New Activities"
- List of all new activities grouped by university
- Course name for each activity
- Activity type (Assignment, Quiz, Resource, etc.)
- Deadline (if applicable)
- Direct link to view in Moodle
- Full description of the activity

## Usage Tips

1. **First scan**: The first time you run it, everything will be marked as "new". After that, only actual new items will trigger notifications.

2. **Frequency**: Set to run twice daily, but you can adjust in the GitHub Actions workflow.

3. **Manual scans**: Use the web dashboard or run `python scraper.py` anytime.

4. **Database**: The `lms_data.db` file stores all history. Back it up regularly.

5. **Privacy**: Your credentials are stored securely as GitHub Secrets and never exposed in logs.

## Advanced Configuration

### Change Check Times

Edit `check_times` in `.env`:

```
CHECK_TIMES=09:00,21:00
```

### Filter Courses

Modify `scraper.py` to filter specific courses by name or ID.

### Customize Notifications

Edit `notifier.py` to change email format or add other notification methods (Telegram, Discord, etc.).

## Support & Updates

- Check GitHub Issues for known problems
- Pull latest updates: `git pull origin main`
- Submit bug reports or feature requests on GitHub

---

**Security Reminder:** Never commit your `.env` file or share your credentials!

Enjoy staying on top of your coursework! 🎓
