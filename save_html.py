import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time

load_dotenv()

options = Options()
# options.add_argument('--headless')  # Comment for debugging
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # Login
    driver.get('https://oulms.ou.ac.lk/login/index.php')
    time.sleep(2)
    
    ms_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'oauth2')]"))
    )
    ms_button.click()
    time.sleep(2)
    
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "loginfmt"))
    )
    username_field.send_keys(os.getenv('OUSL_USERNAME'))
    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(2)
    
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "passwd"))
    )
    password_field.send_keys(os.getenv('OUSL_PASSWORD'))
    driver.find_element(By.ID, "idSIButton9").click()
    time.sleep(2)
    
    stay_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "idSIButton9"))
    )
    stay_button.click()
    time.sleep(5)
    
    # Navigate to dashboard
    driver.get('https://oulms.ou.ac.lk/my/')
    time.sleep(3)
    
    # Save HTML
    with open('ousl_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    print("HTML saved to ousl_dashboard.html")
    print("You can now inspect it to see the actual structure")
    
finally:
    input("Press Enter to close...")
    driver.quit()
