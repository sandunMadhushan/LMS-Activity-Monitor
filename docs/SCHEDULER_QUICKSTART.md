# Quick Start: Automatic Calendar Sync

## What Was Implemented

The calendar sync button now triggers **automatically twice daily**:

- 🌅 **9:00 AM** - Morning sync
- 🌙 **9:00 PM** - Evening sync

## Files Created/Modified

### New Files

- `scheduler.py` - Background task scheduler with APScheduler

### Modified Files

- `app.py` - Integrated scheduler on startup
- `templates/index.html` - Updated button with "Auto" indicator
- `requirements.txt` - Added APScheduler==3.10.4

## How It Works

```
Flask App Starts
      ↓
Scheduler Initializes
      ↓
Jobs Are Scheduled (9 AM, 9 PM)
      ↓
Scheduler Runs in Background
      ↓
At Scheduled Time:
  - Fetch calendar events from OUSL & RUSL
  - Store in deadlines table
  - Log activity
```

## Verify It's Working

1. **Check Logs**

```bash
python app.py
# Look for: "📅 Scheduled calendar sync: Daily at 9:00 AM and 9:00 PM"
```

2. **Check Scheduled Jobs**

```bash
curl http://localhost:5000/api/scheduled-jobs
# Returns: Next run time
```

3. **Check Dashboard**

- Button now shows "🕒 Auto"
- Info banner explains scheduling
- Hover tooltip on button

## Manual Sync Still Available

Users can still click "Sync Calendar" button anytime to trigger immediate sync!

## Next Run Time

Current next run: **October 2, 2025 at 9:00 AM**

## Benefits

✅ No manual intervention needed
✅ Always up-to-date deadlines
✅ Works alongside existing features
✅ Integrates with email reminders
✅ Automatic and reliable

## Customization

To change sync times, edit `scheduler.py`:

```python
CronTrigger(hour='9,21', minute='0')  # 9 AM & 9 PM
```

Change to your preferred times!
