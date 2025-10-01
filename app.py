from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from dotenv import load_dotenv
import atexit
import hashlib

from database import Database
from scraper import MoodleScraper
from notifier import Notifier
from calendar_scraper import CalendarScraper
from scheduler import TaskScheduler

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-key')

db = Database()
calendar_scraper = CalendarScraper()

# Initialize and start the scheduler
scheduler = TaskScheduler()
scheduler.start()

# Ensure scheduler stops when app shuts down
atexit.register(lambda: scheduler.stop())

@app.route('/')
def index():
    """Dashboard home page."""
    stats = db.get_stats()
    recent_activities = db.get_recent_activities(limit=20)
    scan_history = db.get_scan_history(limit=10)
    
    # Get activities separated by LMS
    ousl_activities = db.get_activities_by_lms('OUSL', limit=15)
    rjta_activities = db.get_activities_by_lms('RJTA', limit=15)
    
    # Get upcoming deadlines (combined from activities, calendar, and scraped)
    # Fetch all upcoming deadlines (no time limit) and filter on frontend
    upcoming_deadlines = db.get_all_upcoming_deadlines(days_ahead=365)
    
    return render_template('index.html', 
                          stats=stats,
                          recent_activities=recent_activities,
                          ousl_activities=ousl_activities,
                          rjta_activities=rjta_activities,
                          upcoming_deadlines=upcoming_deadlines,
                          scan_history=scan_history)

@app.route('/courses')
def courses():
    """View all courses."""
    lms_filter = request.args.get('lms', None)
    courses_list = db.get_all_courses(lms_name=lms_filter)
    
    return render_template('courses.html', courses=courses_list, lms_filter=lms_filter)

@app.route('/course/<course_id>')
def course_detail(course_id):
    """View activities for a specific course."""
    activities = db.get_activities_by_course(course_id)
    
    # Get course info
    courses = db.get_all_courses()
    course = next((c for c in courses if c['course_id'] == course_id), None)
    
    return render_template('course_detail.html', course=course, activities=activities)

@app.route('/activities')
def activities():
    """View all activities."""
    limit = int(request.args.get('limit', 50))
    activities_list = db.get_recent_activities(limit=limit)
    
    return render_template('activities.html', activities=activities_list)

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger a manual scan."""
    try:
        scraper = MoodleScraper(headless=True)
        results = scraper.run_full_scan()
        
        return jsonify({
            'success': True,
            'message': f'Scan completed. Found {results["total_new_activities"]} new activities.',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Scan failed: {str(e)}'
        }), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Send a test email."""
    try:
        notifier = Notifier()
        success = notifier.send_test_email()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send test email. Check configuration.'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/stats')
def api_stats():
    """Get statistics as JSON."""
    stats = db.get_stats()
    return jsonify(stats)

@app.route('/api/activities/new')
def api_new_activities():
    """Get new activities as JSON."""
    activities = db.get_new_activities()
    return jsonify(activities)

@app.route('/api/sync-calendar', methods=['POST'])
def sync_calendar():
    """Sync calendar events from both LMS."""
    try:
        events = calendar_scraper.get_all_calendar_events()
        
        # Store calendar events in deadlines table
        count = 0
        within_60_days = 0
        from datetime import timezone, timedelta
        now = datetime.now(timezone.utc)
        sixty_days_later = now + timedelta(days=60)
        
        for event in events:
            # Generate deterministic deadline ID using MD5 hash
            content = f"{event['lms']}_{event['date'].isoformat()}_{event['title']}"
            hash_obj = hashlib.md5(content.encode('utf-8'))
            deadline_id = f"cal_{hash_obj.hexdigest()[:16]}"
            
            db.add_deadline(
                deadline_id=deadline_id,
                title=event['title'],
                description=event.get('description', ''),
                deadline_date=event['date'].isoformat(),
                lms_name=event['lms'],
                source='calendar',
                location=event.get('location', '')
            )
            count += 1
            
            # Count events within 60 days
            if event['date'] <= sixty_days_later:
                within_60_days += 1
        
        return jsonify({
            'success': True,
            'message': f'Synced {count} calendar events successfully! ({within_60_days} within next 60 days)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error syncing calendar: {str(e)}'
        }), 500

@app.route('/api/scheduled-jobs')
def scheduled_jobs():
    """Get list of scheduled jobs."""
    try:
        jobs = scheduler.get_jobs()
        return jsonify({
            'success': True,
            'jobs': jobs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving jobs: {str(e)}'
        }), 500

@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime for display in Asia/Colombo timezone."""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    # Ensure value is timezone-aware (assume UTC if naive)
    if value.tzinfo is None:
        from datetime import timezone
        value = value.replace(tzinfo=timezone.utc)
    
    # Convert to Asia/Colombo timezone (GMT+5:30)
    from datetime import timezone, timedelta
    colombo_tz = timezone(timedelta(hours=5, minutes=30))
    local_time = value.astimezone(colombo_tz)
    
    return local_time.strftime(format)

@app.template_filter('timeago')
def timeago(value):
    """Format datetime as time ago."""
    if value is None:
        return ''
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    # Ensure value is timezone-aware (assume UTC if naive)
    if value.tzinfo is None:
        from datetime import timezone
        value = value.replace(tzinfo=timezone.utc)
    
    # Use UTC time for comparison
    from datetime import timezone
    now = datetime.now(timezone.utc)
    diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    else:
        # Convert to Asia/Colombo timezone for older dates
        from datetime import timedelta
        colombo_tz = timezone(timedelta(hours=5, minutes=30))
        local_time = value.astimezone(colombo_tz)
        return local_time.strftime('%Y-%m-%d')

@app.template_filter('timeonly')
def timeonly(value):
    """Format datetime showing only time in Asia/Colombo timezone."""
    if value is None:
        return ''
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    # Ensure value is timezone-aware (assume UTC if naive)
    if value.tzinfo is None:
        from datetime import timezone
        value = value.replace(tzinfo=timezone.utc)
    
    # Convert to Asia/Colombo timezone (GMT+5:30)
    from datetime import timezone, timedelta
    colombo_tz = timezone(timedelta(hours=5, minutes=30))
    local_time = value.astimezone(colombo_tz)
    
    # Use UTC time for comparison to determine format
    now = datetime.now(timezone.utc)
    diff = now - value
    seconds = diff.total_seconds()
    
    # Show only the actual time in Colombo timezone
    if seconds < 86400:  # Today
        return local_time.strftime('%I:%M %p')
    elif seconds < 604800:  # This week
        return local_time.strftime('%b %d, %I:%M %p')
    else:  # Older
        return local_time.strftime('%b %d, %Y')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
