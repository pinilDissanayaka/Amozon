from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import time
import csv
from .config import random_sleep
from selenium.webdriver.chrome.options import Options


def pretty_print_amazon_results(products: list, page_num: int) -> list:
    # Collect and print product info for a given page
    data = []
    for index, product in enumerate(products, start=1):
        try:
            title = product.find_element(By.TAG_NAME, "h2").text.strip()
        except Exception:
            title = "No Title"
        try:
            asin = product.get_attribute("data-asin")
        except Exception:
            asin = "N/A"
        try:
            sponsored = product.find_element(By.CSS_SELECTOR, ".puis-sponsored-label-text").text
            if "Sponsored" in sponsored:
                label = "Sponsored"
            elif "Featured from Amazon brands" in sponsored:
                label = "Featured from Amazon brands"
            else:
                label = "Organic"
        except Exception:
            label = "Organic"
        data.append({
            "Page Number": f"P{page_num}",
            "Index": index,
            "Title": title,
            "ASIN": asin,
            "Type": label
        })
        print(f"P{page_num} {index}. {label} - {title} (ASIN: {asin})")
    return data


def save_to_csv(data: list, keyword: str):
    # Save product data to CSV
    filename = f"amazon_product_search_results_for_{keyword}.csv"
    with open(filename, mode="w+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Page Number", "Index", "Title", "ASIN", "Type"])
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ Data saved to {filename}")


def search_amazon(base_url, postcode, city_name, search_keyword, max_pages=3) -> list:
    # Main Amazon search and scrape logic
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

    driver.get(base_url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    all_data = []

    try:
        if "captcha" in driver.page_source.lower():
            print("❌ CAPTCHA triggered.")
            input("🧠 CAPTCHA may be shown. Please solve it in the browser if present, then press Enter to continue...")

        # Set location
        location_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
        location_btn.click()

        postal_input = wait.until(EC.presence_of_element_located((By.ID, "GLUXPostalCodeWithCity_PostalCodeInput")))
        postal_input.clear()
        postal_input.send_keys(postcode)
        random_sleep()
        print(f"✅ Postcode entered: {postcode}")
        time.sleep(1)

        dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCity_DropdownButton")))
        dropdown_btn.click()
        time.sleep(1)

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-popover-inner")))
        city_options = driver.find_elements(By.XPATH, "//a[contains(@class, 'a-dropdown-link')]")
        city_found = False
        for option in city_options:
            if option.text.strip().upper() == city_name:
                option.click()
                random_sleep()
                city_found = True
                print(f"✅ City selected: {city_name}")
                break
        if not city_found:
            print(f"❌ City '{city_name}' not found in dropdown.")

        apply_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCityApplyButton")))
        apply_btn.click()
        print("✅ Clicked Apply button.")
        time.sleep(2)

        # Search for keyword
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_keyword)
        random_sleep()
        print(f"🔍 Searching for: {search_keyword}")

        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-search-submit-button")))
        search_btn.click()
        print("✅ Search submitted.")

        # Scrape pages
        current_page = 1
        while current_page <= max_pages:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
            print(f"\n📦 Scraping page {current_page}...\n")

            products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
            if not products:
                print("❌ No products found on this page.")
                break

            page_data = pretty_print_amazon_results(products, current_page)
            all_data.extend(page_data)

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                time.sleep(2)
                random_sleep()
                driver.execute_script("arguments[0].click();", next_btn)
                current_page += 1
                time.sleep(3)
            except Exception as e:
                print("✅ No more pages found or error clicking next:", e)
                break
    except Exception as e:
        print("❌ Error during execution:", e)

    time.sleep(5)
    driver.quit()
    return all_data
