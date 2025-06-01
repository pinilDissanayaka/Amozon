import time
import random
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def simulate_human_interaction(driver):
    """Simulate human-like interaction to reduce bot detection."""
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
    """Check if CAPTCHA or bot protection is active."""
    keywords = ["captcha", "cloudflare", "verify you are human"]
    page_source = driver.page_source.lower()
    return any(word in page_source for word in keywords)

def search_kogan(base_url, postcode="3000") -> list:
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

        # 🔘 Step 1: Click the "Deliver to" location box
        try:
            print("🖱️ Clicking the 'Deliver to' selector...")
            deliver_to = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div._11yRS")))
            deliver_to.click()
            time.sleep(random.uniform(1, 2))
            print("✅ Clicked the 'Deliver to' selector.")
        except Exception as e:
            print(f"⚠️ Failed to click 'Deliver to': {e}")
            driver.save_screenshot("error/deliver_to_click_failed.png")

        # 🧾 Step 2: Enter postcode
        try:
            print("⌨️ Waiting for postcode input field...")
            postcode_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#postcode")))
            postcode_input.click()
            postcode_input.clear()
            time.sleep(1)
            postcode_input.send_keys(postcode)
            postcode_input.send_keys(Keys.ENTER)
            print(f"✅ Entered postcode: {postcode}")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Failed to enter postcode: {e}")
            driver.save_screenshot("error/postcode_input_failed.png")

        # 🏷️ Get page title
        try:
            title_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
            title = title_element.get_attribute("textContent")
            print("✅ Page title:", title)
            all_data.append(title)
        except:
            print("⚠️ Could not find title element.")

        # 🛍️ Scrape product names (if visible)
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
    data = search_kogan(url, postcode="2143")  # Change postcode here if needed
    print("📦 Scraped Data:", data)


