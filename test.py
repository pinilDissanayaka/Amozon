from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# === Configuration ===
POSTCODE = "2143"
CITY_NAME = "REGENTS PARK DC"
SEARCH_KEYWORD = "laptop"

# === Set up WebDriver ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.amazon.com.au")
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # === Step 1: Click location selector ===
    location_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
    location_btn.click()

    # === Step 2: Enter postcode ===
    postal_input = wait.until(EC.presence_of_element_located((By.ID, "GLUXPostalCodeWithCity_PostalCodeInput")))
    postal_input.clear()
    postal_input.send_keys(POSTCODE)
    time.sleep(1)

    # === Step 3: Open city dropdown ===
    dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCity_DropdownButton")))
    dropdown_btn.click()
    time.sleep(1)

    # === Step 4: Select city ===
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-popover-inner")))
    city_options = driver.find_elements(By.XPATH, "//a[contains(@class, 'a-dropdown-link')]")
    city_found = False
    for option in city_options:
        if option.text.strip().upper() == CITY_NAME:
            option.click()
            city_found = True
            print(f"✅ City selected: {CITY_NAME}")
            break
    if not city_found:
        print(f"❌ City '{CITY_NAME}' not found in dropdown.")

    # === Step 5: Click "Apply" button ===
    apply_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCityApplyButton")))
    apply_btn.click()
    print("✅ Clicked Apply button.")
    time.sleep(2)

    # === Step 6: Search for a product ===
    search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
    search_box.clear()
    search_box.send_keys(SEARCH_KEYWORD)
    print(f"🔍 Searching for: {SEARCH_KEYWORD}")

    search_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
    search_btn.click()
    print("✅ Search submitted.")

    # === Optional: Confirm title or wait for results ===
    wait.until(EC.title_contains(SEARCH_KEYWORD))
    print("🔎 Search results loaded.")

except Exception as e:
    print("❌ Error during execution:", e)

time.sleep(5)
driver.quit()


