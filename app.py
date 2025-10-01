from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
from dotenv import load_dotenv

from database import Database
from scraper import MoodleScraper
from notifier import Notifier

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-key')

db = Database()

@app.route('/')
def index():
    """Dashboard home page."""
    stats = db.get_stats()
    recent_activities = db.get_recent_activities(limit=20)
    scan_history = db.get_scan_history(limit=10)
    
    return render_template('index.html', 
                          stats=stats,
                          recent_activities=recent_activities,
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

@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime for display."""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    return value.strftime(format)

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
    
    now = datetime.now()
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
        return value.strftime('%Y-%m-%d')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
