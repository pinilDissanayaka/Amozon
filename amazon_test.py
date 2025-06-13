import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.webdriver.support.ui import Select
import time
import re
import csv
import random

# === Utility ===

def random_sleep(min_sec=1.5, max_sec=3.5):
    time.sleep(random.uniform(min_sec, max_sec))


# === Browser Setup ===

def open_browser(base_url: str, proxy: str = None):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")

        driver = uc.Chrome(options=options)
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        driver.get(base_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "nav-search-bar-form"))
        )
        print(f"✅ Opened Amazon: {base_url}")
        return driver
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        return None


def close_browser(driver):
    try:
        driver.quit()
        print("✅ Browser closed.")
    except Exception as e:
        print(f"❌ Error closing browser: {e}")


# === Location Setup ===

def setup_location(driver, postcode: str, city_name: str):
    try:
        wait = WebDriverWait(driver, 30)
        location_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link")))
        location_btn.click()

        postal_input = wait.until(EC.presence_of_element_located((By.ID, "GLUXPostalCodeWithCity_PostalCodeInput")))
        postal_input.clear()
        postal_input.send_keys(postcode)
        random_sleep()

        dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCity_DropdownButton")))
        dropdown_btn.click()
        time.sleep(1)

        city_options = driver.find_elements(By.XPATH, "//a[contains(@class, 'a-dropdown-link')]")
        for option in city_options:
            if option.text.strip().upper() == city_name.upper():
                option.click()
                print(f"✅ City selected: {city_name}")
                break
        else:
            print(f"❌ City '{city_name}' not found in dropdown.")

        apply_btn = wait.until(EC.element_to_be_clickable((By.ID, "GLUXPostalCodeWithCityApplyButton")))
        apply_btn.click()
        print("✅ Location settings applied.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error in setup_location: {e}")


# === Search ===

def search_amazon(driver, keyword: str):
    try:
        wait = WebDriverWait(driver, 30)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        print(f"🔍 Searching Amazon for: {keyword}")
    except Exception as e:
        print(f"❌ Error during search: {e}")


# === Parsing and Scraping ===

def extract_product_data(products, page_num: int, product_id:str, product_url:str, keyword:str, sku:str) -> list:
    
    number_of_products = len(products)
    print(f"Found {number_of_products} products on page {page_num}.")

    
    data = []
    for index, product in enumerate(products, start=1):
        try:
            title = product.find_element(By.TAG_NAME, "h2").text.strip()
        except:
            title = "No Title"

        try:
            asin = product.get_attribute("data-asin")
        except:
            asin = "N/A"

        try:
            sponsored = product.find_element(By.CSS_SELECTOR, ".puis-sponsored-label-text").text
            if "Sponsored" in sponsored:
                label = "Sponsored"
            elif "Featured from Amazon brands" in sponsored:
                label = "Featured from Amazon brands"
            else:
                label = "Organic"
        except:
            label = "Organic"


        if product_id == str(asin):
            print(f"🔍 Found product with ID {product_id} at index {index} on page {page_num}.")
            print(f"It ranks {index} / {number_of_products} on this page.")

            if index <24 and label != "Organic":
                is_top_24_advertised = "Yes"
            else:
                is_top_24_advertised = "No"
            
            if label == "Sponsored" or label == "Featured from Amazon brands":
                data.append({
                    "Product URL": str(product_url),
                    "Product Title": str(title),
                    "Keyword": str(keyword),
                    "sku": str(sku),
                    "Product ID": str(asin),
                    "Sponsored Rank": f"P{page_num} - {index} / {number_of_products}",
                    "Organic Rank": "No",
                    "Is Top 24 Advertised": is_top_24_advertised
                })
            else:
                data.append({
                    "Product URL": str(product_url),
                    "Product Title": str(title),
                    "Keyword": str(keyword),
                    "sku": str(sku),
                    "Product ID": str(asin),
                    "Sponsored Rank": "No",
                    "Organic Rank": f"P{page_num} - {index} / {number_of_products}",
                    "Is Top 24 Advertised": is_top_24_advertised
                })
                
        print(f"🔗 {index}. {title} - {label} - {asin}")
    return data


def scrape_amazon(driver, keyword, product_id, product_url, sku, max_pages):
    all_data = []
    wait = WebDriverWait(driver, 30)

    for current_page in range(1, max_pages + 1):
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
            print(f"\n📦 Scraping page {current_page}...\n")

            products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
            if not products:
                print("❌ No products found.")
                break

            page_data = extract_product_data(products, current_page, product_id, product_url, keyword, sku)
            all_data.extend(page_data)

            try:
                next_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.s-pagination-next")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                random_sleep(1, 2)

                # Ensure it's clickable
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next")))

                # Perform click via JS to avoid overlay issues
                driver.execute_script("arguments[0].click();", next_btn)
                print(f"➡️ Clicked 'Next' to go to page {current_page + 1}")
                random_sleep(3, 5)
            except Exception as e:
                print("✅ No more pages or error clicking next:", e)
                break
        except Exception as e:
            print(f"❌ Error scraping page {current_page}: {e}")
            break
    return all_data







if __name__ == "__main__":
    base_url = "https://www.amazon.com.au/"
    postcode = "2143"
    city = "REGENTS PARK"
    keyword = "electric screwdriver set"
    proxy = None

    driver = open_browser(base_url, proxy)
    if driver:
        setup_location(driver, postcode, city)
        search_amazon(driver, keyword)
        data = scrape_amazon(driver, keyword, max_pages=3)
        
        