from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import tinydb
import time
import os

# --- Setup test user in your TinyDB ---
DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")
db = tinydb.TinyDB(DB_PATH)
users = db.table("users")

# Ensure a test user exists
users.remove(tinydb.Query().username == "john")
if not users.contains(tinydb.Query().username == "john"):
    users.insert({
        "username": "john",
        "password": "doe",
        "bio": "Test Bio",
        "pfp": "AgentD.png",
        "birthday": "2000-01-01",
        "friends": [],
        "followers": [],
        "following": [],
        "friend_requests": [],
        "blocked_users": []
    })
    print("[INFO] Test user 'john' created.")
else:
    print("[INFO] Test user 'john' already exists.")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    #open login
    driver.get("http://localhost:5006/loginscreen")
    time.sleep(2)

    print("--= Beginning Login Page Tests =--")

    #check page title/jumbotron
    try:
        title_text = driver.title
        if title_text:
            print(f"[PASSED] - Page title exists ('{title_text}')")
        else:
            print("[FAILED] - Page title missing")
    except Exception as e:
        print("[FAILED] - Page title error:", e)

    try:
        subtitle = driver.find_element(By.CSS_SELECTOR, ".lead").text
        print(f"[PASSED] - Subtitle displayed ('{subtitle}')")
    except:
        print("[FAILED] - Subtitle not displayed")

    #check for username field
    try:
        driver.find_element(By.NAME, "username")
        print("[PASSED] - Username input field exists.")
    except:
        print("[FAILED] - Username input field not found.")

    #password
    try:
        driver.find_element(By.NAME, "password")
        print("[PASSED] - Password input field exists.")
    except:
        print("[FAILED] - Password input field not found.")

    #login button
    try:
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        print("[PASSED] - Login button exists.")
    except:
        print("[FAILED] - Login button not found.")

    #create button
    try:
        driver.find_element(By.LINK_TEXT, "Create")
        print("[PASSED] - Create account link exists.")
    except:
        print("[FAILED] - Create account link not found.")

    #login
    try:
        driver.find_element(By.NAME, "username").send_keys("john")
        driver.find_element(By.NAME, "password").send_keys("doe")
        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()

        time.sleep(2)

        if driver.current_url.endswith("/"):
            print("[PASSED] - Redirected to index page after login.")
        else:
            print(f"[FAILED] - Did not redirect properly (current: {driver.current_url})")

        #are cookies set?
        username_cookie = driver.get_cookie("username")
        password_cookie = driver.get_cookie("password")

        if username_cookie and password_cookie:
            print("[PASSED] - Cookies for username and password set.")
        else:
            print("[FAILED] - Cookies not set after login.")

    except Exception as e:
        print("[FAILED] - Login test failed:", e)

    #check for logout
    try:
        logout_button = driver.find_element(By.NAME, "logout")
        logout_button.click()
        time.sleep(2)

        if driver.current_url.endswith("/loginscreen"):
            print("[PASSED] - Redirected to login screen after logout.")
        else:
            print("[FAILED] - Did not return to login screen after logout.")
    except:
        print("[FAILED] - Logout button not working or not found.")
        print("This failure may occur if selenium is running with the argument '--headless")

except Exception as e:
    print("Error during tests:", e)

finally:
    print("--= Ending Tests =--")
    driver.quit()
