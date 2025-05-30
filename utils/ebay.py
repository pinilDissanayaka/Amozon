from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select, WebDriverWait
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


def search_amazon(base_url, postcode, country, search_keyword, max_pages=3) -> list:
    # Setup Chrome options
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Apply stealth
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    all_data = []

    try:
        # Step 1: Open eBay
        driver.get(base_url)
        print(f"✅ Opened eBay {country}")

        # Step 2: Enter search keyword
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gh-ac")))
        search_input = driver.find_element(By.ID, "gh-ac")
        search_input.clear()
        search_input.send_keys(search_keyword)
        search_input.send_keys(Keys.RETURN)
        print(f"🔍 Searching for: {search_keyword}")
        random_sleep()

        # Step 3: Wait for results
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "srp-river-results")))

                # Step 4: Click location setting or fallback to edit
        try:
            location_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 's-zipcode-entry__btn') and contains(., 'Sri Lanka')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", location_button)
            location_button.click()
            print("✅ Clicked 'Postage to Sri Lanka'")
            random_sleep()
        except:
            print("❌ 'Postage to Sri Lanka' not found. Trying default location change...")
            try:
                location_edit_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "s-zipcode-entry__edit-btn"))
                )
                location_edit_btn.click()
                print("📝 Clicked location edit button")
                random_sleep()
            except Exception as le:
                print(f"❌ Failed to open location settings: {le}")
                return

        # Step 5: Select country from dropdown
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[contains(@id, '-select')]"))
        )
        select = Select(dropdown)
        select.select_by_visible_text(country)
        print(f"✅ Selected country: {country}")
        random_sleep()
        

        # Step 6: Set postcode
        postcode_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Postcode']"))
        )
        driver.execute_script("arguments[0].removeAttribute('disabled')", postcode_input)
        postcode_input.clear()
        postcode_input.send_keys(postcode)
        print(f"📮 Postcode set to: {postcode}")
        random_sleep()


        # Step 7: Apply settings with retry
        success = False
        for attempt in range(2):
            try:
                apply_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))
                )
                apply_btn.click()
                print("🎉 Location settings applied!")
                random_sleep()
                success = True
                break
            except Exception as ap:
                print(f"⚠️ Attempt {attempt+1} to click Apply failed: {ap}")
                random_sleep()


        if not success:
            print("❌ Failed to apply location settings after multiple attempts.")

        # Wait to verify
        time.sleep(3)

        current_page = 1
        while current_page <= max_pages:
            print(f"\n📦 Scraping page {current_page}...\n")

            product_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 's-item')]"))
            )

            if not product_cards:
                print("❌ No products found on this page.")
                break

            page_data = pretty_print_ebay_results(product_cards, current_page)
            all_data.extend(page_data)

            try:
                next_btn = driver.find_element(By.XPATH, "//a[contains(@class, 'pagination__next')]")
                if "pagination__next--disabled" in next_btn.get_attribute("class"):
                    print("✅ No more pages.")
                    break
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                time.sleep(1)
                random_sleep()
                next_btn.click()
                current_page += 1
                time.sleep(3)
            except Exception as e:
                print("✅ No next button found or error clicking next:", e)
                break

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        screenshot_path = os.path.abspath("ebay_error_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved to: {screenshot_path}")

    finally:
        driver.quit()
        print("🧹 Browser closed.")

    if all_data:
        save_to_csv(data=all_data, keyword=search_keyword)
