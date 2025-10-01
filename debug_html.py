"""
Debug script to inspect HTML structure of course links
"""
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def debug_ousl_html():
    """Debug OUSL course HTML structure"""
    print("🔍 Debugging OUSL HTML Structure\n")
    
    # Setup Chrome
    options = Options()
    # options.add_argument('--headless')  # Comment out to see the browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Login to OUSL
        print("Logging in to OUSL...")
        driver.get('https://oulms.ou.ac.lk/login/index.php')
        time.sleep(3)
        
        # Click Microsoft login
        try:
            ms_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'oauth2')]"))
            )
            ms_button.click()
            time.sleep(2)
        except:
            print("Could not find Microsoft login button")
        
        # Enter username
        username = os.getenv('OUSL_USERNAME')
        password = os.getenv('OUSL_PASSWORD')
        
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "loginfmt"))
            )
            username_field.send_keys(username)
            driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(2)
        except:
            print("Could not enter username")
        
        # Enter password
        try:
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "passwd"))
            )
            password_field.send_keys(password)
            driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(2)
        except:
            print("Could not enter password")
        
        # Stay signed in
        try:
            stay_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "idSIButton9"))
            )
            stay_button.click()
            time.sleep(3)
        except:
            print("Could not click stay signed in")
        
        # Navigate to dashboard
        driver.get('https://oulms.ou.ac.lk/my/')
        time.sleep(3)
        
        print("Parsing HTML...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find course links
        course_links = soup.find_all('a', href=re.compile(r'/course/view\.php\?id='))
        
        print(f"\nFound {len(course_links)} course links\n")
        print("=" * 80)
        
        # Show first 3 course links in detail
        for i, link in enumerate(course_links[:3], 1):
            print(f"\n🔍 Course Link #{i}:")
            print("-" * 80)
            print(f"Full HTML: {link.prettify()[:500]}...")
            print(f"\nAttributes: {link.attrs}")
            print(f"\nText content: '{link.get_text(strip=True)}'")
            
            # Check for spans
            spans = link.find_all('span')
            if spans:
                print(f"\nFound {len(spans)} span(s):")
                for j, span in enumerate(spans, 1):
                    print(f"  Span {j}: class={span.get('class')} | text='{span.get_text(strip=True)}'")
            
            # Check for coursename class
            coursename = link.find('span', class_='coursename')
            if coursename:
                print(f"\n✅ Found coursename span: '{coursename.get_text(strip=True)}'")
            
            print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close browser...")
        driver.quit()

if __name__ == '__main__':
    debug_ousl_html()
