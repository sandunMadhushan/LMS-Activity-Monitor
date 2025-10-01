"""
Lightweight test - skips Chrome check
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Quick Configuration Check\n")

# Check credentials
checks = {
    'OUSL_USERNAME': os.getenv('OUSL_USERNAME'),
    'OUSL_PASSWORD': os.getenv('OUSL_PASSWORD'),
    'RJTA_USERNAME': os.getenv('RJTA_USERNAME'),
    'RJTA_PASSWORD': os.getenv('RJTA_PASSWORD'),
    'EMAIL_SENDER': os.getenv('EMAIL_SENDER'),
    'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
    'EMAIL_RECIPIENT': os.getenv('EMAIL_RECIPIENT'),
    'SECRET_KEY': os.getenv('SECRET_KEY')
}

all_good = True
for key, value in checks.items():
    if not value or value.startswith('your_'):
        print(f"❌ {key} - Not configured")
        all_good = False
    else:
        masked = value[:3] + '*' * min(len(value) - 3, 10)
        print(f"✅ {key} - {masked}")

print("\n" + "="*50)
if all_good:
    print("✅ All credentials configured!")
    print("\n📝 Next step: Install Google Chrome")
    print("   Download from: https://www.google.com/chrome/")
else:
    print("❌ Some credentials missing")
    print("   Edit your .env file")
