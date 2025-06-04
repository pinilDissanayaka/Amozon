from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select, WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from .config import random_sleep
import time
import os
import csv
import re

def pretty_print_ebay_results(products: list, page_num:int) -> list:
    try:
        # Collect and print product info for a given page
        data = []
        index=1
        for product in products:
            try:
                title = product.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]//div[contains(@class, 's-item__title')]/span[@role='heading']").get_attribute("innerText").strip()
                
                if title is None or title == "" or title == "Shop on eBay":
                    continue
            except Exception:
                title = "No Title"
            
            try:
                link_elem = product.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]")
                product_url = link_elem.get_attribute("href")
                
                match = re.search(r'/itm/(\d+)', product_url)
                asin = match.group(1) if match else "N/A"
                
            except Exception:
                asin = "N/A"
                
            try:
                sponsored = product.find_element(By.XPATH, ".//div[contains(@aria-hidden, 'true') and contains(text(), 'Sponsored')]").text
                
                if "Sponsored" in sponsored:
                    label = "Sponsored"
                else:
                    label = "Organic"
                
            except Exception:
                label = "Sponsored"
            
            data.append({
                "Page Number": f"P{page_num}",
                "Index": index,
                "Title": title,
                "ASIN": asin,
                "Type": label
            })
            
            print(f"P{page_num} {index}. {label} - {title} (ASIN: {asin})")
            index += 1
        return data
    except Exception as e:
        print(f"❌ Error in pretty_print_ebay_results: {e}")
        return []
    
def save_to_csv(data: list, keyword: str):
    # Save product data to CSV
    filename = f"data/ebay_product_search_results_for_{keyword}.csv"
    with open(filename, mode="w+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Page Number", "Index", "Title", "ASIN", "Type"])
        writer.writeheader()
        writer.writerows(data)
    print(f"\n✅ Data saved to {filename}")


def search_kagon(base_url) -> list:
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Create driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Apply stealth to reduce bot detection
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
    )

    all_data = []

    try:
        driver.get(base_url)
        wait = WebDriverWait(driver, 20)

        time.sleep(5)  # Give JavaScript time to run

        # Check for CAPTCHA
        if "captcha" in driver.page_source.lower():
            print("❌ CAPTCHA triggered.")
            input("🧠 CAPTCHA may be shown. Please solve it manually, then press Enter to continue...")

        # Scroll down to trigger JS loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)

        # TODO: Add scraping logic here and append results to `all_data`

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        screenshot_path = os.path.abspath("error/kagon_error_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}")

    finally:
        driver.quit()
        print("🧹 Browser closed.")

    return all_data


    

