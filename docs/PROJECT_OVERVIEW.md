# 🎓 LMS Activity Monitor - Complete System

## Overview

A comprehensive web-based system to monitor multiple Moodle LMS instances for new activities, assignments, and course content. Designed for students managing multiple degree programs simultaneously.

## ✨ Key Features

### Core Functionality
- **Multi-LMS Support**: Monitor both OUSL and Rajarata University Moodle instances simultaneously
- **Automated Monitoring**: Runs twice daily (9 AM and 9 PM) via GitHub Actions
- **Smart Change Detection**: Only notifies about genuinely new content
- **Comprehensive Coverage**: Monitors all activity types (assignments, quizzes, resources, forums, etc.)

### Notification System
- **Email Notifications**: Detailed HTML emails with full activity information
- **Rich Content**: Includes deadlines, descriptions, and direct links
- **Grouped by LMS**: Clear organization of updates from each university
- **Beautiful Formatting**: Professional HTML email template

### Web Dashboard
- **Real-time Overview**: View all courses and activities
- **Statistics Dashboard**: Track total courses, activities, and new items
- **Course Browser**: Navigate through all enrolled courses
- **Activity Timeline**: See recent changes chronologically
- **Manual Controls**: Trigger scans and test emails from the interface
- **Responsive Design**: Works on desktop, tablet, and mobile

### Security & Privacy
- **Secure Credentials**: Uses GitHub Secrets for sensitive data
- **Encrypted Storage**: All credentials encrypted in transit
- **No Logs**: Passwords never appear in logs or console output
- **Private Database**: Local SQLite database with your data only

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Scheduler)                │
│              Runs at 9 AM & 9 PM (Configurable)             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Selenium Web Scraper                      │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   OUSL Moodle    │         │  RUSL Moodle     │         │
│  │   - Login        │         │  - Login         │         │
│  │   - Get Courses  │         │  - Get Courses   │         │
│  │   - Extract      │         │  - Extract       │         │
│  │     Activities   │         │     Activities   │         │
│  └──────────────────┘         └──────────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     SQLite Database                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Courses    │  │  Activities  │  │ Scan History │     │
│  │              │  │              │  │              │     │
│  │ - Course ID  │  │ - Title      │  │ - Timestamp  │     │
│  │ - Name       │  │ - Type       │  │ - Results    │     │
│  │ - LMS        │  │ - Deadline   │  │ - Status     │     │
│  │ - URL        │  │ - Is New     │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────┬───────────────────────────┬─────────────────┘
                │                           │
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────────┐
│   Email Notifier          │   │   Flask Web Dashboard    │
│   - Check new activities  │   │   - View courses         │
│   - Format HTML email     │   │   - Browse activities    │
│   - Send via SMTP         │   │   - Statistics           │
│   - Mark as notified      │   │   - Manual scan          │
└───────────────────────────┘   └──────────────────────────┘
```

## 📁 Project Structure

```
lms-scraper/
│
├── scraper.py              # Main scraping logic with Selenium
├── database.py             # SQLite database operations
├── notifier.py             # Email notification system
├── app.py                  # Flask web application
│
├── templates/              # HTML templates for web dashboard
│   ├── base.html          # Base template with navbar
│   ├── index.html         # Dashboard homepage
│   ├── courses.html       # Courses listing page
│   ├── course_detail.html # Individual course view
│   └── activities.html    # All activities view
│
├── static/
│   └── style.css          # Comprehensive styling
│
├── .github/
│   └── workflows/
│       └── monitor.yml    # GitHub Actions workflow
│
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
│
├── README.md             # Project overview
├── SETUP_GUIDE.md        # Detailed setup instructions
├── PROJECT_OVERVIEW.md   # This file
├── LICENSE               # MIT License
│
├── start.sh              # Quick start script (Linux/Mac)
└── start.bat             # Quick start script (Windows)
```

## 🔧 Technology Stack

### Backend
- **Python 3.11**: Core programming language
- **Selenium**: Web browser automation for scraping
- **Beautiful Soup**: HTML parsing
- **SQLite**: Lightweight database
- **SMTP**: Email sending

### Web Dashboard
- **Flask**: Lightweight Python web framework
- **Jinja2**: Templating engine
- **HTML5/CSS3**: Frontend technologies
- **Font Awesome**: Icons

### Automation
- **GitHub Actions**: Scheduled task runner (free tier)
- **Cron**: Scheduling syntax

### Dependencies
- `flask==3.0.0` - Web framework
- `requests==2.31.0` - HTTP library
- `beautifulsoup4==4.12.2` - HTML parser
- `selenium==4.15.2` - Browser automation
- `python-dotenv==1.0.0` - Environment variables
- `webdriver-manager==4.0.1` - Auto Chrome driver management
- `lxml==4.9.3` - XML/HTML processing

## 🚀 Deployment Options

### Option 1: GitHub Actions (Recommended)
- ✅ **Free**: No cost with GitHub free tier
- ✅ **Automated**: Runs on schedule
- ✅ **Secure**: Credentials stored as secrets
- ✅ **Reliable**: GitHub infrastructure
- ❌ **Limitation**: No persistent web dashboard

### Option 2: Local Machine
- ✅ **Full Control**: Run anytime
- ✅ **Web Dashboard**: Access locally
- ✅ **No Limits**: Run as often as you want
- ❌ **Manual**: Requires your computer to be on

### Option 3: Cloud Hosting (Web Dashboard)
Deploy the dashboard to:

#### Heroku (Free Tier)
- Web dashboard accessible 24/7
- Database persistence
- Easy deployment

#### Railway (GitHub Student Pack)
- $5/month credit (free with student pack)
- Better performance than Heroku
- Simple setup

#### Render (Free Tier)
- Free static site hosting
- Auto-deploy from GitHub

#### PythonAnywhere (Free Tier)
- Python-focused hosting
- Good for beginners

## 🎯 Use Cases

### Primary Use Case
**Student with Multiple Degrees**
- Enrolled in OUSL and Rajarata University
- Hard to check both Moodle sites regularly
- Misses assignments and deadlines
- **Solution**: Automated notifications twice daily

### Additional Use Cases
1. **Part-time Students**: Working professionals who can't check daily
2. **Online Learners**: Students in multiple online courses
3. **Faculty**: Instructors monitoring multiple courses
4. **Course Coordinators**: Tracking updates across programs

## 📊 What Gets Monitored?

### Activity Types
- ✅ **Assignments** - with deadlines
- ✅ **Quizzes** - with due dates
- ✅ **Resources** - PDFs, files, links
- ✅ **Forums** - new discussions
- ✅ **Pages** - course content
- ✅ **URLs** - external links
- ✅ **Labels** - section headers
- ✅ **Books** - course textbooks
- ✅ **Workshops** - peer assessments
- ✅ **Lessons** - structured content

### Metadata Captured
- Title and description
- Activity type
- Course association
- Direct URL
- Deadline (if applicable)
- First seen timestamp
- LMS source

## 🔐 Security Considerations

### Credential Storage
- **Local**: `.env` file (never committed)
- **GitHub**: Repository Secrets (encrypted)
- **Runtime**: Environment variables (memory only)

### Best Practices
1. Never commit `.env` file
2. Use GitHub Secrets for automation
3. Enable 2FA on your Moodle accounts
4. Use Gmail App Passwords (not main password)
5. Regularly rotate credentials
6. Keep dependencies updated

### Data Privacy
- Database stored locally or in GitHub artifacts
- No third-party data sharing
- Your credentials never leave your control
- Email sent directly from your Gmail

## 📈 Future Enhancements

### Planned Features
- [ ] Telegram bot notifications
- [ ] Discord webhook support
- [ ] SMS notifications (Twilio)
- [ ] Mobile app (React Native)
- [ ] Calendar integration (Google Calendar)
- [ ] Priority filtering (urgent assignments first)
- [ ] Multi-language support
- [ ] Dark mode for web dashboard
- [ ] Export to CSV/Excel
- [ ] Assignment completion tracking

### Potential Integrations
- **Notion**: Auto-create tasks
- **Todoist**: Add assignments as tasks
- **Google Calendar**: Auto-add deadlines
- **Slack**: Team notifications
- **Microsoft Teams**: Enterprise notifications

## 🐛 Troubleshooting

### Common Issues

**1. Login Fails**
- Verify credentials are correct
- Check if Moodle is accessible
- Look for CAPTCHA or security measures
- Try running with `--headless False` to see what happens

**2. Email Not Sending**
- Verify Gmail App Password (16 chars)
- Check 2FA is enabled
- Ensure SMTP settings are correct
- Test with `--test-email` flag

**3. GitHub Actions Failing**
- Check all secrets are set
- Review Actions logs for errors
- Verify workflow syntax
- Check rate limits

**4. Database Issues**
- Delete `lms_data.db` to reset
- Check file permissions
- Ensure SQLite is installed

**5. Browser/Selenium Errors**
- Install/update Chrome
- Clear browser cache
- Update webdriver-manager
- Check Chrome version compatibility

## 📞 Support

### Getting Help
1. Check `SETUP_GUIDE.md` for detailed instructions
2. Review error messages in logs
3. Search GitHub Issues
4. Create a new issue with details

### Contributing
Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built for students managing multiple degree programs
- Inspired by the challenges of online learning
- Powered by open-source technologies
- Community-driven development

---

**Made with ❤️ for students who want to stay on top of their coursework!**

*Last Updated: October 2025*
