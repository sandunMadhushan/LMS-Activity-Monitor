"""
Test script to verify the LMS Monitor setup.
Run this to check if everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    print("\n🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} - Need Python 3.9+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    required = [
        'flask',
        'requests',
        'bs4',
        'selenium',
        'dotenv',
        'webdriver_manager'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing.append(package)
    
    if missing:
        print_warning("Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print_error(".env file not found")
        print_warning("Run: cp .env.example .env")
        print_warning("Then edit .env with your credentials")
        return False
    
    print_success(".env file exists")
    
    load_dotenv()
    
    required_vars = [
        'OUSL_USERNAME',
        'OUSL_PASSWORD',
        'RUSL_USERNAME',
        'RUSL_PASSWORD',
        'EMAIL_SENDER',
        'EMAIL_PASSWORD',
        'EMAIL_RECIPIENT'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print_error(f"{var} not configured")
            missing.append(var)
        else:
            # Show only first 3 chars for security
            masked = value[:3] + '*' * (len(value) - 3)
            print_success(f"{var} = {masked}")
    
    if missing:
        print_warning("Please configure missing variables in .env")
        return False
    
    return True

def check_chrome():
    """Check if Chrome/Chromium is installed."""
    print("\n🔍 Checking Chrome...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        
        print_info("Installing/checking ChromeDriver...")
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.quit()
        
        print_success("Chrome/ChromeDriver working")
        return True
        
    except Exception as e:
        print_error(f"Chrome setup failed: {e}")
        print_warning("Install Google Chrome from: https://google.com/chrome")
        return False

def check_database():
    """Check if database can be initialized."""
    print("\n🔍 Checking database...")
    
    try:
        from database import Database
        db = Database()
        stats = db.get_stats()
        print_success("Database initialized")
        print_info(f"Total courses: {stats['total_courses']}")
        print_info(f"Total activities: {stats['total_activities']}")
        return True
    except Exception as e:
        print_error(f"Database error: {e}")
        return False

def check_email_config():
    """Check if email configuration is valid."""
    print("\n🔍 Checking email configuration...")
    
    load_dotenv()
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = os.getenv('SMTP_PORT', '587')
    sender = os.getenv('EMAIL_SENDER')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not sender or not password:
        print_error("Email credentials not configured")
        return False
    
    # Basic validation
    if '@' not in sender:
        print_error("Invalid email address")
        return False
    
    if len(password) < 8:
        print_error("Email password too short (use App Password)")
        return False
    
    print_success(f"Email sender: {sender}")
    print_success(f"SMTP: {smtp_server}:{smtp_port}")
    print_info("Note: To actually test email sending, run: python scraper.py --test-email")
    
    return True

def check_file_structure():
    """Check if all required files exist."""
    print("\n🔍 Checking file structure...")
    
    required_files = [
        'scraper.py',
        'database.py',
        'notifier.py',
        'app.py',
        'requirements.txt',
        '.env.example',
        'README.md'
    ]
    
    required_dirs = [
        'templates',
        'static',
        '.github/workflows'
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_error(f"{file} missing")
            all_good = False
    
    for dir in required_dirs:
        if os.path.isdir(dir):
            print_success(f"{dir}/")
        else:
            print_error(f"{dir}/ missing")
            all_good = False
    
    return all_good

def main():
    """Run all checks."""
    print("=" * 60)
    print("🎓 LMS Activity Monitor - System Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
        ("File Structure", check_file_structure),
        ("Chrome/Selenium", check_chrome),
        ("Database", check_database),
        ("Email Configuration", check_email_config)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Check failed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    
    if passed == total:
        print_success(f"All checks passed! ({passed}/{total})")
        print_info("\n🚀 You're ready to go!")
        print_info("Next steps:")
        print("   1. Run: python scraper.py --test-email")
        print("   2. Run: python scraper.py --headless False")
        print("   3. Run: python app.py")
    else:
        print_warning(f"Some checks failed ({passed}/{total} passed)")
        print_info("\n📖 Please review the errors above and:")
        print("   1. Fix any missing dependencies")
        print("   2. Configure your .env file")
        print("   3. Install Google Chrome if needed")
        print("   4. Check the SETUP_GUIDE.md for help")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
