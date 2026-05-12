import time
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. TEST DATA (Credentials removed for privacy)
# In a real scenario, these could be loaded from an encrypted CSV or JSON file.
students = [
    {"login": "user_alpha_01", "pass": "secure_password_123"},
    {"login": "user_beta_02", "pass": "secure_password_456"},
    {"login": "user_gamma_03", "pass": "secure_password_789"}
]

# 2. IP ROTATION (Tor Signal NEWNYM)
# This function requests a new identity from Tor to avoid IP rate-limiting.
def renew_tor_ip():
    print("\n♻️ Requesting new IP address...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9051))
            s.sendall(b'AUTHENTICATE ""\n')
            s.sendall(b'SIGNAL NEWNYM\n')
            response = s.recv(1024)
            if b'250' in response:
                print("✅ IP successfully rotated.")
            else:
                print(f"⚠️ Tor response: {response}")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Tor Control Port error: {e}. Ensure Tor is running with ControlPort 9051.")

# 3. BROWSER CONFIGURATION
def get_driver():
    options = webdriver.ChromeOptions()
    # Routing traffic through Tor SOCKS5 proxy
    options.add_argument('--proxy-server=socks5://127.0.0.1:9050')
    # Stealth mode: disable automation flags to avoid bot detection
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# 4. MAIN AUTOMATION LOGIC
def run_automation():
    target_url = "https://example-portal.com/login" # Generic URL for portfolio
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    for i, student in enumerate(students):
        # Rotate IP every 5 users to maintain anonymity
        if i > 0 and i % 5 == 0:
            print(f"\n--- Batch limit reached. Rotating IP... ---")
            driver.quit()
            renew_tor_ip()
            driver = get_driver()
            wait = WebDriverWait(driver, 15)

        login = student['login']
        password = student['pass']

        try:
            print(f"[{i+1}/{len(students)}] Processing user: {login}")
            driver.get(target_url)

            # Locate elements and interact
            user_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
            pass_field = driver.find_element(By.NAME, "password")
            
            user_field.clear()
            user_field.send_keys(login)
            pass_field.clear()
            pass_field.send_keys(password)
            
            # Submit form
            driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            
            time.sleep(5) # Wait for page load

            # Validation logic
            if "login" in driver.current_url:
                print(f"❌ Login failed or Captcha triggered for: {login}")
            else:
                print(f"✅ Success: {login}")
                # Logout to prepare for next user
                # driver.get("https://example-portal.com/logout")
                time.sleep(2)

        except Exception as e:
            print(f"⚠️ Error processing {login}: {e}")
            continue

    driver.quit()
    print("\nProcess completed successfully!")

if __name__ == "__main__":
    run_automation()
