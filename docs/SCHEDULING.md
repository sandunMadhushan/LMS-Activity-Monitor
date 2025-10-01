# Automatic Scheduling Guide

## Overview

The LMS monitoring system now includes automatic background task scheduling to keep your calendar events synchronized without manual intervention.

## Features

### 🗓️ Automatic Calendar Sync

Calendar events from both OUSL and RUSL are automatically synced **twice daily**:

- **9:00 AM** - Morning sync to catch overnight updates
- **9:00 PM** - Evening sync to catch daytime updates

### How It Works

1. **Background Scheduler**: Uses APScheduler to run tasks in the background
2. **Calendar Fetching**: Retrieves events from both university iCal URLs
3. **Database Storage**: Stores events in the deadlines table
4. **Deadline Tracking**: Events appear in the "Upcoming Deadlines" section

## Technical Details

### Implementation

- **Library**: APScheduler 3.10.4
- **Scheduler Type**: BackgroundScheduler (runs in separate thread)
- **Trigger**: CronTrigger for time-based execution
- **Timezone**: Asia/Colombo (GMT+5:30)

### Files

- `scheduler.py` - Scheduler implementation and job definitions
- `app.py` - Scheduler initialization and integration

### Code Structure

```python
# Scheduler starts automatically when Flask app starts
scheduler = TaskScheduler()
scheduler.start()

# Jobs are scheduled using cron syntax
CronTrigger(hour='9,21', minute='0')  # 9 AM and 9 PM
```

## API Endpoints

### Get Scheduled Jobs

```bash
GET /api/scheduled-jobs
```

**Response:**

```json
{
  "success": true,
  "jobs": [
    {
      "id": "calendar_sync",
      "name": "Sync Calendar Events",
      "next_run": "2025-10-02 09:00 AM"
    }
  ]
}
```

### Manual Sync (Still Available)

```bash
POST /api/sync-calendar
```

**Response:**

```json
{
  "success": true,
  "message": "Synced 10 calendar events successfully!"
}
```

## Logs

The scheduler logs its activity:

```
INFO:scheduler:📅 Scheduled calendar sync: Daily at 9:00 AM and 9:00 PM
INFO:scheduler:✅ Scheduler started successfully
INFO:scheduler:🗓️  Starting scheduled calendar sync...
INFO:scheduler:✅ Calendar sync completed! Synced 10 events at 2025-10-02 09:00 AM
```

## Monitoring

### Dashboard Indicator

- The "Sync Calendar" button now shows **🕒 Auto** to indicate automatic scheduling
- Hover tooltip displays: "Auto-syncs daily at 9 AM & 9 PM"
- Info banner below stats shows scheduling details

### Verify Scheduler Status

Check if scheduler is running:

```bash
curl http://localhost:5000/api/scheduled-jobs
```

### Check Logs

Monitor the Flask app logs for scheduler activity:

```bash
python app.py
# Look for "Scheduled calendar sync" messages
```

## Customization

### Change Sync Times

Edit `scheduler.py`:

```python
# Current: 9 AM and 9 PM
CronTrigger(hour='9,21', minute='0')

# Example: Every 4 hours (6 AM, 10 AM, 2 PM, 6 PM, 10 PM)
CronTrigger(hour='6,10,14,18,22', minute='0')

# Example: Three times daily (8 AM, 2 PM, 8 PM)
CronTrigger(hour='8,14,20', minute='0')
```

### Add More Scheduled Tasks

Add additional jobs in `scheduler.py`:

```python
def start(self):
    # Existing calendar sync
    self.scheduler.add_job(...)

    # New job example
    self.scheduler.add_job(
        func=self.some_other_job,
        trigger=CronTrigger(hour='12', minute='0'),  # Daily at noon
        id='job_id',
        name='Job Name'
    )
```

## Benefits

### 1. **Always Up-to-Date**

Calendar events are refreshed automatically, ensuring deadlines are current.

### 2. **Zero Manual Effort**

No need to remember to click "Sync Calendar" - it happens automatically.

### 3. **Consistent Schedule**

Syncs at the same time every day, providing reliable updates.

### 4. **Email Reminders**

Combined with the deadline reminder system, you'll get timely email notifications about upcoming events.

## Troubleshooting

### Scheduler Not Starting

**Symptom**: No "Scheduler started" message in logs

**Solutions**:

1. Check APScheduler is installed: `pip install APScheduler==3.10.4`
2. Verify imports in `app.py`
3. Check for Python errors on startup

### Jobs Not Running

**Symptom**: Next run time passes but job doesn't execute

**Solutions**:

1. Verify scheduler is running: Check `/api/scheduled-jobs`
2. Check system time is correct
3. Review logs for errors during job execution

### Calendar Sync Fails

**Symptom**: Error in logs during scheduled sync

**Solutions**:

1. Verify calendar URLs are valid in `calendar_scraper.py`
2. Check internet connection
3. Ensure database is accessible

## Production Deployment

### Important Notes

1. **Server Time**: Ensure server timezone is correct
2. **Process Manager**: Use a process manager (PM2, systemd) to keep Flask running
3. **Logging**: Configure proper logging to file for monitoring
4. **Health Checks**: Monitor scheduler status via API endpoint

### Example PM2 Configuration

```json
{
  "name": "lms-monitor",
  "script": "app.py",
  "interpreter": "python3",
  "instances": 1,
  "autorestart": true,
  "watch": false,
  "max_memory_restart": "500M"
}
```

## Future Enhancements

Potential additions to the scheduler:

- ✅ Calendar sync (implemented)
- 📋 Automatic LMS scanning at scheduled times
- 📧 Scheduled deadline reminder emails
- 🧹 Database cleanup/maintenance tasks
- 📊 Weekly report generation
- 🔄 Periodic health checks

## Summary

The automatic calendar sync scheduler:

- ✅ Runs in the background
- ✅ Syncs twice daily (9 AM & 9 PM)
- ✅ Requires no manual intervention
- ✅ Provides status via API
- ✅ Logs all activity
- ✅ Integrates seamlessly with existing features

Users can still manually trigger syncs anytime via the dashboard button!
