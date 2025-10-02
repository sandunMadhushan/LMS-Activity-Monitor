# 📱 Ntfy.sh Mobile Push Notifications Setup Guide

Get instant push notifications on your phone when new LMS activities are detected!

## 🎯 What is Ntfy.sh?

Ntfy.sh is a free, open-source push notification service that sends instant alerts to your phone. No account needed, no costs, super simple!

## ⚡ Quick Setup (5 Minutes)

### Step 1: Install the Ntfy App

**Android:**
- Open Google Play Store
- Search for "ntfy"
- Install "ntfy - PUT/POST to your phone"
- [Direct Link](https://play.google.com/store/apps/details?id=io.heckel.ntfy)

**iOS:**
- Open Apple App Store
- Search for "ntfy"
- Install "ntfy"
- [Direct Link](https://apps.apple.com/us/app/ntfy/id1625396347)

### Step 2: Create Your Unique Topic

1. Open the Ntfy app
2. Tap the **"+"** button (bottom right)
3. Choose **"Subscribe to topic"**
4. Enter a **unique topic name** (see security note below)

**Example topic names:**
```
lms-monitor-sandun-xyz789-secret
lms-notify-p4k3-private-2024
ousl-rusl-monitor-abc123xyz
```

⚠️ **Security Note**: Anyone who knows your topic name can send you notifications! Make it long, random, and don't share it publicly.

### Step 3: Configure Your Project

#### For Local Development:

1. Open your `.env` file
2. Add these lines:
```bash
NTFY_TOPIC=your-unique-topic-name
NTFY_SERVER=https://ntfy.sh
```

Example:
```bash
NTFY_TOPIC=lms-monitor-sandun-xyz789-secret
NTFY_SERVER=https://ntfy.sh
```

#### For GitHub Actions:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these secrets:
   - Name: `NTFY_TOPIC`
   - Value: `your-unique-topic-name`

### Step 4: Test the Setup

#### Test from Terminal (Optional):
```bash
# Replace with YOUR topic name
curl -d "Test from terminal!" ntfy.sh/your-unique-topic-name
```

You should instantly get a notification on your phone! 📱

#### Test from the Dashboard:
1. Run your Flask app: `python app.py`
2. Go to the dashboard
3. Click "Test Email" (this will also test Ntfy if configured)

## 📲 What Notifications Will You Get?

### 1. New Activities Notification
When the scan finds new activities:
```
🎓 4 New LMS Activities!

📚 OUSL (3 new)
1. [RESOURCE] EEI4362 CAT01 2023/2024
   📖 EEI4362 Object Oriented Design
2. [ASSIGNMENT] Final Project
   📖 EEI5467 Software Testing
...
```

### 2. Deadline Reminders
For upcoming deadlines:
```
⏰ 2 URGENT Deadlines!

⚠️ URGENT:
⚡ DUE TODAY: Final Project
   📖 EEI4362 Object Oriented Design

📅 Coming up:
• Assignment 3 (in 5 days)
   📖 EEX4373 Data Science
```

## 🎨 Notification Features

Your notifications will include:
- ✅ **Priority levels**: Urgent deadlines get high priority
- ✅ **Emojis and icons**: 📚 🔔 ⚠️ for visual clarity
- ✅ **Click actions**: Tap to open your dashboard
- ✅ **Rich content**: Course names, activity types, deadlines
- ✅ **Instant delivery**: <1 second notification time

## 🔧 Advanced Configuration

### Using a Custom Ntfy Server

If you host your own Ntfy server:

```bash
NTFY_TOPIC=your-topic
NTFY_SERVER=https://your-ntfy-server.com
```

### Notification Priorities

The system automatically sets priorities:
- **Urgent**: Deadlines due today/tomorrow
- **High**: New activities, upcoming deadlines
- **Default**: Test notifications

## 🔒 Security Best Practices

1. **Use Long Topic Names**: `lms-monitor-xyz789-p4k3-secret` ✅
   Not: `lms-monitor` ❌

2. **Keep Topic Private**: Don't share in public repos or social media

3. **Use Random Characters**: Mix letters and numbers

4. **Change Periodically**: Update topic name if compromised

5. **No Sensitive Data**: Topic names are not encrypted in URLs

## 🛠️ Troubleshooting

### Not Receiving Notifications?

1. **Check topic name matches** in both app and `.env` file
2. **Verify internet connection** on your phone
3. **Check app permissions** (notifications allowed)
4. **Test with curl** to verify server connectivity
5. **Check GitHub Secrets** if using Actions

### Test Command:
```bash
curl -H "Title: Test" -d "Hello from LMS Monitor" ntfy.sh/your-topic
```

### Delayed Notifications?

- Ntfy is usually instant (<1 second)
- Check your phone's battery saver settings
- Ensure Ntfy app is not restricted in background

### Too Many Notifications?

The system only notifies for:
- ✅ NEW activities (not existing ones)
- ✅ Deadlines within 7 days
- ✅ Twice daily scans (9 AM & 9 PM)

## 📊 Notification Schedule

| Time | Notification Type | Trigger |
|------|------------------|---------|
| 9:00 AM SLT | New Activities | If found during scan |
| 9:00 AM SLT | Deadline Reminders | If within 7 days |
| 9:00 PM SLT | New Activities | If found during scan |
| 9:00 PM SLT | Deadline Reminders | If within 7 days |

## 🆚 Comparison: Email vs Ntfy

| Feature | Email | Ntfy |
|---------|-------|------|
| Speed | 30-60 seconds | <1 second ⚡ |
| Setup Time | 5 minutes | 2 minutes |
| Reliability | 99% | 99%+ |
| Rich Content | ✅ HTML emails | ✅ Formatted text |
| Click Actions | ✅ Links | ✅ Deep links |
| Cost | Free | Free |
| Spam Issues | Sometimes | Never |

**Recommendation**: Use BOTH! Email for detailed info, Ntfy for instant alerts.

## 📱 Mobile App Features

The Ntfy app offers:
- 🔔 **Sound customization** per topic
- 🎨 **Custom icons** for different topics
- 🔕 **Quiet hours** to avoid night notifications
- 💾 **Notification history** (kept for 12 hours)
- 🔗 **Quick actions** from notifications
- 📍 **Multiple topics** in one app

## 🔗 Useful Links

- **Ntfy Documentation**: https://docs.ntfy.sh
- **Android App**: https://play.google.com/store/apps/details?id=io.heckel.ntfy
- **iOS App**: https://apps.apple.com/us/app/ntfy/id1625396347
- **Web Interface**: https://ntfy.sh/app
- **GitHub**: https://github.com/binwiederhier/ntfy

## 💡 Pro Tips

1. **Test Before Deploying**: Always test locally before GitHub Actions
2. **Use Web Interface**: Subscribe at https://ntfy.sh/app for desktop notifications
3. **Custom Sounds**: Set unique sounds for LMS notifications in the app
4. **Quiet Hours**: Configure app to silence notifications at night
5. **Battery Saving**: Ntfy uses very little battery (efficient websockets)

## 🎉 You're All Set!

Once configured, you'll get instant notifications whenever:
- 📚 New course materials are posted
- 📝 New assignments are added
- ⏰ Deadlines are approaching
- 🔔 Any LMS activity is detected

**No more missing important updates!** 🚀

---

**Need help?** Check the main `README.md` or open an issue on GitHub.
