"""
Signup Page Tests
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.binary_location = "/usr/bin/chromium-browser"
service = Service("/usr/bin/chromedriver")
URL = "http://localhost:5000/signupscreen"
driver = webdriver.Chrome(service=service, options=options)
driver.get(URL)
time.sleep(2)

passed = 0
failed = 0

def test_result(condition, test_name):
    global passed, failed
    if condition:
        print(f"[PASSED] - {test_name}")
        passed += 1
    else:
        print(f"[FAILED] - {test_name}")
        failed += 1

def dismiss_alert():
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass

print(f"Beginning Tests\n")

try:
    test_result(driver.find_element(By.NAME, "username"), "Username Field Exists")

    test_result(driver.find_element(By.NAME, "password"), "Password Field Exists")

    test_result(driver.find_element(By.NAME, "password-confirm"), "Confirm Password Field Exists")

    test_result(driver.find_element(By.NAME, "birthday"), "Birthday Field Exists")

    create_btn = driver.find_element(By.XPATH, "//input[@value='Create Account']")
    test_result(create_btn, "Create Account Button Exists")

    delete_btn = driver.find_element(By.XPATH, "//input[@value='Delete']")
    test_result(delete_btn, "Delete Button Exists")

    test_result(create_btn.is_enabled(), "Create Account Button is Enabled")

    driver.find_element(By.NAME, "username").send_keys("testuser")
    driver.find_element(By.NAME, "first_name").send_keys("Test")
    driver.find_element(By.NAME, "last_name").send_keys("User")
    driver.find_element(By.NAME, "password").send_keys("abc123")
    driver.find_element(By.NAME, "password-confirm").send_keys("xyz123")
    driver.find_element(By.ID, "birthday").send_keys("2000-01-01")
    create_btn.click()
    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        test_result("Passwords do not match" in alert.text, "Mismatched Password Alert Works")
        alert.accept()
    except:
        test_result(False, "Mismatched Password Alert Works")
    
    dismiss_alert()
    driver.refresh()
    time.sleep(1)
    driver.find_element(By.NAME, "username").send_keys("younguser")
    driver.find_element(By.NAME, "first_name").send_keys("Tiny")
    driver.find_element(By.NAME, "last_name").send_keys("Tim")
    driver.find_element(By.NAME, "password").send_keys("abc123")
    driver.find_element(By.NAME, "password-confirm").send_keys("abc123")
    driver.find_element(By.ID, "birthday").send_keys("2015-01-01")
    create_btn = driver.find_element(By.XPATH, "//input[@value='Create Account']")
    create_btn.click()
    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        test_result("at least 13 years old" in alert.text, "Underage User Alert Works")
        alert.accept()
    except:
        test_result(False, "Underage User Alert Works")
    
    dismiss_alert()
    driver.refresh()
    time.sleep(1)
    driver.find_element(By.NAME, "username").send_keys("olduser")
    driver.find_element(By.NAME, "first_name").send_keys("Old")
    driver.find_element(By.NAME, "last_name").send_keys("Man")
    driver.find_element(By.NAME, "password").send_keys("abc123")
    driver.find_element(By.NAME, "password-confirm").send_keys("abc123")
    driver.find_element(By.ID, "birthday").send_keys("1900-01-01")
    create_btn = driver.find_element(By.XPATH, "//input[@value='Create Account']")
    create_btn.click()
    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        test_result("too old" in alert.text, "Overage User Alert Works")
        alert.accept()
    except:
        test_result(False, "Overage User Alert Works")

finally:
    print(f"\nEnding Tests:\n {passed+failed} Tests Ran: {passed} Tests Passed, {failed} Tests Failed\n")
    driver.quit()