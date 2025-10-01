# LMS Scraper - Calendar & Deadline Enhancement

## What's Been Implemented:

### 1. Calendar Integration ✅
- **calendar_scraper.py** - New file that fetches iCal events from both OUSL and RJTA
  - Parses calendar URLs using icalendar library
  - Extracts upcoming events with dates, titles, descriptions
  - Can extract dates from activity descriptions using regex patterns

### 2. Database Updates ✅
- **New Table: `deadlines`** - Stores calendar events and scraped deadlines
  - Fields: deadline_id, title, description, deadline_date, lms_name, course_id, activity_id, source, location
  - Source can be: 'calendar', 'activity', or 'scraped'

- **New Methods in database.py:**
  - `add_deadline()` - Add/update deadline entries
  - `get_all_upcoming_deadlines()` - Get combined deadlines from activities, calendar, and scraping
  - `get_scan_history()` - Already existed, used for sidebar

### 3. App.py Updates ✅
- Added `calendar_scraper` import and initialization
- Updated `index()` route to use `get_all_upcoming_deadlines()` (combines all sources)
- **New API endpoint: `/api/sync-calendar`** - Syncs calendar events from both LMS calendars

### 4. Frontend Updates ✅
- Added **"Sync Calendar" button** in dashboard header
- Added `syncCalendar()` JavaScript function
- Timezone fixes applied (Asia/Colombo GMT+5:30) to all time displays

## Calendar URLs (Already Configured):
- **OUSL**: https://oulms.ou.ac.lk/calendar/export_execute.php?userid=19900&authtoken=9e92461354ae8674632a70fdaaadde2280af8dfb&preset_what=all&preset_time=custom
- **RJTA**: https://lms.aps.rjt.ac.lk/calendar/export_execute.php?userid=17234&authtoken=55a6286965183ea25486870ac8006fab00c9c038&preset_what=all&preset_time=custom

## How It Works:

### Syncing Calendar Events:
1. Click "Sync Calendar" button on dashboard
2. Fetches events from both OUSL and RJTA calendar URLs
3. Stores them in `deadlines` table with source='calendar'
4. Dashboard automatically shows combined deadlines from:
   - Activity deadlines (from scraping)
   - Calendar events (from iCal feeds)
   - Future: Scraped dates from activity descriptions

### Deadline Detection:
The system now shows deadlines from multiple sources:
- **Activity deadlines**: Already captured when scraping Moodle activities
- **Calendar events**: Fetched from iCal URLs (assignments, quizzes, events)
- **Scraped dates** (Ready for enhancement): `extract_dates_from_text()` can find dates like:
  - "by 15th October 2025"
  - "submit before 20-10-2025"
  - "due on 2025-10-15"
  - "deadline: 15 Oct 2025"

## Next Steps / Enhancements Needed:

### 1. Enhance Activity Scraping to Extract Dates
Update `scraper.py` to use `calendar_scraper.extract_dates_from_text()`:
```python
from calendar_scraper import CalendarScraper
cal_scraper = CalendarScraper()

# When processing activity description:
dates = cal_scraper.extract_dates_from_text(activity_description)
if dates:
    # Store the earliest date as deadline
    deadline_id = f"scraped_{activity_id}_{dates[0].isoformat()}"
    db.add_deadline(
        deadline_id=deadline_id,
        title=f"{activity_title} (Select Group)",
        description=activity_description,
        deadline_date=dates[0].isoformat(),
        lms_name=lms_name,
        course_id=course_id,
        activity_id=activity_id,
        source='scraped'
    )
```

### 2. Add Scan History Sidebar (Optional)
Create a sidebar on the right side of dashboard showing recent scans:
- Time of scan
- LMS scanned  
- Courses found
- Activities found
- Status (success/error)

### 3. Improve Deadline Display
Update the deadline cards to show:
- Source badge (Calendar/Activity/Scraped)
- Different icons for different sources
- Better date formatting

## Testing:

1. **Test Calendar Sync:**
```bash
python -c "from calendar_scraper import CalendarScraper; cs = CalendarScraper(); events = cs.get_all_calendar_events(); print(f'Found {len(events)} events')"
```

2. **Test Database:**
```bash
sqlite3 lms_data.db "SELECT * FROM deadlines LIMIT 5;"
```

3. **Test in Browser:**
- Visit dashboard: http://127.0.0.1:5000
- Click "Sync Calendar" button
- Check "Upcoming Deadlines" section
- Should see events from calendar + activities

## Dependencies Installed:
- `icalendar` - For parsing iCal calendar feeds
- `python-dateutil` - For date parsing
- `requests` - Already installed

## Files Modified/Created:
1. ✅ calendar_scraper.py (NEW)
2. ✅ database.py (UPDATED - added deadlines table & methods)
3. ✅ app.py (UPDATED - calendar integration)
4. ✅ templates/index.html (UPDATED - sync button & JS)

## Known Limitations:
1. Date extraction from descriptions is regex-based (may miss some formats)
2. Scan history sidebar not yet added to UI (data is available)
3. Activity scraping doesn't yet call extract_dates_from_text()
4. Calendar sync is manual (click button) - could be automated

## Recommended Next Actions:
1. Test the calendar sync functionality
2. Add date extraction to scraper.py activity processing
3. Create scan history sidebar component
4. Style the deadline cards to show source badges
5. Add automated calendar sync (e.g., every scan)
