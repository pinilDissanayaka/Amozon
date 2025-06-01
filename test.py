import time
import random
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def simulate_human_interaction(driver):
    """Simulates human-like mouse movements and scrolling to reduce bot detection."""
    action = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(100, 500)
        y_offset = random.randint(100, 500)
        try:
            action.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.5, 1.5))
        except:
            pass  # ignore if movement goes out of bounds
    # Random scroll to mimic user behavior
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {random.randint(300, scroll_height)});")
    time.sleep(random.uniform(1.5, 3.0))

def search_kagon(base_url) -> list:
    options = uc.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled") 

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")

    # Launch undetected Chrome
    driver = uc.Chrome(options=options)
    all_data = []

    try:
        driver.get(base_url)
        time.sleep(5)  # Wait for JS to load

        # Check for CAPTCHA
        if "captcha" in driver.page_source.lower():
            print("🛑 CAPTCHA detected!")
            input("⚠️ Please solve the CAPTCHA manually, then press Enter to continue...")

        simulate_human_interaction(driver)

        # Example scraping logic — you should customize this
        wait = WebDriverWait(driver, 15)
        # Example: Wait for some element (replace this with your actual target)
        try:
            title_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
            print("✅ Page title:", title_element.get_attribute("textContent"))
            all_data.append(title_element.get_attribute("textContent"))
        except:
            print("⚠️ Could not find the title element.")

        # Add your own scraping logic here...

    except Exception as e:
        print(f"❌ Error: {e}")
        os.makedirs("error", exist_ok=True)
        screenshot_path = os.path.abspath("error/kagon_error_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}")

    finally:
        driver.quit()
        print("🧹 Browser closed.")

    return all_data

# Example usage
if __name__ == "__main__":
    url = "https://www.kogan.com/au/"  # Replace with your target URL
    data = search_kagon(url)
    print("🔍 Scraped Data:", data)
