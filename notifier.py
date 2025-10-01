import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Notifier:
    """Handle email notifications for new LMS activities."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('EMAIL_SENDER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        self.recipient_email = os.getenv('EMAIL_RECIPIENT')
    
    def send_notification(self, activities: List[Dict[str, Any]]) -> bool:
        """Send email notification about new activities."""
        if not activities:
            print("No new activities to notify about.")
            return True
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("Email configuration incomplete. Skipping notification.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🔔 LMS Update: {len(activities)} New Activities'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create email body
            html_body = self._create_html_email(activities)
            text_body = self._create_text_email(activities)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email notification sent successfully! ({len(activities)} new activities)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email notification: {e}")
            return False
    
    def _create_html_email(self, activities: List[Dict[str, Any]]) -> str:
        """Create HTML formatted email body."""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .activity {{
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin-bottom: 20px;
                    background: #f9f9f9;
                    border-radius: 5px;
                }}
                .activity-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }}
                .activity-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .activity-type {{
                    background: #667eea;
                    color: white;
                    padding: 3px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                .course-name {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 5px;
                }}
                .lms-badge {{
                    background: #764ba2;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    margin-left: 10px;
                }}
                .deadline {{
                    color: #d32f2f;
                    font-weight: bold;
                    margin-top: 10px;
                }}
                .description {{
                    margin-top: 10px;
                    padding: 10px;
                    background: white;
                    border-radius: 3px;
                }}
                .view-button {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 16px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 New LMS Activities Detected!</h1>
                    <p>You have {len(activities)} new activities in your courses</p>
                    <p style="font-size: 14px; opacity: 0.9;">Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        # Group activities by LMS
        activities_by_lms = {}
        for activity in activities:
            lms = activity.get('lms_name', 'Unknown')
            if lms not in activities_by_lms:
                activities_by_lms[lms] = []
            activities_by_lms[lms].append(activity)
        
        for lms, lms_activities in activities_by_lms.items():
            html += f"<h2 style='color: #764ba2; margin-top: 30px;'>📚 {lms}</h2>"
            
            for activity in lms_activities:
                activity_type = activity.get('activity_type', 'unknown').upper()
                title = activity.get('title', 'Untitled')
                course_name = activity.get('course_name', 'Unknown Course')
                description = activity.get('description', '')
                url = activity.get('url', '#')
                deadline = activity.get('deadline')
                
                # Truncate description
                if description and len(description) > 300:
                    description = description[:297] + '...'
                
                html += f"""
                <div class="activity">
                    <div class="activity-header">
                        <div>
                            <span class="activity-type">{activity_type}</span>
                        </div>
                    </div>
                    <div class="activity-title">{title}</div>
                    <div class="course-name">
                        📖 {course_name}
                    </div>
                """
                
                if deadline:
                    html += f'<div class="deadline">⏰ Deadline: {deadline}</div>'
                
                if description:
                    html += f'<div class="description">{description}</div>'
                
                if url and url != '#':
                    html += f'<a href="{url}" class="view-button">View in Moodle →</a>'
                
                html += '</div>'
        
        html += """
                <div class="footer">
                    <p>This is an automated notification from your LMS Activity Monitor.</p>
                    <p>You're receiving this because new content was detected in your enrolled courses.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_text_email(self, activities: List[Dict[str, Any]]) -> str:
        """Create plain text email body."""
        text = f"""
LMS ACTIVITY NOTIFICATION
{'=' * 60}

You have {len(activities)} new activities in your courses!
Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Group by LMS
        activities_by_lms = {}
        for activity in activities:
            lms = activity.get('lms_name', 'Unknown')
            if lms not in activities_by_lms:
                activities_by_lms[lms] = []
            activities_by_lms[lms].append(activity)
        
        for lms, lms_activities in activities_by_lms.items():
            text += f"\n{lms}\n{'-' * 60}\n"
            
            for i, activity in enumerate(lms_activities, 1):
                activity_type = activity.get('activity_type', 'unknown').upper()
                title = activity.get('title', 'Untitled')
                course_name = activity.get('course_name', 'Unknown Course')
                description = activity.get('description', '')
                url = activity.get('url', '')
                deadline = activity.get('deadline')
                
                text += f"\n{i}. [{activity_type}] {title}\n"
                text += f"   Course: {course_name}\n"
                
                if deadline:
                    text += f"   ⏰ Deadline: {deadline}\n"
                
                if description:
                    desc_short = description[:200] + '...' if len(description) > 200 else description
                    text += f"   Description: {desc_short}\n"
                
                if url:
                    text += f"   URL: {url}\n"
                
                text += "\n"
        
        text += f"\n{'=' * 60}\n"
        text += "This is an automated notification from your LMS Activity Monitor.\n"
        
        return text
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration."""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = '✅ LMS Monitor - Test Email'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            body = """
            This is a test email from your LMS Activity Monitor!
            
            If you're receiving this, your email configuration is working correctly.
            
            The system will now check your Moodle courses twice daily (9 AM and 9 PM)
            and send you notifications about any new activities.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print("✅ Test email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
    
    def send_deadline_reminders(self, deadlines: List[Dict[str, Any]]) -> bool:
        """Send email notification about upcoming deadlines."""
        if not deadlines:
            print("No upcoming deadlines to notify about.")
            return True
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("Email configuration incomplete. Skipping notification.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'⏰ Upcoming Deadlines: {len(deadlines)} Due Soon!'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create email body
            html_body = self._create_deadline_html_email(deadlines)
            text_body = self._create_deadline_text_email(deadlines)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Deadline reminder email sent successfully! ({len(deadlines)} deadlines)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send deadline reminder: {e}")
            return False
    
    def _create_deadline_html_email(self, deadlines: List[Dict[str, Any]]) -> str:
        """Create HTML formatted deadline reminder email."""
        from datetime import datetime, timezone, timedelta
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .deadline-item {{
                    border-left: 4px solid #f5576c;
                    padding: 15px;
                    margin-bottom: 20px;
                    background: #fff5f5;
                    border-radius: 5px;
                }}
                .urgent {{
                    border-left-color: #d32f2f;
                    background: #ffebee;
                }}
                .deadline-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }}
                .deadline-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #d32f2f;
                }}
                .source-badge {{
                    background: #f5576c;
                    color: white;
                    padding: 3px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    text-transform: uppercase;
                }}
                .course-name {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 5px;
                }}
                .lms-badge {{
                    background: #764ba2;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 3px;
                    font-size: 11px;
                    margin-left: 10px;
                }}
                .deadline-date {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #d32f2f;
                    margin-top: 10px;
                }}
                .time-remaining {{
                    background: #fff3cd;
                    padding: 8px;
                    border-radius: 3px;
                    margin-top: 10px;
                    color: #856404;
                    font-weight: bold;
                }}
                .description {{
                    margin-top: 10px;
                    padding: 10px;
                    background: white;
                    border-radius: 3px;
                }}
                .view-button {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 16px;
                    background: #f5576c;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Upcoming Deadline Reminders!</h1>
                    <p>You have {len(deadlines)} deadlines approaching</p>
                    <p style="font-size: 14px; opacity: 0.9;">Reminder sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        # Group deadlines by LMS
        deadlines_by_lms = {}
        for deadline in deadlines:
            lms = deadline.get('lms_name', 'Unknown')
            if lms not in deadlines_by_lms:
                deadlines_by_lms[lms] = []
            deadlines_by_lms[lms].append(deadline)
        
        for lms, lms_deadlines in deadlines_by_lms.items():
            html += f"<h2 style='color: #f5576c; margin-top: 30px;'>📚 {lms}</h2>"
            
            for deadline in lms_deadlines:
                source = deadline.get('source', 'activity').capitalize()
                title = deadline.get('title', 'Untitled')
                course_name = deadline.get('course_name', '')
                description = deadline.get('description', '')
                url = deadline.get('url', '#')
                deadline_date = deadline.get('deadline_date', '')
                location = deadline.get('location', '')
                
                # Calculate time remaining
                try:
                    if deadline_date:
                        deadline_dt = datetime.fromisoformat(deadline_date.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        time_diff = deadline_dt - now
                        days = time_diff.days
                        hours = time_diff.seconds // 3600
                        
                        if days < 0:
                            time_remaining = "⚠️ OVERDUE!"
                            urgent_class = "urgent"
                        elif days == 0:
                            time_remaining = f"⚡ Due TODAY in {hours} hours!"
                            urgent_class = "urgent"
                        elif days == 1:
                            time_remaining = f"📅 Due TOMORROW"
                            urgent_class = "urgent"
                        elif days < 7:
                            time_remaining = f"📅 Due in {days} days"
                            urgent_class = ""
                        else:
                            time_remaining = f"📅 Due in {days} days"
                            urgent_class = ""
                    else:
                        time_remaining = ""
                        urgent_class = ""
                except:
                    time_remaining = ""
                    urgent_class = ""
                
                # Truncate description
                if description and len(description) > 300:
                    description = description[:297] + '...'
                
                html += f"""
                <div class="deadline-item {urgent_class}">
                    <div class="deadline-header">
                        <div>
                            <span class="source-badge">{source}</span>
                        </div>
                    </div>
                    <div class="deadline-title">{title}</div>
                """
                
                if course_name:
                    html += f'<div class="course-name">📖 {course_name}</div>'
                
                if deadline_date:
                    try:
                        deadline_dt = datetime.fromisoformat(deadline_date.replace('Z', '+00:00'))
                        # Convert to Colombo time
                        colombo_tz = timezone(timedelta(hours=5, minutes=30))
                        local_dt = deadline_dt.astimezone(colombo_tz)
                        formatted_date = local_dt.strftime('%B %d, %Y at %I:%M %p')
                        html += f'<div class="deadline-date">🗓️ {formatted_date}</div>'
                    except:
                        html += f'<div class="deadline-date">🗓️ {deadline_date}</div>'
                
                if time_remaining:
                    html += f'<div class="time-remaining">{time_remaining}</div>'
                
                if location:
                    html += f'<div style="margin-top: 10px;">📍 Location: {location}</div>'
                
                if description:
                    html += f'<div class="description">{description}</div>'
                
                if url and url != '#':
                    html += f'<a href="{url}" class="view-button">View in Moodle →</a>'
                
                html += '</div>'
        
        html += """
                <div class="footer">
                    <p>This is an automated deadline reminder from your LMS Activity Monitor.</p>
                    <p>Stay on top of your assignments and never miss a deadline! 🎯</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_deadline_text_email(self, deadlines: List[Dict[str, Any]]) -> str:
        """Create plain text deadline reminder email."""
        from datetime import datetime, timezone, timedelta
        
        text = f"""
UPCOMING DEADLINE REMINDERS
{'=' * 60}

You have {len(deadlines)} deadlines approaching!
Reminder sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Group by LMS
        deadlines_by_lms = {}
        for deadline in deadlines:
            lms = deadline.get('lms_name', 'Unknown')
            if lms not in deadlines_by_lms:
                deadlines_by_lms[lms] = []
            deadlines_by_lms[lms].append(deadline)
        
        for lms, lms_deadlines in deadlines_by_lms.items():
            text += f"\n{lms}\n{'-' * 60}\n"
            
            for i, deadline in enumerate(lms_deadlines, 1):
                source = deadline.get('source', 'activity').upper()
                title = deadline.get('title', 'Untitled')
                course_name = deadline.get('course_name', '')
                description = deadline.get('description', '')
                url = deadline.get('url', '')
                deadline_date = deadline.get('deadline_date', '')
                location = deadline.get('location', '')
                
                text += f"\n{i}. [{source}] {title}\n"
                
                if course_name:
                    text += f"   Course: {course_name}\n"
                
                if deadline_date:
                    try:
                        deadline_dt = datetime.fromisoformat(deadline_date.replace('Z', '+00:00'))
                        colombo_tz = timezone(timedelta(hours=5, minutes=30))
                        local_dt = deadline_dt.astimezone(colombo_tz)
                        formatted_date = local_dt.strftime('%B %d, %Y at %I:%M %p')
                        text += f"   🗓️  Deadline: {formatted_date}\n"
                        
                        # Calculate time remaining
                        now = datetime.now(timezone.utc)
                        time_diff = deadline_dt - now
                        days = time_diff.days
                        
                        if days < 0:
                            text += f"   ⚠️  OVERDUE!\n"
                        elif days == 0:
                            text += f"   ⚡ Due TODAY!\n"
                        elif days == 1:
                            text += f"   📅 Due TOMORROW\n"
                        else:
                            text += f"   📅 Due in {days} days\n"
                    except:
                        text += f"   🗓️  Deadline: {deadline_date}\n"
                
                if location:
                    text += f"   📍 Location: {location}\n"
                
                if description:
                    desc_short = description[:200] + '...' if len(description) > 200 else description
                    text += f"   Description: {desc_short}\n"
                
                if url:
                    text += f"   URL: {url}\n"
                
                text += "\n"
        
        text += f"\n{'=' * 60}\n"
        text += "Stay on top of your assignments and never miss a deadline!\n"
        
        return text
