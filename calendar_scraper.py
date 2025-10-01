import requests
from icalendar import Calendar
from datetime import datetime, timezone, timedelta
import re
from typing import List, Dict

class CalendarScraper:
    def __init__(self):
        self.ousl_calendar_url = "https://oulms.ou.ac.lk/calendar/export_execute.php?userid=19900&authtoken=9e92461354ae8674632a70fdaaadde2280af8dfb&preset_what=all&preset_time=custom"
        self.rjta_calendar_url = "https://lms.aps.rjt.ac.lk/calendar/export_execute.php?userid=17234&authtoken=55a6286965183ea25486870ac8006fab00c9c038&preset_what=all&preset_time=custom"
    
    def fetch_calendar_events(self, url: str, lms_name: str) -> List[Dict]:
        """Fetch and parse iCal calendar events."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            cal = Calendar.from_ical(response.content)
            events = []
            
            now = datetime.now(timezone.utc)
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    summary = str(component.get('summary', 'Untitled Event'))
                    dtstart = component.get('dtstart')
                    description = str(component.get('description', ''))
                    location = str(component.get('location', ''))
                    
                    if dtstart:
                        # Convert to datetime if it's a date
                        if hasattr(dtstart.dt, 'date'):
                            event_date = dtstart.dt
                        else:
                            event_date = datetime.combine(dtstart.dt, datetime.min.time())
                            event_date = event_date.replace(tzinfo=timezone.utc)
                        
                        # Only include future events
                        if event_date > now:
                            events.append({
                                'title': summary,
                                'date': event_date,
                                'description': description,
                                'location': location,
                                'lms': lms_name,
                                'source': 'calendar'
                            })
            
            # Sort by date
            events.sort(key=lambda x: x['date'])
            return events
            
        except Exception as e:
            print(f"Error fetching calendar from {lms_name}: {e}")
            return []
    
    def get_all_calendar_events(self) -> List[Dict]:
        """Get calendar events from both OUSL and RJTA."""
        ousl_events = self.fetch_calendar_events(self.ousl_calendar_url, 'OUSL')
        rjta_events = self.fetch_calendar_events(self.rjta_calendar_url, 'RJTA')
        
        all_events = ousl_events + rjta_events
        all_events.sort(key=lambda x: x['date'])
        
        return all_events
    
    def extract_dates_from_text(self, text: str) -> List[datetime]:
        """Extract dates from activity descriptions."""
        dates = []
        
        if not text:
            return dates
        
        # Pattern 1: "by 15th October 2025", "before 20-10-2025", "due on 2025-10-15"
        patterns = [
            r'(?:by|before|due on|due|deadline|submit by)\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
            r'(?:by|before|due on|due|deadline|submit by)\s+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
            r'(?:by|before|due on|due|deadline|submit by)\s+(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})',  # 15th October 2025
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    
                    # Try to parse the date
                    if len(groups) == 3:
                        if groups[0].isdigit() and groups[1].isdigit() and len(groups[2]) == 4:
                            # DD-MM-YYYY or YYYY-MM-DD
                            if len(groups[0]) == 4:  # YYYY-MM-DD
                                date = datetime(int(groups[0]), int(groups[1]), int(groups[2]), tzinfo=timezone.utc)
                            else:  # DD-MM-YYYY
                                date = datetime(int(groups[2]), int(groups[1]), int(groups[0]), tzinfo=timezone.utc)
                            dates.append(date)
                        elif groups[1].isalpha():  # 15th October 2025
                            # Parse month name
                            months = {
                                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                                'september': 9, 'october': 10, 'november': 11, 'december': 12,
                                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                            }
                            month = months.get(groups[1].lower())
                            if month:
                                date = datetime(int(groups[2]), month, int(groups[0]), tzinfo=timezone.utc)
                                dates.append(date)
                except (ValueError, IndexError):
                    continue
        
        return dates

if __name__ == "__main__":
    scraper = CalendarScraper()
    events = scraper.get_all_calendar_events()
    print(f"Found {len(events)} upcoming calendar events")
    for event in events[:5]:
        print(f"- {event['title']} ({event['lms']}) - {event['date']}")
