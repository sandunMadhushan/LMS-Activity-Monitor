# LMS Activity Monitor

A web-based system to monitor multiple Moodle LMS instances for new activities, assignments, and course content. Get notifications twice daily about any new additions to your courses. **Now deployed on Render with automated GitHub Actions scanning!**

## 🌟 Features

- 🔍 **Multi-LMS Support**: Monitor OUSL and Rajarata University Moodle instances
- 📧 **Email Notifications**: Get detailed notifications about new content
- 🌐 **Web Dashboard**: View all changes in a user-friendly interface (deployed on Render)
- 🔄 **Automated Checks**: Runs twice daily (9 AM and 9 PM Sri Lanka Time) via GitHub Actions
- 📊 **Activity Tracking**: Monitors assignments, resources, forums, quizzes, and more
- � **Calendar Integration**: Syncs deadlines to your calendar automatically
- ⏰ **Deadline Reminders**: Get notified about upcoming deadlines
- �🔐 **Secure**: Credentials stored as GitHub Secrets

## 🚀 Quick Start

### Live Dashboard
Visit the live dashboard at: **https://lms-activity-monitor.onrender.com**

### Deployment Options

1. **Production (Recommended)**: Deployed on Render + GitHub Actions
2. **Local Development**: Run locally for testing

## 📦 Setup Instructions

### 1. Local Development Setup

1. Clone this repository
2. Install Python 3.9 or higher
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your actual credentials:
   - **OUSL credentials**: Your Open University username and password
   - **RUSL credentials**: Your Rajarata University username and password
   - **Email settings**: Gmail address and app password (see below)

### 2. Gmail Setup for Notifications

To send email notifications:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password:
   - Go to Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `.env` as `EMAIL_PASSWORD`

### 3. Running Locally

Run the scraper manually:

```bash
python scraper.py
```

Run the web dashboard:

```bash
python app.py
```

Then visit: `http://localhost:5000`

### 4. GitHub Actions Setup (Automated Scanning)

The system uses GitHub Actions to automatically scan both Moodle instances twice daily:

1. **Fork this repository**
2. **Go to Settings → Secrets and variables → Actions**
3. **Add the following secrets:**

   - `OUSL_USERNAME` - Your OUSL Moodle username
   - `OUSL_PASSWORD` - Your OUSL Moodle password
   - `RUSL_USERNAME` - Your RUSL Moodle username
   - `RUSL_PASSWORD` - Your RUSL Moodle password
   - `EMAIL_SENDER` - Your Gmail address
   - `EMAIL_PASSWORD` - Gmail app password
   - `EMAIL_RECIPIENT` - Email to receive notifications

4. **Automated Schedule**: 
   - Runs at **9:00 AM Sri Lanka Time** (3:30 AM UTC)
   - Runs at **9:00 PM Sri Lanka Time** (3:30 PM UTC)
   
5. **What it does automatically:**
   - ✅ Scans both OUSL and RUSL Moodle sites
   - ✅ Detects new activities and assignments
   - ✅ Sends email notifications for new content
   - ✅ Sends deadline reminders (7 days in advance)
   - ✅ Updates the database in the repository
   - ✅ Uploads database as workflow artifact

### 5. Render Deployment (Web Dashboard)

The web dashboard is deployed on Render.com for 24/7 access:

1. **Files already configured:**
   - `render.yaml` - Render service configuration
   - `runtime.txt` - Python 3.11.9 runtime
   - `requirements.txt` - Updated with gunicorn and production dependencies

2. **Deploy to Render:**
   - Connect your GitHub repository to Render
   - Render will auto-deploy from the `master` branch
   - No environment variables needed (uses database from GitHub)

3. **Important Notes:**
   - ⚠️ Scanning is disabled on Render (Chrome/ChromeDriver not available)
   - ✅ All scanning happens via GitHub Actions
   - ✅ Dashboard displays data from the GitHub-updated database
   - ✅ Calendar sync works on Render
   - ✅ Free tier sleeps after 15 minutes of inactivity

**See `docs/DEPLOYMENT_GUIDE.md` for detailed deployment instructions.**

### 6. Manual GitHub Actions Run

Go to Actions → LMS Monitor → Run workflow

## 🔄 How It Works

### Automated Workflow (GitHub Actions)
1. **Scheduled Trigger**: Runs at 9 AM & 9 PM Sri Lanka Time
2. **Authentication**: Logs into both OUSL and RUSL Moodle instances
3. **Course Discovery**: Finds all your enrolled courses
4. **Content Scraping**: Extracts all activities, assignments, resources using Selenium + Chrome
5. **Change Detection**: Compares with previous scan to find new items
6. **Notifications**: Sends email with details of new content
7. **Deadline Check**: Identifies upcoming deadlines (next 7 days) and sends reminders
8. **Database Update**: Commits updated database back to GitHub repository
9. **Artifact Upload**: Stores database as workflow artifact (90-day retention)

### Web Dashboard (Render)
1. **Always Online**: Hosted on Render.com for 24/7 access
2. **Real-time Data**: Uses the latest database from GitHub
3. **Calendar Sync**: Syncs deadlines to calendar events (Google Calendar compatible)
4. **Read-only Scanning**: Scan button disabled (handled by GitHub Actions)

## 📊 What Gets Monitored

- ✅ New assignments (with deadlines)
- ✅ New resources (PDFs, files, links)
- ✅ New forum posts
- ✅ New quizzes and exams
- ✅ New pages and labels
- ✅ Course updates and announcements
- ✅ Assignment deadlines
- ✅ Calendar events from Moodle

## 🎨 Dashboard Features

- 📈 Statistics overview (courses, activities, deadlines)
- 📚 View all courses from both universities
- 🆕 See recent changes and new activities
- 📅 Upcoming deadlines (7-day view)
- 🔍 Search functionality
- 📧 Test email notifications
- 🔄 Manual calendar sync
- 🎯 Filter by LMS (OUSL/RUSL)

## Project Structure

```
lms-scraper/
├── .github/
│   └── workflows/
│       └── monitor.yml          # GitHub Actions workflow for automated scanning
├── docs/                        # 📚 All documentation
│   ├── README.md               # Documentation index
│   ├── GETTING_STARTED.md      # Complete getting started guide
│   ├── SETUP_GUIDE.md          # Detailed setup instructions
│   ├── QUICK_REFERENCE.md      # Quick reference guide
│   ├── SCHEDULING.md           # Automatic scheduling documentation
│   ├── SCHEDULER_QUICKSTART.md # Scheduler quick start
│   ├── PROJECT_OVERVIEW.md     # Architecture and design
│   ├── IMPLEMENTATION_SUMMARY.md # Implementation details
│   └── SYSTEM_SUMMARY.md       # System features summary
├── static/
│   └── style.css               # Web dashboard CSS styles
├── templates/                   # Flask HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Main dashboard
│   ├── courses.html            # Courses page
│   ├── course_detail.html      # Course detail page
│   └── activities.html         # Activities page
├── tests/                       # 🧪 Test scripts
│   ├── README.md               # Test documentation
│   ├── test_setup.py           # System setup tests
│   └── test_course_names.py    # Course scraping tests
│
├── .env                         # Environment variables (create from .env.example)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # This file - main documentation
├── requirements.txt            # Python dependencies
├── lms_data.db                 # SQLite database (created automatically)
│
├── app.py                      # 🌐 Flask web application
├── scraper.py                  # 🔍 Main scraping logic (OUSL & RUSL)
├── database.py                 # 💾 Database operations (SQLite)
├── calendar_scraper.py         # 📅 Calendar event scraper & deadline extractor
├── scheduler.py                # ⏰ Background task scheduler (APScheduler)
├── notifier.py                 # 📧 Email notification system
│
├── start.sh                    # Linux/Mac startup script
└── start.bat                   # Windows startup script
```

### Core Components

- **`app.py`** - Flask web server with dashboard, routes, and API endpoints
- **`scraper.py`** - Selenium-based web scraper for OUSL and RUSL Moodle sites (~900 lines)
- **`database.py`** - SQLite database manager with all CRUD operations (~650 lines)
- **`calendar_scraper.py`** - iCalendar event fetcher and deadline extractor from text
- **`scheduler.py`** - APScheduler integration for automated twice-daily scanning
- **`notifier.py`** - SMTP-based email notification system

### Documentation

All detailed documentation is in the `docs/` folder:
- **Getting Started**: `docs/GETTING_STARTED.md` - New user guide
- **Setup Guide**: `docs/SETUP_GUIDE.md` - Detailed setup walkthrough  
- **Quick Reference**: `docs/QUICK_REFERENCE.md` - Commands and common tasks
- **Scheduling**: `docs/SCHEDULING.md` - Auto-scan configuration
- **Architecture**: `docs/PROJECT_OVERVIEW.md` - System design and architecture

### Testing

Test scripts are in the `tests/` folder:
- **`test_setup.py`** - Validates environment setup and configuration
- **`test_course_names.py`** - Tests scraping functionality for both universities

Run tests:
```bash
python tests/test_setup.py
python tests/test_course_names.py
```

## 🛠️ Troubleshooting

### Scraper Issues (GitHub Actions)
- Check the Actions tab for detailed logs
- Make sure credentials are correct in GitHub Secrets
- Verify Moodle sites are accessible
- Chrome/ChromeDriver are automatically installed by the workflow

### Email Issues
- Verify Gmail app password is correct
- Check if 2FA is enabled on your Google Account
- Use App Passwords (not your regular password)
- Check spam folder for notifications

### GitHub Actions Issues
- Check Actions tab for error logs
- Verify all 7 secrets are set correctly
- Ensure repository has write permissions enabled
- Database commits require `permissions: contents: write` (already configured)

### Render Deployment Issues
- Check Render dashboard logs for errors
- Verify `runtime.txt` specifies Python 3.11.9
- Database is tracked in git (not blocked by .gitignore)
- Scan button is disabled on Render (by design)

### Calendar Sync Issues
- Check that deadlines exist in the database
- Calendar events are stored in the `deadlines` table with `source='calendar'`
- Duplicate events are automatically prevented
- Delete old calendar events manually if needed: `DELETE FROM deadlines WHERE source='calendar'`

## 🔒 Security Notes

- ✅ Never commit `.env` file (already in .gitignore)
- ✅ Use GitHub Secrets for all sensitive data
- ✅ Credentials are encrypted in transit (HTTPS)
- ✅ Database is public but contains no sensitive info (only course metadata)
- ✅ Use Gmail App Passwords (not your main password)
- ✅ Repository can be private if needed (GitHub Actions work on private repos)

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs (Actions tab)
2. Review Render deployment logs (Render dashboard)
3. Check error messages in email notifications
4. Ensure all dependencies are installed (`requirements.txt`)
5. Verify Moodle sites are accessible from your network
6. See detailed docs in `docs/` folder

## 🚀 Recent Updates

- ✅ Deployed to Render.com for 24/7 web access
- ✅ GitHub Actions scheduled for 9 AM & 9 PM Sri Lanka Time
- ✅ Added calendar sync functionality
- ✅ Automated deadline reminders (7 days in advance)
- ✅ Fixed database tracking in git
- ✅ Disabled scan button on Render (automated via GitHub Actions)
- ✅ Added write permissions for workflow commits
- ✅ Removed artifact download step (using git-tracked database)

## 📚 Documentation

For more detailed information, see the `docs/` folder:
- **`DEPLOYMENT_GUIDE.md`** - Complete Render + GitHub Actions setup
- **`GETTING_STARTED.md`** - New user guide
- **`SETUP_GUIDE.md`** - Detailed setup walkthrough
- **`SCHEDULING.md`** - Auto-scan configuration
- **`PROJECT_OVERVIEW.md`** - System architecture

## 📄 License

MIT License - Feel free to modify and use for your needs!

---

**Made with ❤️ for OUSL and Rajarata University students**
```
