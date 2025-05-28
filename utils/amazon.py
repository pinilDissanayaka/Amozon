from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def pretty_print_amazon_results(products:list):
    for index, product in enumerate(products, start=1):
        try:
            title = product.find_element(By.TAG_NAME, "h2").text.strip()
        except:
            title = "No Title"

        try:
            asin = product.get_attribute("data-asin")
        except:
            asin = "N/A"

        # Check if it's sponsored
        try:
            sponsored = product.find_element(By.CSS_SELECTOR, ".puis-sponsored-label-text").text
            is_sponsored = "Sponsored" in sponsored
        except:
            is_sponsored = False

        label = "🟨 Sponsored" if is_sponsored else "🟩 Organic"
        print(f"{index}. {label} - {title} (ASIN: {asin})")
        
        


def search_amazon(base_url, postcode, city_name, search_keyword)-> list:
    # === Set up WebDriver ===
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(base_url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    try:
        # === Step 1: Click location selector ===
        location_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
        location_btn.click()

        # === Step 2: Enter postcode ===
        postal_input = wait.until(EC.presence_of_element_located((By.ID, "GLUXPostalCodeWithCity_PostalCodeInput")))
        postal_input.clear()
        postal_input.send_keys(postcode)
        print(f"✅ Postcode entered: {postcode}")
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
            if option.text.strip().upper() == city_name:
                option.click()
                city_found = True
                print(f"✅ City selected: {city_name}")
                break
        if not city_found:
            print(f"❌ City '{city_name}' not found in dropdown.")

        # === Step 5: Click "Apply" button ===
        apply_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCityApplyButton")))
        apply_btn.click()
        print("✅ Clicked Apply button.")
        time.sleep(2)

        # === Step 6: Search for a product ===
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_keyword)
        print(f"🔍 Searching for: {search_keyword}")

        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
        search_btn.click()
        print("✅ Search submitted.")

        # === Step 7: Wait for results and print them ===
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))

        print("\n📦 Search Results:\n")
        products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

        if not products:
            print("❌ No products found.")
            return []
        pretty_print_amazon_results(products)
    except Exception as e:
        print("❌ Error during execution:", e)

    time.sleep(5)
    driver.quit()
    
    return products
