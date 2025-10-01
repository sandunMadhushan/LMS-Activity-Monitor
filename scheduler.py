"""
Background scheduler for automated tasks.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import hashlib

from calendar_scraper import CalendarScraper
from database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for the LMS monitoring system."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.db = Database()
        self.calendar_scraper = CalendarScraper()
    
    def _generate_deadline_id(self, lms, date_iso, title):
        """Generate a deterministic deadline ID using MD5 hash."""
        content = f"{lms}_{date_iso}_{title}"
        hash_obj = hashlib.md5(content.encode('utf-8'))
        return f"cal_{hash_obj.hexdigest()[:16]}"
        
    def sync_calendar_job(self):
        """Job to sync calendar events from both LMS."""
        try:
            logger.info("🗓️  Starting scheduled calendar sync...")
            events = self.calendar_scraper.get_all_calendar_events()
            
            # Store calendar events in deadlines table
            count = 0
            within_60_days = 0
            from datetime import timezone, timedelta
            now = datetime.now(timezone.utc)
            sixty_days_later = now + timedelta(days=60)
            
            for event in events:
                deadline_id = self._generate_deadline_id(
                    event['lms'], 
                    event['date'].isoformat(), 
                    event['title']
                )
                self.db.add_deadline(
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
            
            logger.info(f"✅ Calendar sync completed! Synced {count} events ({within_60_days} within next 60 days) at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
            
        except Exception as e:
            logger.error(f"❌ Calendar sync failed: {str(e)}")
    
    def start(self):
        """Start the scheduler with configured jobs."""
        # Schedule calendar sync at 9 AM and 9 PM daily
        self.scheduler.add_job(
            func=self.sync_calendar_job,
            trigger=CronTrigger(hour='9,21', minute='0'),  # 9 AM and 9 PM
            id='calendar_sync',
            name='Sync Calendar Events',
            replace_existing=True
        )
        
        logger.info("📅 Scheduled calendar sync: Daily at 9:00 AM and 9:00 PM")
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("✅ Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
    
    def get_jobs(self):
        """Get list of all scheduled jobs."""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %I:%M %p') if job.next_run_time else 'N/A'
            })
        return jobs
