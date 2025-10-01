# LMS Activity Monitor

A web-based system to monitor multiple Moodle LMS instances for new activities, assignments, and course content. Get notifications twice daily about any new additions to your courses.

## Features

- 🔍 **Multi-LMS Support**: Monitor OUSL and Rajarata University Moodle instances
- 📧 **Email Notifications**: Get detailed notifications about new content
- 🌐 **Web Dashboard**: View all changes in a user-friendly interface
- 🔄 **Automated Checks**: Runs twice daily (9 AM and 9 PM) via GitHub Actions
- 📊 **Activity Tracking**: Monitors assignments, resources, forums, quizzes, and more
- 🔐 **Secure**: Credentials stored as GitHub Secrets

## Setup Instructions

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

### 4. GitHub Actions Setup (Automated Checks)

1. Fork this repository
2. Go to Settings → Secrets and variables → Actions
3. Add the following secrets:

   - `OUSL_USERNAME`
   - `OUSL_PASSWORD`
   - `RUSL_USERNAME`
   - `RUSL_PASSWORD`
   - `EMAIL_SENDER`
   - `EMAIL_PASSWORD`
   - `EMAIL_RECIPIENT`

4. The workflow will automatically run twice daily (9 AM and 9 PM UTC)

### 5. Manual GitHub Actions Run

Go to Actions → LMS Monitor → Run workflow

## How It Works

1. **Authentication**: Logs into both Moodle instances using your credentials
2. **Course Discovery**: Finds all your enrolled courses
3. **Content Scraping**: Extracts all activities, assignments, resources
4. **Change Detection**: Compares with previous scan to find new items
5. **Notifications**: Sends email with details of new content
6. **Storage**: Saves data to SQLite database for history

## What Gets Monitored

- ✅ New assignments (with deadlines)
- ✅ New resources (PDFs, files, links)
- ✅ New forum posts
- ✅ New quizzes
- ✅ New pages and labels
- ✅ Course updates and announcements

## Dashboard Features

- View all courses from both universities
- See recent changes and additions
- Filter by date or course
- View assignment deadlines
- Search functionality

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

## Troubleshooting

### Scraper Issues
- Make sure credentials are correct
- Check if Moodle sites are accessible
- Try running with `--headless false` for debugging

### Email Issues
- Verify Gmail app password is correct
- Check if 2FA is enabled
- Make sure "Less secure app access" is not needed (use app passwords instead)

### GitHub Actions
- Check Actions tab for error logs
- Verify all secrets are set correctly
- Ensure repository is not private (or enable Actions for private repos)

## Security Notes

- Never commit `.env` file
- Use GitHub Secrets for sensitive data
- Credentials are encrypted in transit
- Database stored locally/in GitHub (encrypted)

## Support

If you encounter issues:
1. Check the logs in the Actions tab
2. Review error messages
3. Ensure all dependencies are installed
4. Verify Moodle sites are accessible

## License

MIT License - Feel free to modify and use for your needs!
```
