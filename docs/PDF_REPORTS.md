# PDF Report Generation

## Overview

The LMS Activity Monitor now automatically generates and emails beautiful PDF reports containing:
- ✅ Summary statistics
- 📚 New activities from both OUSL and RUSL
- ⏰ Upcoming deadlines (next 30 days)

## Features

### Automatic Generation
- PDF reports are generated automatically after each scan
- Reports are emailed to you along with the regular notifications
- Reports are saved locally in the `reports/` directory

### Report Contents

1. **Header**
   - Report title
   - Generation date and time (Sri Lanka Time)

2. **Summary Section**
   - Total courses
   - Total activities
   - New activities count
   - Last scan time

3. **New Activities**
   - Grouped by university (OUSL/RUSL)
   - Activity type, course name, title, and posted date
   - Color-coded tables
   - Up to 20 activities per university

4. **Upcoming Deadlines**
   - Next 30 days
   - LMS, title, course, and deadline date
   - Sorted by date
   - Color-coded warning table

5. **Footer**
   - Dashboard link
   - Auto-generated timestamp

## How It Works

### Workflow

1. **Scan Completes** → LMS activities and deadlines are collected
2. **PDF Generation** → Beautiful PDF report is created
3. **Email Delivery** → PDF is attached and sent to your email
4. **Local Storage** → PDF is saved in `reports/` directory

### Schedule

- **9:00 AM** Sri Lanka Time (GitHub Actions)
- **9:00 PM** Sri Lanka Time (GitHub Actions)

After each scan, you'll receive:
1. 📧 Regular email notification with activity details
2. 📱 Mobile push notification (if configured)
3. 📊 PDF report attachment with comprehensive overview

## Configuration

### Requirements

Already included in `requirements.txt`:
- `reportlab==4.0.7` - PDF generation
- `Pillow==10.1.0` - Image handling

### Email Setup

Same email configuration used for regular notifications:

```bash
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_RECIPIENT=recipient@example.com
```

## PDF Styling

### Design Elements

- **Colors**: Gradient purple/blue theme matching dashboard
- **Tables**: Professional with alternating row colors
- **Typography**: Clean Helvetica font
- **Layout**: Letter size (8.5" × 11")

### File Naming

Reports are named with timestamp:
```
LMS_Report_20251006_093000.pdf
```

Format: `LMS_Report_YYYYMMDD_HHMMSS.pdf`

## Manual Generation

You can also generate reports manually by running:

```bash
python pdf_report.py
```

This will:
1. Connect to the database
2. Gather latest activities and deadlines
3. Generate PDF in `reports/` directory
4. Show the file path

## File Locations

- **Generated PDFs**: `reports/LMS_Report_*.pdf`
- **Generator Code**: `pdf_report.py`
- **Email Integration**: `notifier.py` (send_email_with_pdf method)

## Troubleshooting

### PDF Not Generated

**Check**:
1. Dependencies installed: `pip install reportlab Pillow`
2. `reports/` directory exists (auto-created)
3. Database has activities/deadlines

### Email Not Received

**Check**:
1. Email configuration in `.env`
2. Gmail App Password (not regular password)
3. Check spam folder
4. Verify PDF file exists in `reports/`

### PDF Looks Broken

**Solution**:
- Update dependencies: `pip install --upgrade reportlab Pillow`
- Check console for ReportLab errors
- Ensure data in database is valid

## Example Output

### Email Subject
```
📊 LMS Activity Report - 5 New Activities, 3 Deadlines
```

### Email Body
```
Hello!

Here's your latest LMS Activity Report from the automated monitoring system.

📊 Report Summary:
• 5 new activities detected
• 3 upcoming deadlines (next 30 days)

Please find the detailed PDF report attached to this email.

Dashboard: https://lms-activity-monitor.up.railway.app
```

### PDF Sections

1. **Title Page**
   - "LMS Activity Report"
   - Friday, October 6, 2025

2. **Summary Table**
   - Total Courses: 12
   - Total Activities: 156
   - New Activities: 5
   - Last Scan: 8 hours ago

3. **OUSL Activities**
   - 3 new assignments
   - 1 new resource
   - 1 new forum post

4. **Upcoming Deadlines**
   - 3 deadlines in next 30 days
   - Sorted by date

## Benefits

✅ **Professional Format** - Clean, printable PDF reports
✅ **Email Delivery** - Automatically sent to your inbox
✅ **Comprehensive** - All info in one place
✅ **Archivable** - Save reports for reference
✅ **Mobile-Friendly** - Open on any device

## Future Enhancements

Potential future features:
- Charts and graphs
- Trend analysis
- Weekly summary reports
- Custom report templates
- Multiple recipients

---

**Generated PDFs are automatically attached to your daily notification emails!** 📧📊
