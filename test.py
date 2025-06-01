import time
import random
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def simulate_human_interaction(driver):
    action = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        try:
            action.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
            time.sleep(random.uniform(0.5, 1.2))
        except:
            continue
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {random.randint(200, scroll_height)});")
    time.sleep(random.uniform(1.5, 3.0))

def is_captcha_present(driver):
    keywords = ["captcha", "cloudflare", "verify you are human"]
    page_source = driver.page_source.lower()
    return any(word in page_source for word in keywords)

def extract_products_from_page(driver):
    products = []
    try:
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div.product-title a")
        for prod in product_elements:
            text = prod.text.strip()
            if text:
                products.append(text)
    except Exception as e:
        print("⚠️ Error extracting product data on current page:", e)
    return products

def go_to_next_page(driver, wait):
    try:
        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pagination__next")))
        if "disabled" in next_button.get_attribute("class"):
            return False
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        time.sleep(random.uniform(1, 2))
        next_button.click()
        print("➡️ Navigated to next page.")
        time.sleep(random.uniform(4, 6))  # wait for page load
        return True
    except Exception:
        return False

def search_kogan(base_url, target_postcode="3000", search_keyword="laptop", max_pages=5) -> list:
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    all_data = []

    try:
        driver.get(base_url)
        time.sleep(5)

        if is_captcha_present(driver):
            print("🛑 CAPTCHA or bot detection triggered.")
            input("⚠️ Please manually solve the CAPTCHA, then press Enter to continue...")

        simulate_human_interaction(driver)

        wait = WebDriverWait(driver, 15)

        # Deliver to
        try:
            print("🖱️ Clicking 'Deliver to'...")
            deliver_to = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div._11yRS")))
            deliver_to.click()
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"⚠️ Failed to click 'Deliver to': {e}")

        # Enter postcode
        try:
            print("⌨️ Entering postcode...")
            postcode_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#postcode")))
            postcode_input.clear()
            postcode_input.send_keys(target_postcode)
            postcode_input.send_keys(Keys.ENTER)
            print(f"✅ Postcode '{target_postcode}' entered.")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Failed to enter postcode: {e}")

        # Search for a product
        try:
            print(f"🔎 Searching for '{search_keyword}'...")
            search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#product-search-field")))
            search_input.clear()
            search_input.send_keys(search_keyword)
            time.sleep(1)
            search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-nav__button")))
            search_button.click()
            print("✅ Search submitted.")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Search failed: {e}")

        # Paginated product extraction
        page = 1
        while page <= max_pages:
            print(f"📄 Scraping page {page}...")
            simulate_human_interaction(driver)
            products = extract_products_from_page(driver)
            print(f"🔹 Found {len(products)} products on page {page}.")
            all_data.extend(products)
            if not go_to_next_page(driver, wait):
                print("⛔ No more pages.")
                break
            page += 1

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        os.makedirs("error", exist_ok=True)
        screenshot_path = os.path.abspath("error/kogan_error_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}")
    finally:
        driver.quit()
        print("🧹 Browser closed.")

    return all_data

# 🔍 Example usage
if __name__ == "__main__":
    url = "https://www.kogan.com/au/"
    data = search_kogan(url, target_postcode="3000", search_keyword="laptop", max_pages=3)
    print("📦 Scraped Products:", data)

