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

def search_kogan(base_url, target_postcode="3000", search_keyword="laptop") -> list:
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

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

        # 🔘 Click on "Deliver to"
        try:
            print("🖱️ Clicking 'Deliver to'...")
            deliver_to = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div._11yRS")))
            deliver_to.click()
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f"⚠️ Failed to click 'Deliver to': {e}")

        # 🧾 Enter postcode
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

        # 🔍 Search for a product
        try:
            print(f"🔎 Searching for '{search_keyword}'...")
            search_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#product-search-field")))
            search_input.clear()
            search_input.send_keys(search_keyword)
            time.sleep(1)

            search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-nav__button")))
            search_button.click()
            print("✅ Search submitted.")
            time.sleep(5)  # Wait for results to load
        except Exception as e:
            print(f"⚠️ Search failed: {e}")

        # 🛍️ Extract product titles from results
        try:
            product_elements = driver.find_elements(By.CSS_SELECTOR, "div.product-title a")
            print(f"🛍️ Found {len(product_elements)} products.")
            for prod in product_elements:
                text = prod.text.strip()
                if text:
                    all_data.append(text)
        except Exception as e:
            print("⚠️ Error extracting product data:", e)

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
    data = search_kogan(url, target_postcode="3000", search_keyword="laptop")
    print("📦 Scraped Products:", data)



