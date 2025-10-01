import os
import sys
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

from database import Database
from notifier import Notifier
from calendar_scraper import CalendarScraper

load_dotenv()

class MoodleScraper:
    """Scrape Moodle LMS instances for course activities."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.db = Database()
        self.notifier = Notifier()
        self.calendar_scraper = CalendarScraper()
    
    def setup_driver(self):
        """Setup Selenium WebDriver."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Try to use system chromedriver first (for CI environments), fallback to webdriver_manager
        try:
            # Check if chromedriver is in PATH (CI environment)
            import shutil
            import os
            if shutil.which('chromedriver'):
                print("Using system ChromeDriver")
                service = Service('chromedriver')
            else:
                print("Using ChromeDriverManager")
                driver_path = ChromeDriverManager().install()
                print(f"ChromeDriver path: {driver_path}")
                
                # Handle Chrome for Testing structure (chromedriver-linux64/chromedriver)
                if 'chromedriver-linux64' in driver_path and not driver_path.endswith('chromedriver'):
                    # The path might point to THIRD_PARTY_NOTICES, so find the actual chromedriver
                    driver_dir = os.path.dirname(driver_path)
                    actual_driver = os.path.join(driver_dir, 'chromedriver')
                    if os.path.exists(actual_driver):
                        driver_path = actual_driver
                        print(f"Corrected path: {driver_path}")
                
                service = Service(driver_path)
        except Exception as e:
            print(f"Error detecting ChromeDriver, using ChromeDriverManager: {e}")
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def close_driver(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
    
    def generate_activity_id(self, course_id: str, title: str, activity_type: str) -> str:
        """Generate a unique ID for an activity."""
        unique_string = f"{course_id}_{title}_{activity_type}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _extract_and_store_deadline(self, activity_id: str, course_id: str, 
                                    title: str, description: str, lms_name: str):
        """Extract deadline from activity text and store in deadlines table."""
        try:
            # Combine title and description for searching
            search_text = f"{title} {description or ''}"
            
            # Extract dates using calendar scraper's method
            extracted_dates = self.calendar_scraper.extract_dates_from_text(search_text)
            
            if extracted_dates:
                # Use the first/earliest extracted date
                deadline_date = extracted_dates[0]
                
                # Generate unique deadline ID
                deadline_id = f"scraped_{activity_id}_{deadline_date.isoformat()}"
                
                # Store in deadlines table
                self.db.add_deadline(
                    deadline_id=deadline_id,
                    title=title,
                    description=description or '',
                    deadline_date=deadline_date.isoformat(),
                    lms_name=lms_name,
                    course_id=course_id,
                    activity_id=activity_id,
                    source='scraped',
                    location=''
                )
                print(f"      📅 Deadline extracted: {deadline_date.strftime('%Y-%m-%d')}")
        except Exception as e:
            # Silently fail - deadline extraction is optional
            pass
    
    def scrape_ousl(self) -> Dict[str, Any]:
        """Scrape Open University of Sri Lanka Moodle."""
        print("\n🔍 Scraping OUSL Moodle...")
        
        # Ensure driver is set up
        if not self.driver:
            self.setup_driver()
        
        username = os.getenv('OUSL_USERNAME')
        password = os.getenv('OUSL_PASSWORD')
        
        if not username or not password:
            print("❌ OUSL credentials not found in environment variables")
            return {'success': False, 'error': 'Missing credentials'}
        
        try:
            # Navigate to login page
            self.driver.get('https://oulms.ou.ac.lk/login/index.php')
            time.sleep(2)
            
            # Look for OAuth/SSO login button
            try:
                # Try to find the SSO login button
                sso_buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'oauth2')]")
                if sso_buttons:
                    print("Found SSO login, clicking...")
                    sso_buttons[0].click()
                    time.sleep(3)
                
                # Fill in credentials on SSO page
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                password_field = self.driver.find_element(By.ID, "password")
                
                username_field.send_keys(username)
                password_field.send_keys(password)
                
                # Submit form
                login_button = self.driver.find_element(By.ID, "kc-login")
                login_button.click()
                
            except Exception as e:
                print(f"SSO login attempt failed, trying standard login: {e}")
                # Fallback to standard Moodle login if available
                try:
                    username_field = self.driver.find_element(By.ID, "username")
                    password_field = self.driver.find_element(By.ID, "password")
                    username_field.send_keys(username)
                    password_field.send_keys(password)
                    
                    login_button = self.driver.find_element(By.ID, "loginbtn")
                    login_button.click()
                except:
                    raise
            
            # Wait for dashboard to load
            time.sleep(5)
            
            # Check if login was successful
            if "login" in self.driver.current_url.lower():
                print("❌ Login failed - still on login page")
                return {'success': False, 'error': 'Login failed'}
            
            print("✅ Logged in successfully!")
            
            # Scrape courses
            courses = self._scrape_ousl_courses()
            
            return {
                'success': True,
                'lms_name': 'OUSL',
                'courses': courses
            }
            
        except Exception as e:
            print(f"❌ Error scraping OUSL: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _scrape_ousl_courses(self) -> List[Dict[str, Any]]:
        """Scrape all courses from OUSL dashboard."""
        courses = []
        
        try:
            # Navigate to dashboard/my courses
            self.driver.get('https://oulms.ou.ac.lk/my/')
            time.sleep(3)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all course cards - Modern Moodle uses these classes
            # Try multiple selectors for different Moodle versions
            course_cards = (
                soup.find_all('div', class_=re.compile(r'coursebox|course-listitem|course-info-container|dashboard-card')) or
                soup.find_all('div', class_='card-body') or
                soup.find_all('div', class_=re.compile(r'card.*course'))
            )
            
            # Also get all course links as fallback
            course_links = soup.find_all('a', href=re.compile(r'/course/view\.php\?id='))
            
            seen_course_ids = set()
            
            # First try: Extract from course cards
            if course_cards:
                print(f"  Found {len(course_cards)} course cards")
                for card in course_cards:
                    try:
                        # Find the course link within the card
                        link = card.find('a', href=re.compile(r'/course/view\.php\?id='))
                        if not link:
                            continue
                        
                        course_url = link.get('href')
                        if not course_url:
                            continue
                        
                        # Make URL absolute
                        if course_url.startswith('/'):
                            course_url = 'https://oulms.ou.ac.lk' + course_url
                        
                        # Extract course ID
                        course_id_match = re.search(r'id=(\d+)', course_url)
                        if not course_id_match:
                            continue
                        
                        course_id = f"ousl_{course_id_match.group(1)}"
                        
                        if course_id in seen_course_ids:
                            continue
                        seen_course_ids.add(course_id)
                        
                        # Try to extract course name from the card
                        course_name = None
                        
                        # Method 1: Look for <a> with class "aalink coursename" (OUSL specific)
                        coursename_link = card.find('a', class_='aalink coursename')
                        if coursename_link:
                            # Get all text but filter out sr-only content
                            # Remove all sr-only elements first
                            for sr_only in coursename_link.find_all(class_='sr-only'):
                                sr_only.decompose()
                            for hidden in coursename_link.find_all(class_='hidden'):
                                hidden.decompose()
                            
                            course_name = coursename_link.get_text(strip=True)
                            if course_name:
                                print(f"  [DEBUG] Found name from aalink coursename: '{course_name}'")
                        
                        # Method 2: Look for heading elements (h1-h5)
                        if not course_name:
                            for tag in ['h3', 'h4', 'h5', 'h2']:
                                heading = card.find(tag)
                                if heading:
                                    course_name = heading.get_text(strip=True)
                                    if course_name and course_name.lower() != 'course image':
                                        print(f"  [DEBUG] Found name from {tag}: '{course_name}'")
                                        break
                        
                        # Method 3: Look for common Moodle course name classes
                        if not course_name:
                            name_elements = (
                                card.find('span', class_=re.compile(r'coursename|multiline')) or
                                card.find('div', class_=re.compile(r'coursename|course-name')) or
                                card.find('span', class_='text-truncate')
                            )
                            
                            if name_elements:
                                course_name = name_elements.get_text(strip=True)
                                print(f"  [DEBUG] Found name from class: '{course_name}'")
                        
                        if not course_name or course_name.lower() in ['course image', 'course name', 'course is starred']:
                            print(f"  [DEBUG] Skipping - no valid course name found in card")
                            continue
                        
                        print(f"  📚 Found course: {course_name}")
                        
                        # Add to database
                        self.db.add_course(course_id, 'OUSL', course_name, course_url)
                        
                        # Scrape course activities
                        activities = self._scrape_course_activities(course_url, course_id, 'OUSL')
                        
                        courses.append({
                            'course_id': course_id,
                            'name': course_name,
                            'url': course_url,
                            'activities': activities
                        })
                        
                        time.sleep(2)  # Be respectful
                        
                    except Exception as e:
                        print(f"  ⚠️ Error processing course card: {e}")
                        continue
            
            # Fallback: Try direct link extraction if no cards found
            if not courses and course_links:
                print(f"  Trying fallback method with {len(course_links)} links")
                
                for link in course_links:
                    try:
                        course_url = link.get('href')
                        if not course_url:
                            continue
                        
                        # Make URL absolute
                        if course_url.startswith('/'):
                            course_url = 'https://oulms.ou.ac.lk' + course_url
                        
                        # Extract course ID
                        course_id_match = re.search(r'id=(\d+)', course_url)
                        if not course_id_match:
                            continue
                        
                        course_id = f"ousl_{course_id_match.group(1)}"
                        
                        if course_id in seen_course_ids:
                            continue
                        seen_course_ids.add(course_id)
                        
                        # Try multiple ways to extract course name
                        course_name = None
                        
                        # Method 1: Try to find span with coursename class
                        coursename_span = link.find('span', class_='coursename')
                        if coursename_span:
                            course_name = coursename_span.get_text(strip=True)
                        
                        # Method 2: Try to find any span inside the link
                        if not course_name:
                            spans = link.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                if text and text.lower() != 'course image' and len(text) > 3:
                                    course_name = text
                                    break
                        
                        # Method 3: Get all text from link, excluding "Course image"
                        if not course_name:
                            course_name = link.get_text(strip=True)
                            if 'Course image' in course_name:
                                course_name = course_name.replace('Course image', '').strip()
                        
                        # Method 4: Try to get from title or aria-label attribute
                        if not course_name or len(course_name) < 3:
                            course_name = link.get('title') or link.get('aria-label')
                        
                        if not course_name or len(course_name) < 3 or course_name.lower() == 'course image':
                            continue
                        
                        print(f"  📚 Found course: {course_name}")
                        
                        # Add to database
                        self.db.add_course(course_id, 'OUSL', course_name, course_url)
                        
                        # Scrape course activities
                        activities = self._scrape_course_activities(course_url, course_id, 'OUSL')
                        
                        courses.append({
                            'course_id': course_id,
                            'name': course_name,
                            'url': course_url,
                            'activities': activities
                        })
                        
                        time.sleep(2)  # Be respectful
                        
                    except Exception as e:
                        print(f"  ⚠️ Error processing course: {e}")
                        continue
            
            print(f"✅ Found {len(courses)} courses")
            
        except Exception as e:
            print(f"❌ Error scraping courses: {e}")
        
        return courses
    
    def scrape_rusl(self) -> Dict[str, Any]:
        """Scrape Rajarata University Moodle."""
        print("\n🔍 Scraping Rajarata University Moodle...")
        
        # Ensure driver is set up
        if not self.driver:
            self.setup_driver()
        
        username = os.getenv('RUSL_USERNAME')
        password = os.getenv('RUSL_PASSWORD')
        
        if not username or not password:
            print("❌ RUSL credentials not found in environment variables")
            return {'success': False, 'error': 'Missing credentials'}
        
        try:
            # Navigate to login page
            self.driver.get('https://lms.aps.rjt.ac.lk/login/index.php')
            time.sleep(2)
            
            # Fill in login form
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            login_button = self.driver.find_element(By.ID, "loginbtn")
            login_button.click()
            
            # Wait for dashboard to load
            time.sleep(5)
            
            # Check if login was successful
            if "login" in self.driver.current_url.lower():
                print("❌ Login failed - still on login page")
                return {'success': False, 'error': 'Login failed'}
            
            print("✅ Logged in successfully!")
            
            # Scrape courses
            courses = self._scrape_rusl_courses()
            
            return {
                'success': True,
                'lms_name': 'RUSL',
                'courses': courses
            }
            
        except Exception as e:
            print(f"❌ Error scraping RUSL: {e}")
            return {'success': False, 'error': str(e)}
    
    def _scrape_rusl_courses(self) -> List[Dict[str, Any]]:
        """Scrape all courses from RUSL dashboard."""
        courses = []
        
        try:
            # Navigate to dashboard
            self.driver.get('https://lms.aps.rjt.ac.lk/my/')
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all course cards - Modern Moodle uses these classes
            course_cards = (
                soup.find_all('div', class_=re.compile(r'coursebox|course-listitem|course-info-container|dashboard-card')) or
                soup.find_all('div', class_='card-body') or
                soup.find_all('div', class_=re.compile(r'card.*course'))
            )
            
            # Also get all course links as fallback
            course_links = soup.find_all('a', href=re.compile(r'/course/view\.php\?id='))
            
            seen_course_ids = set()
            
            # First try: Extract from course cards
            if course_cards:
                print(f"  Found {len(course_cards)} course cards")
                for card in course_cards:
                    try:
                        # Find the course link within the card
                        link = card.find('a', href=re.compile(r'/course/view\.php\?id='))
                        if not link:
                            continue
                        
                        course_url = link.get('href')
                        if not course_url:
                            continue
                        
                        if course_url.startswith('/'):
                            course_url = 'https://lms.aps.rjt.ac.lk' + course_url
                        
                        course_id_match = re.search(r'id=(\d+)', course_url)
                        if not course_id_match:
                            continue
                        
                        course_id = f"rusl_{course_id_match.group(1)}"
                        
                        if course_id in seen_course_ids:
                            continue
                        seen_course_ids.add(course_id)
                        
                        # Try to extract course name from the card
                        course_name = None
                        
                        # Method 1: Look for <a> with class "aalink coursename" (Moodle standard)
                        coursename_link = card.find('a', class_='aalink coursename')
                        if coursename_link:
                            # Get all text but filter out sr-only content
                            for sr_only in coursename_link.find_all(class_='sr-only'):
                                sr_only.decompose()
                            for hidden in coursename_link.find_all(class_='hidden'):
                                hidden.decompose()
                            
                            course_name = coursename_link.get_text(strip=True)
                            if course_name:
                                print(f"  [DEBUG] Found name from aalink coursename: '{course_name}'")
                        
                        # Method 2: Look for common Moodle course name classes
                        if not course_name:
                            name_elements = (
                                card.find('span', class_=re.compile(r'coursename|multiline')) or
                                card.find('h3', class_=re.compile(r'coursename|course-name')) or
                                card.find('div', class_=re.compile(r'coursename|course-name')) or
                                card.find('span', class_='text-truncate')
                            )
                            
                            if name_elements:
                                course_name = name_elements.get_text(strip=True)
                        
                        if not course_name or course_name.lower() in ['course image', 'course name', 'course is starred']:
                            continue
                        
                        print(f"  📚 Found course: {course_name}")
                        
                        self.db.add_course(course_id, 'RUSL', course_name, course_url)
                        
                        activities = self._scrape_course_activities(course_url, course_id, 'RUSL')
                        
                        courses.append({
                            'course_id': course_id,
                            'name': course_name,
                            'url': course_url,
                            'activities': activities
                        })
                        
                        time.sleep(2)  # Be respectful
                        
                    except Exception as e:
                        print(f"  ⚠️ Error processing course card: {e}")
                        continue
            
            # Fallback: Try direct link extraction if no cards found
            if not courses and course_links:
                print(f"  Trying fallback method with {len(course_links)} links")
                
                for link in course_links:
                    try:
                        course_url = link.get('href')
                        if not course_url:
                            continue
                        
                        if course_url.startswith('/'):
                            course_url = 'https://lms.aps.rjt.ac.lk' + course_url
                        
                        course_id_match = re.search(r'id=(\d+)', course_url)
                        if not course_id_match:
                            continue
                        
                        course_id = f"rusl_{course_id_match.group(1)}"
                        
                        if course_id in seen_course_ids:
                            continue
                        seen_course_ids.add(course_id)
                        
                        # Try multiple ways to extract course name
                        course_name = None
                        
                        # Method 1: Try to find span with coursename class
                        coursename_span = link.find('span', class_='coursename')
                        if coursename_span:
                            course_name = coursename_span.get_text(strip=True)
                        
                        # Method 2: Try to find any span inside the link
                        if not course_name:
                            spans = link.find_all('span')
                            for span in spans:
                                text = span.get_text(strip=True)
                                if text and text.lower() != 'course image' and len(text) > 3:
                                    course_name = text
                                    break
                        
                        # Method 3: Get all text from link, excluding "Course image"
                        if not course_name:
                            course_name = link.get_text(strip=True)
                            if 'Course image' in course_name:
                                course_name = course_name.replace('Course image', '').strip()
                        
                        # Method 4: Try to get from title or aria-label attribute
                        if not course_name or len(course_name) < 3:
                            course_name = link.get('title') or link.get('aria-label')
                        
                        if not course_name or len(course_name) < 3 or course_name.lower() == 'course image':
                            continue
                        
                        print(f"  📚 Found course: {course_name}")
                        
                        self.db.add_course(course_id, 'RUSL', course_name, course_url)
                        
                        activities = self._scrape_course_activities(course_url, course_id, 'RUSL')
                        
                        courses.append({
                            'course_id': course_id,
                            'name': course_name,
                            'url': course_url,
                            'activities': activities
                        })
                        
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"  ⚠️ Error processing course: {e}")
                        continue
            
            print(f"✅ Found {len(courses)} courses")
            
        except Exception as e:
            print(f"❌ Error scraping courses: {e}")
        
        return courses
    
    def _scrape_course_activities(self, course_url: str, course_id: str, lms_name: str = 'OUSL') -> List[Dict[str, Any]]:
        """Scrape all activities from a course page."""
        activities = []
        
        try:
            self.driver.get(course_url)
            time.sleep(3)
            
            # Expand all sections
            try:
                expand_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[data-action='expand']")
                for btn in expand_buttons:
                    try:
                        btn.click()
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass
            
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all activity items
            activity_items = soup.find_all('li', class_=re.compile(r'activity|modtype'))
            
            for item in activity_items:
                try:
                    # Extract activity type
                    activity_type = 'unknown'
                    classes = item.get('class', [])
                    for cls in classes:
                        if 'modtype_' in cls:
                            activity_type = cls.replace('modtype_', '')
                            break
                    
                    # Find activity link
                    link = item.find('a', href=True)
                    if not link:
                        continue
                    
                    title = link.get_text(strip=True)
                    url = link.get('href')
                    
                    if url.startswith('/'):
                        base_url = course_url.split('/course/')[0]
                        url = base_url + url
                    
                    # Try to find description
                    description = ''
                    desc_div = item.find('div', class_=re.compile(r'description|summary'))
                    if desc_div:
                        description = desc_div.get_text(strip=True)
                    
                    # Try to find deadline
                    deadline = None
                    deadline_spans = item.find_all('span', class_=re.compile(r'due|deadline'))
                    for span in deadline_spans:
                        deadline_text = span.get_text(strip=True)
                        if deadline_text:
                            deadline = deadline_text
                            break
                    
                    # Generate unique activity ID
                    activity_id = self.generate_activity_id(course_id, title, activity_type)
                    
                    # Add to database and check if new
                    is_new = self.db.add_activity(
                        activity_id=activity_id,
                        course_id=course_id,
                        activity_type=activity_type,
                        title=title,
                        description=description,
                        url=url,
                        deadline=deadline
                    )
                    
                    # Extract deadline dates from title and description
                    self._extract_and_store_deadline(
                        activity_id=activity_id,
                        course_id=course_id,
                        title=title,
                        description=description,
                        lms_name=lms_name
                    )
                    
                    if is_new:
                        print(f"    🆕 New: [{activity_type}] {title}")
                    
                    activities.append({
                        'activity_id': activity_id,
                        'type': activity_type,
                        'title': title,
                        'url': url,
                        'description': description,
                        'deadline': deadline,
                        'is_new': is_new
                    })
                    
                except Exception as e:
                    print(f"    ⚠️ Error processing activity: {e}")
                    continue
            
            print(f"    Found {len(activities)} activities")
            
        except Exception as e:
            print(f"  ❌ Error scraping course activities: {e}")
        
        return activities
    
    def run_full_scan(self):
        """Run a complete scan of all LMS instances."""
        print("=" * 60)
        print("🚀 Starting LMS Full Scan")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.setup_driver()
        
        results = {
            'ousl': None,
            'rusl': None,
            'total_new_activities': 0
        }
        
        try:
            # Scrape OUSL
            ousl_result = self.scrape_ousl()
            results['ousl'] = ousl_result
            
            if ousl_result['success']:
                total_courses = len(ousl_result['courses'])
                total_activities = sum(len(c['activities']) for c in ousl_result['courses'])
                new_activities = sum(sum(1 for a in c['activities'] if a.get('is_new')) 
                                   for c in ousl_result['courses'])
                
                self.db.add_scan_history('OUSL', total_courses, total_activities, 
                                        new_activities, 'success')
                results['total_new_activities'] += new_activities
            else:
                self.db.add_scan_history('OUSL', 0, 0, 0, 'failed', 
                                        ousl_result.get('error'))
            
            # Scrape RUSL
            rusl_result = self.scrape_rusl()
            results['rusl'] = rusl_result
            
            if rusl_result['success']:
                total_courses = len(rusl_result['courses'])
                total_activities = sum(len(c['activities']) for c in rusl_result['courses'])
                new_activities = sum(sum(1 for a in c['activities'] if a.get('is_new')) 
                                   for c in rusl_result['courses'])
                
                self.db.add_scan_history('RUSL', total_courses, total_activities, 
                                        new_activities, 'success')
                results['total_new_activities'] += new_activities
            else:
                self.db.add_scan_history('RUSL', 0, 0, 0, 'failed', 
                                        rusl_result.get('error'))
            
        except Exception as e:
            print(f"❌ Error during scan: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.close_driver()
            
            # Send notifications if there are new activities (moved to finally block)
            try:
                if results['total_new_activities'] > 0:
                    print(f"\n📧 Sending notification for {results['total_new_activities']} new activities...")
                    new_activities = self.db.get_new_activities()
                    
                    if self.notifier.send_notification(new_activities):
                        # Mark as notified
                        activity_ids = [a['activity_id'] for a in new_activities]
                        self.db.mark_activities_as_notified(activity_ids)
                        print("✅ Notifications sent and activities marked as notified")
                    else:
                        print("⚠️ Failed to send notifications")
                else:
                    print("\n✅ No new activities found.")
                
                # Send deadline reminders for upcoming deadlines (next 7 days)
                print("\n📅 Checking for upcoming deadlines...")
                upcoming_deadlines = self.db.get_all_upcoming_deadlines(days_ahead=7)
                
                if upcoming_deadlines:
                    print(f"⏰ Found {len(upcoming_deadlines)} upcoming deadlines in the next 7 days")
                    print("📧 Sending deadline reminder email...")
                    self.notifier.send_deadline_reminders(upcoming_deadlines)
                else:
                    print("✅ No upcoming deadlines in the next 7 days")
            except Exception as e:
                print(f"⚠️ Error sending notifications: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Scan Complete!")
        print("=" * 60)
        
        return results

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LMS Activity Scraper')
    parser.add_argument('--headless', type=bool, default=True, 
                       help='Run browser in headless mode')
    parser.add_argument('--test-email', action='store_true',
                       help='Send a test email')
    
    args = parser.parse_args()
    
    if args.test_email:
        print("📧 Sending test email...")
        notifier = Notifier()
        notifier.send_test_email()
        return
    
    scraper = MoodleScraper(headless=args.headless)
    scraper.run_full_scan()

if __name__ == '__main__':
    main()
