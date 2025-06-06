from selenium import webdriver
import undetected_chromedriver as uc
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

def find_ranking(products: list, page_num:int, product_id:str, product_url:str, keyword:str = None):
    try:
        # Collect and print product info for a given page
        number_of_products = len(products)
        
        data=[]
        
        print(f"\n📦 Found {number_of_products} products on page {page_num}:\n")
        index=1
        for product in products:
            try:
                title = product.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]//div[contains(@class, 's-item__title')]/span[@role='heading']").get_attribute("innerText").strip()
                
                if title is None or title == "" or title == "Shop on eBay":
                    continue
            except Exception:
                title = "No Title"
                
            print(f"🔹 Product {index}: {title}")
            
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
                
            if product_id == str(asin):
                print(f"🔍 Found product with ID {product_id} at index {index} on page {page_num}.")
                print(f"It ranks {index} / {number_of_products} on this page.")
                
                if index <24 and label == "Sponsored":
                    is_top_24_advertised = "Yes"
                else:
                    is_top_24_advertised = "No"
                
                if label == "Sponsored":
                    data.append({
                        "Product URL": product_url,
                        "Product Title": title,
                        "Keyword": keyword, 
                        "Product ID": asin,
                        "Sponsored Rank": f"P{page_num} - {index} / {number_of_products}",
                        "Organic Rank": "N/A",
                        "Is Top 24 Advertised": is_top_24_advertised
                    })
                else:
                    data.append({
                        "Product URL": product_url,
                        "Product Title": title,
                        "Keyword": keyword, 
                        "Product ID": asin,
                        "Sponsored Rank": "N/A",
                        "Organic Rank": f"P{page_num} - {index} / {number_of_products}",
                        "Is Top 24 Advertised": is_top_24_advertised
                    })
            index += 1

        return data
    except Exception as e:
        print(f"❌ Error in find_ranking: {e}")

    
    
    
def search_ebay(base_url, postcode, country, search_keyword, product_id, product_url, max_pages=3, proxy=None):
    try: 
        # Setup Chrome options
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")


        driver=None
        
        try:
            driver = uc.Chrome(options=options)
            
            random_sleep()
            
            # Apply stealth
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            # Step 1: Open eBay
            driver.get(base_url)
            print(f"✅ Opened eBay {country}")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "gh-ac"))  
            )
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            exit(1)


        try:
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
            
            all_data=[]

            current_page = 1
            while current_page <= max_pages:
                print(f"\n📦 Scraping page {current_page}...\n")

                product_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 's-item')]"))
                )

                if not product_cards:
                    print("❌ No products found on this page.")
                    break

                data = find_ranking(products=product_cards, page_num=current_page, product_id=product_id, product_url=product_url, keyword=search_keyword)

                if data is not None:
                    all_data.extend(data)

                else:
                    print("❌ Product ID not found on this page.")

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
            screenshot_path = os.path.abspath("error/ebay_error_screenshot.png")
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
            
        
        return all_data
    except Exception as e:
        print(f"❌ Error in search_ebay: {e}")
        if driver:
            screenshot_path = os.path.abspath("error/ebay_error_screenshot.png")
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
        return []
            