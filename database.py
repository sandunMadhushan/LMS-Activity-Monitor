import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

class Database:
    """Handle all database operations for LMS monitoring."""
    
    def __init__(self, db_path: str = "lms_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT UNIQUE NOT NULL,
                lms_name TEXT NOT NULL,
                course_name TEXT NOT NULL,
                course_url TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id TEXT UNIQUE NOT NULL,
                course_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT,
                deadline TIMESTAMP,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_new BOOLEAN DEFAULT 1,
                metadata TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
        """)
        
        # Scan history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lms_name TEXT NOT NULL,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                courses_found INTEGER,
                activities_found INTEGER,
                new_activities INTEGER,
                status TEXT,
                error_message TEXT
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notification_type TEXT,
                status TEXT,
                FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
            )
        """)
        
        # Deadlines table (for calendar events and scraped deadlines)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deadline_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                deadline_date TIMESTAMP NOT NULL,
                lms_name TEXT NOT NULL,
                course_id TEXT,
                activity_id TEXT,
                source TEXT NOT NULL,
                location TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(course_id),
                FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_course(self, course_id: str, lms_name: str, course_name: str, course_url: str = None):
        """Add or update a course."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO courses (course_id, lms_name, course_name, course_url, last_checked)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(course_id) DO UPDATE SET
                course_name = excluded.course_name,
                course_url = excluded.course_url,
                last_checked = CURRENT_TIMESTAMP
        """, (course_id, lms_name, course_name, course_url))
        
        conn.commit()
        conn.close()
    
    def add_activity(self, activity_id: str, course_id: str, activity_type: str,
                     title: str, description: str = None, url: str = None,
                     deadline: str = None, metadata: Dict = None) -> bool:
        """
        Add a new activity. Returns True if activity is new, False if it already exists.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if activity already exists
        cursor.execute("SELECT id FROM activities WHERE activity_id = ?", (activity_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing activity
            cursor.execute("""
                UPDATE activities
                SET is_new = 0, description = ?, deadline = ?, metadata = ?
                WHERE activity_id = ?
            """, (description, deadline, json.dumps(metadata) if metadata else None, activity_id))
            conn.commit()
            conn.close()
            return False
        else:
            # Insert new activity
            cursor.execute("""
                INSERT INTO activities 
                (activity_id, course_id, activity_type, title, description, url, deadline, metadata, is_new)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (activity_id, course_id, activity_type, title, description, url, deadline,
                  json.dumps(metadata) if metadata else None))
            
            conn.commit()
            conn.close()
            return True
    
    def get_new_activities(self) -> List[Dict[str, Any]]:
        """Get all new activities that haven't been notified."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.activity_id,
                a.activity_type,
                a.title,
                a.description,
                a.url,
                a.deadline,
                a.first_seen,
                a.metadata,
                c.course_name,
                c.lms_name,
                c.course_url
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.is_new = 1
            ORDER BY a.first_seen DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        activities = []
        
        for row in cursor.fetchall():
            activity = dict(zip(columns, row))
            if activity['metadata']:
                activity['metadata'] = json.loads(activity['metadata'])
            activities.append(activity)
        
        conn.close()
        return activities
    
    def mark_activities_as_notified(self, activity_ids: List[str]):
        """Mark activities as no longer new after notification sent."""
        if not activity_ids:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(activity_ids))
        cursor.execute(f"""
            UPDATE activities
            SET is_new = 0
            WHERE activity_id IN ({placeholders})
        """, activity_ids)
        
        # Record notifications
        for activity_id in activity_ids:
            cursor.execute("""
                INSERT INTO notifications (activity_id, notification_type, status)
                VALUES (?, 'email', 'sent')
            """, (activity_id,))
        
        conn.commit()
        conn.close()
    
    def add_scan_history(self, lms_name: str, courses_found: int, 
                        activities_found: int, new_activities: int,
                        status: str = "success", error_message: str = None):
        """Record a scan operation."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scan_history 
            (lms_name, courses_found, activities_found, new_activities, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lms_name, courses_found, activities_found, new_activities, status, error_message))
        
        conn.commit()
        conn.close()
    
    def get_all_courses(self, lms_name: str = None) -> List[Dict[str, Any]]:
        """Get all courses, optionally filtered by LMS."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if lms_name:
            cursor.execute("""
                SELECT course_id, lms_name, course_name, course_url, first_seen, last_checked
                FROM courses
                WHERE lms_name = ?
                ORDER BY course_name
            """, (lms_name,))
        else:
            cursor.execute("""
                SELECT course_id, lms_name, course_name, course_url, first_seen, last_checked
                FROM courses
                ORDER BY lms_name, course_name
            """)
        
        columns = [desc[0] for desc in cursor.description]
        courses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return courses
    
    def get_activities_by_course(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all activities for a specific course."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                activity_id, activity_type, title, description, url, 
                deadline, first_seen, is_new, metadata
            FROM activities
            WHERE course_id = ?
            ORDER BY first_seen DESC
        """, (course_id,))
        
        columns = [desc[0] for desc in cursor.description]
        activities = []
        
        for row in cursor.fetchall():
            activity = dict(zip(columns, row))
            if activity['metadata']:
                activity['metadata'] = json.loads(activity['metadata'])
            activities.append(activity)
        
        conn.close()
        return activities
    
    def get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most recent activities across all courses."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.activity_id,
                a.activity_type,
                a.title,
                a.description,
                a.url,
                a.deadline,
                a.first_seen,
                a.is_new,
                c.course_name,
                c.lms_name
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            ORDER BY a.first_seen DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        activities = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return activities
    
    def get_scan_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent scan history."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM scan_history
            ORDER BY scan_time DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return history
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = cursor.fetchone()[0]
        
        # Total activities
        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]
        
        # New activities
        cursor.execute("SELECT COUNT(*) FROM activities WHERE is_new = 1")
        new_activities = cursor.fetchone()[0]
        
        # Activities by type
        cursor.execute("""
            SELECT activity_type, COUNT(*) as count
            FROM activities
            GROUP BY activity_type
        """)
        activities_by_type = dict(cursor.fetchall())
        
        # Last scan time
        cursor.execute("""
            SELECT scan_time, lms_name
            FROM scan_history
            ORDER BY scan_time DESC
            LIMIT 1
        """)
        last_scan = cursor.fetchone()
        
        # Count by LMS
        cursor.execute("SELECT COUNT(*) FROM courses WHERE lms_name = 'OUSL'")
        ousl_courses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM courses WHERE lms_name = 'RUSL'")
        rusl_courses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_courses': total_courses,
            'total_activities': total_activities,
            'new_activities': new_activities,
            'activities_by_type': activities_by_type,
            'last_scan_time': last_scan[0] if last_scan else None,
            'last_scan_lms': last_scan[1] if last_scan else None,
            'ousl_courses': ousl_courses,
            'rusl_courses': rusl_courses
        }
    
    def get_upcoming_deadlines(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get activities with upcoming deadlines."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.activity_id,
                a.activity_type,
                a.title,
                a.description,
                a.url,
                a.deadline,
                a.is_new,
                c.course_name,
                c.lms_name
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.deadline IS NOT NULL
            AND a.deadline != ''
            ORDER BY a.deadline ASC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        deadlines = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return deadlines
    
    def get_activities_by_lms(self, lms_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activities for a specific LMS."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.activity_id,
                a.activity_type,
                a.title,
                a.description,
                a.url,
                a.deadline,
                a.first_seen,
                a.is_new,
                c.course_name,
                c.lms_name
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            WHERE c.lms_name = ?
            ORDER BY a.first_seen DESC
            LIMIT ?
        """, (lms_name, limit))
        
        columns = [desc[0] for desc in cursor.description]
        activities = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return activities

    
    def add_deadline(self, deadline_id: str, title: str, deadline_date: str, 
                    lms_name: str, description: str = None, course_id: str = None,
                    activity_id: str = None, source: str = 'scraped', location: str = None):
        """Add or update a deadline."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO deadlines (deadline_id, title, description, deadline_date, 
                                  lms_name, course_id, activity_id, source, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(deadline_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                deadline_date = excluded.deadline_date,
                location = excluded.location
        """, (deadline_id, title, description, deadline_date, lms_name, 
              course_id, activity_id, source, location))
        
        conn.commit()
        conn.close()
    
    def delete_calendar_events(self):
        """Delete all calendar events from deadlines table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM deadlines WHERE source = 'calendar'")
        
        conn.commit()
        conn.close()
    
    def get_all_upcoming_deadlines(self, days_ahead: int = 30):
        """Get all upcoming deadlines from both activities and calendar events."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get deadlines from activities
        cursor.execute("""
            SELECT 
                a.activity_id as id,
                a.title,
                a.description,
                a.deadline as deadline_date,
                a.url,
                c.course_name,
                c.lms_name,
                'activity' as source,
                '' as location
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.deadline IS NOT NULL
            AND a.deadline != ''
            AND datetime(a.deadline) >= datetime('now')
            AND datetime(a.deadline) <= datetime('now', '+' || ? || ' days')
        """, (days_ahead,))
        
        activity_deadlines = [dict(zip([desc[0] for desc in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        # Get deadlines from calendar/deadlines table
        cursor.execute("""
            SELECT 
                deadline_id as id,
                title,
                description,
                deadline_date,
                '' as url,
                COALESCE((SELECT course_name FROM courses WHERE course_id = d.course_id), '') as course_name,
                lms_name,
                source,
                location
            FROM deadlines d
            WHERE datetime(deadline_date) >= datetime('now')
            AND datetime(deadline_date) <= datetime('now', '+' || ? || ' days')
        """, (days_ahead,))
        
        calendar_deadlines = [dict(zip([desc[0] for desc in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        conn.close()
        
        # Combine and sort by date
        all_deadlines = activity_deadlines + calendar_deadlines
        all_deadlines.sort(key=lambda x: x.get('deadline_date', ''))
        
        return all_deadlines
    
    def get_scan_history(self, limit: int = 10):
        """Get recent scan history."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                lms_name,
                scan_time,
                courses_found,
                activities_found,
                new_activities,
                status,
                error_message
            FROM scan_history
            ORDER BY scan_time DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return history

    
    def add_deadline(self, deadline_id: str, title: str, deadline_date: str, 
                    lms_name: str, description: str = None, course_id: str = None,
                    activity_id: str = None, source: str = 'scraped', location: str = None):
        """Add or update a deadline."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO deadlines (deadline_id, title, description, deadline_date, 
                                  lms_name, course_id, activity_id, source, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(deadline_id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                deadline_date = excluded.deadline_date,
                location = excluded.location
        """, (deadline_id, title, description, deadline_date, lms_name, 
              course_id, activity_id, source, location))
        
        conn.commit()
        conn.close()
    
    def get_all_upcoming_deadlines(self, days_ahead: int = 30):
        """Get all upcoming deadlines from both activities and calendar events."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get deadlines from activities
        cursor.execute("""
            SELECT 
                a.activity_id as id,
                a.title,
                a.description,
                a.deadline as deadline_date,
                a.url,
                c.course_name,
                c.lms_name,
                'activity' as source,
                '' as location
            FROM activities a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.deadline IS NOT NULL
            AND a.deadline != ''
            AND datetime(a.deadline) >= datetime('now')
            AND datetime(a.deadline) <= datetime('now', '+' || ? || ' days')
        """, (days_ahead,))
        
        activity_deadlines = [dict(zip([desc[0] for desc in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        # Get deadlines from calendar/deadlines table
        cursor.execute("""
            SELECT 
                deadline_id as id,
                title,
                description,
                deadline_date,
                '' as url,
                COALESCE((SELECT course_name FROM courses WHERE course_id = d.course_id), '') as course_name,
                lms_name,
                source,
                location
            FROM deadlines d
            WHERE datetime(deadline_date) >= datetime('now')
            AND datetime(deadline_date) <= datetime('now', '+' || ? || ' days')
        """, (days_ahead,))
        
        calendar_deadlines = [dict(zip([desc[0] for desc in cursor.description], row)) 
                             for row in cursor.fetchall()]
        
        conn.close()
        
        # Combine and sort by date
        all_deadlines = activity_deadlines + calendar_deadlines
        all_deadlines.sort(key=lambda x: x.get('deadline_date', ''))
        
        return all_deadlines
    
    def get_scan_history(self, limit: int = 10):
        """Get recent scan history."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                lms_name,
                scan_time,
                courses_found,
                activities_found,
                new_activities,
                status,
                error_message
            FROM scan_history
            ORDER BY scan_time DESC
            LIMIT ?
        """, (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return history
