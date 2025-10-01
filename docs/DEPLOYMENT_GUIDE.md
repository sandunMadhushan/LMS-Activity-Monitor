# 🚀 Deployment Guide

This guide explains how to deploy the LMS scraper to various cloud platforms so you can access it from anywhere.

## 📋 Table of Contents
- [Recommended: Render.com](#recommended-rendercom)
- [Alternative: PythonAnywhere](#alternative-pythonanywhere)
- [Alternative: Railway](#alternative-railway)
- [VPS Setup (DigitalOcean/AWS)](#vps-setup-digitaloceanaws)

---

## ⭐ Recommended: Render.com

**Best for**: Free tier, auto-deployment from GitHub, scheduled tasks

### Prerequisites
- GitHub account
- Render account (sign up at https://render.com)

### Step 1: Prepare Repository
1. Make sure all files are committed to GitHub:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin master
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Deploy Web Service (Dashboard)

1. Click **"New +"** → **"Web Service"**
2. Connect your `lms-scraper` repository
3. Configure the service:
   - **Name**: `lms-scraper-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. Add Environment Variables (click "Advanced"):
   ```
   OUSL_USERNAME = your_ousl_username
   OUSL_PASSWORD = your_ousl_password
   RUSL_USERNAME = your_rusl_username
   RUSL_PASSWORD = your_rusl_password
   EMAIL_SENDER = your_email@gmail.com
   EMAIL_PASSWORD = your_app_password
   EMAIL_RECIPIENT = recipient@email.com
   SMTP_SERVER = smtp.gmail.com
   SMTP_PORT = 587
   ```

5. Click **"Create Web Service"**

6. Wait for deployment (5-10 minutes)

7. Your dashboard will be available at: `https://lms-scraper-dashboard.onrender.com`

### Step 4: Set Up Cron Job (Scheduled Scraping)

1. Click **"New +"** → **"Cron Job"**
2. Connect the same repository
3. Configure:
   - **Name**: `lms-scraper-job`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Command**: `python scraper.py --headless True`
   - **Schedule**: `0 1,13 * * *` (runs at 1 AM and 1 PM UTC)

4. Add the same Environment Variables as Step 3

5. Click **"Create Cron Job"**

### ⚠️ Important Notes for Render:

**Database Persistence**:
- Free tier web services have **ephemeral storage** (resets on restart)
- Cron jobs don't share filesystem with web service
- **Solution**: Use a persistent database

**Recommended Fix**: Add PostgreSQL database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `lms-database`
3. Free tier: 90 days, then $7/month
4. Update your code to use PostgreSQL instead of SQLite
5. Or use **Render Disks** (persistent storage, $1/GB/month)

**Alternative**: Keep using GitHub Actions for scraping (as you already have), and deploy only the dashboard to Render.

---

## 🐍 Alternative: PythonAnywhere

**Best for**: Simple Python apps, educational use, small projects

### Limitations
- Free tier: Limited CPU hours
- External network access restricted on free tier (can't scrape external sites)
- **Recommendation**: Use paid tier ($5/month) for full scraping capability

### Setup Steps

1. **Sign up**: Go to https://www.pythonanywhere.com

2. **Upload Code**:
   - Clone from GitHub in PythonAnywhere console:
   ```bash
   git clone https://github.com/sandunMadhushan/lms-scraper.git
   cd lms-scraper
   pip install -r requirements.txt
   ```

3. **Set up Web App**:
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask"
   - Point to your `app.py` file
   - Set working directory: `/home/yourusername/lms-scraper`

4. **Configure Environment Variables**:
   - Edit WSGI file to load .env:
   ```python
   from dotenv import load_dotenv
   load_dotenv('/home/yourusername/lms-scraper/.env')
   ```

5. **Set up Scheduled Task**:
   - Go to "Tasks" tab
   - Add scheduled task: `python /home/yourusername/lms-scraper/scraper.py --headless True`
   - Schedule: Daily at 9:00 and 21:00

6. **Access**: Your app will be at `https://yourusername.pythonanywhere.com`

---

## 🚂 Alternative: Railway

**Best for**: Modern deployment, fair pricing, persistent storage

### Setup Steps

1. **Sign up**: Go to https://railway.app

2. **Deploy from GitHub**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `lms-scraper`

3. **Configure Web Service**:
   - Railway auto-detects Python
   - Add start command: `gunicorn app:app`
   - Add environment variables

4. **Add Persistent Volume**:
   - Go to service settings
   - Add volume: Mount path `/app/data`
   - Update database path in code to `/app/data/lms_data.db`

5. **Set up Cron Job**:
   - Add new service: "Cron"
   - Command: `python scraper.py --headless True`
   - Schedule: `0 1,13 * * *`

6. **Access**: Railway provides a URL like `https://lms-scraper-production.up.railway.app`

---

## 💻 VPS Setup (DigitalOcean/AWS)

**Best for**: Full control, production deployments, advanced users

### Option 1: DigitalOcean Droplet ($6/month)

1. **Create Droplet**:
   - Sign up at https://digitalocean.com
   - Create Ubuntu 22.04 droplet
   - Choose $6/month plan

2. **SSH into server**:
   ```bash
   ssh root@your_droplet_ip
   ```

3. **Install dependencies**:
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python and required packages
   apt install -y python3 python3-pip python3-venv git nginx
   
   # Install Chrome and ChromeDriver
   wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
   sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
   apt update
   apt install -y google-chrome-stable
   
   # Install ChromeDriver
   CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
   CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION%%.*})
   wget "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
   unzip chromedriver-linux64.zip
   mv chromedriver-linux64/chromedriver /usr/local/bin/
   chmod +x /usr/local/bin/chromedriver
   rm -rf chromedriver-linux64.zip chromedriver-linux64
   ```

4. **Clone and setup project**:
   ```bash
   # Create app user
   adduser --disabled-password --gecos "" lmsapp
   su - lmsapp
   
   # Clone repository
   git clone https://github.com/sandunMadhushan/lms-scraper.git
   cd lms-scraper
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Create .env file
   nano .env
   # (Add your credentials)
   ```

5. **Set up systemd service** (as root):
   ```bash
   # Create service file
   cat > /etc/systemd/system/lms-scraper.service << 'EOF'
   [Unit]
   Description=LMS Scraper Dashboard
   After=network.target
   
   [Service]
   User=lmsapp
   WorkingDirectory=/home/lmsapp/lms-scraper
   Environment="PATH=/home/lmsapp/lms-scraper/venv/bin"
   ExecStart=/home/lmsapp/lms-scraper/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   EOF
   
   # Start service
   systemctl daemon-reload
   systemctl enable lms-scraper
   systemctl start lms-scraper
   ```

6. **Configure Nginx**:
   ```bash
   cat > /etc/nginx/sites-available/lms-scraper << 'EOF'
   server {
       listen 80;
       server_name your_domain.com;  # or droplet IP
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   EOF
   
   ln -s /etc/nginx/sites-available/lms-scraper /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

7. **Set up cron job** (as lmsapp user):
   ```bash
   crontab -e
   # Add:
   0 1,13 * * * cd /home/lmsapp/lms-scraper && /home/lmsapp/lms-scraper/venv/bin/python scraper.py --headless True
   ```

8. **Access**: Visit `http://your_droplet_ip`

### Optional: Add SSL with Let's Encrypt
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your_domain.com
```

---

## 🔐 Security Considerations

1. **Never commit credentials**: Use environment variables
2. **Use strong passwords**: For LMS accounts
3. **Enable 2FA**: On your hosting provider
4. **Keep dependencies updated**: Run `pip list --outdated` regularly
5. **Monitor logs**: Check for suspicious activity
6. **Use HTTPS**: Enable SSL certificate
7. **Restrict access**: Consider adding authentication to dashboard

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid Plan | Best For |
|----------|-----------|-----------|----------|
| **Render** | ✅ (with limits) | $7/month | Easy start, auto-deploy |
| **Railway** | $5 credit/month | Pay as you go | Modern, fair pricing |
| **PythonAnywhere** | ✅ (limited) | $5/month | Simple Python apps |
| **Heroku** | ❌ (discontinued) | $7-25/month | Enterprise features |
| **DigitalOcean** | ❌ | $6/month | Full control, scalable |
| **AWS EC2** | ✅ (12 months) | Variable | Enterprise, scalable |
| **GitHub Actions** | ✅ (2000 min/month) | $0 | Scheduled jobs only |

---

## 🎯 Recommendation Summary

**Best Overall**: **Render.com**
- Free tier to start
- Easy GitHub integration
- Automatic deployments
- Good for learning and small projects

**Best for Production**: **DigitalOcean Droplet**
- Full control
- Predictable $6/month cost
- Persistent storage
- Can scale as needed

**Best for Just Monitoring**: **Keep using GitHub Actions**
- Already set up
- Completely free
- No hosting needed
- Access database via artifacts or repository

**Hybrid Approach** (Recommended):
1. Use **GitHub Actions** for scheduled scraping (free, reliable)
2. Deploy **dashboard only** to Render/Railway (lightweight, fast)
3. Store database in GitHub repo (simple) or PostgreSQL (scalable)

---

## 🆘 Troubleshooting

### "Module not found" errors
- Ensure all dependencies in `requirements.txt`
- Reinstall: `pip install -r requirements.txt`

### ChromeDriver issues on hosting
- Some free tiers don't support Chrome
- Use GitHub Actions for scraping instead
- Only deploy dashboard to web host

### Database not persisting
- Free web services often have ephemeral storage
- Use persistent database (PostgreSQL)
- Or store in GitHub (commit after each scan)

### App sleeping/slow on free tier
- Render free tier sleeps after 15 min inactivity
- First request takes ~30 seconds to wake up
- Upgrade to paid plan for always-on

---

## 📚 Next Steps

1. Choose your hosting platform
2. Follow the setup guide above
3. Test the deployment
4. Set up monitoring/alerts
5. Consider adding authentication for security

Need help? Check the other docs in the `/docs` folder!
