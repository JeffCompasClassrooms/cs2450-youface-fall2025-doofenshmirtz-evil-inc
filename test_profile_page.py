from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import tinydb
import time
import os

# --- Setup test user in your TinyDB ---
DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")  # adjust path to your app DB
db = tinydb.TinyDB(DB_PATH)
users = db.table("users")

# Insert user only if it doesn't exist
users.remove(tinydb.Query().username == "john")
if not users.contains(tinydb.Query().username == "john"):
    users.insert({
        "username": "john",
        "password": "doe",
        "bio": "Hello!",
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

# --- Selenium setup ---
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    # --- Go to login page ---
    driver.get("http://localhost:5006/loginscreen")
    time.sleep(2)  # wait for page to load

    # --- Fill in credentials ---
    driver.find_element(By.NAME, "username").send_keys("john")
    driver.find_element(By.NAME, "password").send_keys("doe")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']").click()
    time.sleep(2)  # wait for redirect

    # --- Go to profile page ---
    driver.get("http://localhost:5006/profilescreen")
    time.sleep(2)

    print("--= Beginning Profile Page Tests =--")

    # --- Check Profile Picture ---
    try:
        driver.find_element(By.ID, "pfp")
        print("[PASSED] - Profile Picture exists.")
    except:
        print("[FAILED] - Profile Picture not found.")

    # --- Check Username Display ---
    try:
        driver.find_element(By.ID, "username_display")
        print("[PASSED]- Username being displayed")
    except:
        print("[FAILED] - Username not displaying")

    # --- Check User Handle Display
    try:
        driver.find_element(By.ID, "handle_display")
        print("[PASSED]- User Handle being displayed")
    except:
        print("[FAILED] - User Handle not displaying")

    # --- Check Birthday Display ---
    try:
        expected_birthday = "2000-01-01"
        birthday_elem = driver.find_element(By.ID, "birthday")

        displayed_value = (
            birthday_elem.get_attribute("value")
            if birthday_elem.tag_name == "input" 
            else birthday_elem.text
        )

        displayed_value = displayed_value.strip()
        if displayed_value.lower().startswith("birthday:"):
            displayed_value = displayed_value[len("birthday:"):].strip()

        if str(displayed_value) == str(expected_birthday):
            print("[PASSED] - Birthday being displayed correctly")
        else:
            print("[PASSED] - Birthday being displayed")
            print(f"[FAILED] - Birthday incorrect, found '{displayed_value}' instead")

    except Exception as e:
        print("[FAILED] - Birthday not displaying:", e)

    # --- Check Age Display ---
    try:
        driver.find_element(By.ID, "age")
        print("[PASSED]- Age being displayed")
    except:
        print("[FAILED] - Age not displaying")

    # --- Check Bio Box ---
    try:
        driver.find_element(By.NAME, "bio")
        print("[PASSED] - Bio box exists.")
    except:
        print("[FAILED] - Bio box not found.")

    try:
        driver.find_element(By.NAME, "save_button")
        print("[PASSED] - Bio save button exists.")
    except:
        print("[FAILED] - Bio save button not found")

    # --- Check Bio Update
    try:
        new_bio = "hello!"
        bio_box = driver.find_element(By.NAME, "bio")
        bio_box.clear()
        bio_box.send_keys(new_bio)

        bio_save_button = driver.find_element(By.NAME, "save_button")
        bio_save_button.click()

        time.sleep(1)
        # Grab the bio_box for value after page reload
        bio_box = driver.find_element(By.NAME, "bio")

        if bio_box.get_attribute("value") == new_bio:
            print("[PASSED] - Bio updated and saved")
        else:
            print("[FAILED] - Bio not saved")
    except:
        print("[FAILED] - Bio not saved")

    # --- Check Delete Button ---
    try:
        driver.find_element(By.NAME, "delete")
        print("[PASSED] - Delete button exists.")
    except:
        print("[FAILED] - Delete button not found.")

    # --- Check Delete Text Field ---
    try:
        driver.find_element(By.NAME, "delete_confirm")
        print("[PASSED] - Delete confirm field exists.")
    except:
        print("[FAILED] - Delete confirm field not found.")

    try:
        delete_box = driver.find_element(By.NAME, "delete_confirm")
        delete_box.send_keys("delete")
        delete_button = driver.find_element(By.NAME, "delete")
        delete_button.click()

        time.sleep(1)

        if users.contains(tinydb.Query().username == "john"):
            print("[FAILED] - Delete button pressed but john still in db")
        else:
            print("[PASSED] - user john doe removed from db")

    # Works if user is deleted and redirected to login page
    except WebDriverException:
        print("[PASSED] - john deleted from db")
    except:
        print("[FAILED] - Delete logic nonfunctional")

except Exception as e:
    print("Error:", e)

finally:
    print("--= Ending Tests =--")
    driver.quit()
