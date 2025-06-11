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
import os
import csv
import re
import time
import random

def find_ranking(products: list, page_num:int, product_id:str, product_url:str, keyword:str, sku:str):
    try:
        # Collect and print product info for a given page
        number_of_products = len(products)
        
        data=[]
        
        print(f"\n📦 Found {number_of_products} products on page {page_num}:\n")
        
        index=1
        for product in products:
            try:
                title = product.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]//div[contains(@class, 's-item__title')]/span[@role='heading']").get_attribute("innerText").strip()
                #title = product.find_element(By.XPATH, ".//span[@role='heading']").get_attribute("innerText").strip()
                if title is None or title == "" or title == "Shop on eBay":
                    continue
            except Exception:
                title = "No Title"
            
            try:
                link_elem = product.find_element(By.XPATH, ".//a[contains(@class, 's-item__link')]")
                product_link = link_elem.get_attribute("href")
                
                match = re.search(r'/itm/(\d+)', product_link)
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
                label = "Sponsored-Pickup From ebay"
                
            if product_id == str(asin):
                print(f"🔍 Found product with ID {product_id} at index {index} on page {page_num}.")
                print(f"It ranks {index} / {number_of_products} on this page.")

                if index <24 and label != "Organic":
                    is_top_24_advertised = "Yes"
                else:
                    is_top_24_advertised = "No"
                
                if label == "Sponsored" or label == "Sponsored-Pickup From ebay":
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
            index += 1
            
            print(f"🔗 {index-1}. {title} - {label} - {asin}")

        return data
    except Exception as e:
        print(f"❌ Error in find_ranking: {e}")


def open_browser(base_url:str, proxy:str=None):
    try: 
        # Setup Chrome options
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")


        driver=None
        
        try:
            driver = uc.Chrome(options=options)
            
            
            # Apply stealth
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            # Step 1: Open Kagon
            driver.get(base_url)
            print(f"✅ Opened Kagon {base_url}")

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "gh-ac"))  
            )
            return driver
        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            exit(1)
    except Exception as e:
        print(f"Error in open_browser: {e}")
        exit(1)
        
        
def search_ebay(driver, search_keyword:str):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "gh-ac")))
        search_input = driver.find_element(By.ID, "gh-ac")
        search_input.clear()
        search_input.send_keys(search_keyword)
        search_input.send_keys(Keys.RETURN)
        print(f"🔍 Searching for: {search_keyword}")
  
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "srp-river-results")))
    except Exception as e:
        print(f"Error in search_ebay: {e}")
        driver.quit()
        return None
    
    
def setup_location(driver, postcode:str, country:str):
    try:
        location_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 's-zipcode-entry__btn') and contains(., 'Sri Lanka')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", location_button)
        location_button.click()
        print("✅ Clicked 'Postage to Sri Lanka'")
        #random_sleep()
    except:
        print("❌ 'Postage to Sri Lanka' not found. Trying default location change...")
        try:
            location_edit_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "s-zipcode-entry__edit-btn"))
            )
            location_edit_btn.click()
            print("📝 Clicked location edit button")
            #random_sleep()
        except Exception as le:
            print(f"❌ Failed to open location settings: {le}")
            return

    # Step 5: Select country from dropdown
    dropdown = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//select[contains(@id, '-select')]"))
    )
    select = Select(dropdown)
    select.select_by_visible_text(country)
    print(f"✅ Selected country: {country}")
    

    # Step 6: Set postcode
    postcode_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Postcode']"))
    )
    driver.execute_script("arguments[0].removeAttribute('disabled')", postcode_input)
    postcode_input.clear()
    postcode_input.send_keys(postcode)
    print(f"📮 Postcode set to: {postcode}")

    # Step 7: Apply settings with retry
    success = False
    for attempt in range(2):
        try:
            apply_btn = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Apply']"))
            )
            apply_btn.click()
            print("🎉 Location settings applied!")
            success = True
            break
        except Exception as ap:
            print(f"⚠️ Attempt {attempt+1} to click Apply failed: {ap}")


    if not success:
        print("❌ Failed to apply location settings after multiple attempts.")
        


def scrape_web(driver, product_id:str, product_url:str, search_keyword:str, sku:str, max_pages:int=3):
    
    all_data=[]
    # Dictionary to track if we've already found the product
    found_products = {}

    current_page = 1
    while current_page <= max_pages:
        print(f"\n📦 Scraping page {current_page}...\n")

        product_cards = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 's-item')]"))
        )

        if not product_cards:
            print("❌ No products found on this page.")
            break

        data = find_ranking(products=product_cards, page_num=current_page, product_id=product_id, product_url=product_url, keyword=search_keyword, sku=sku)

        if data is not None:
            print(data)
            # Process each item before adding to all_data
            for item in data:
                item_id = item["Product ID"]
                # Check if we've already found this product
                if item_id in found_products:
                    # Get the index of the existing item
                    index = found_products[item_id]
                    existing_item = all_data[index]
                    
                    # Merge the information
                    if item["Sponsored Rank"] != "No" and existing_item["Sponsored Rank"] == "No":
                        existing_item["Sponsored Rank"] = item["Sponsored Rank"]
                    
                    if item["Organic Rank"] != "No" and existing_item["Organic Rank"] == "No":
                        existing_item["Organic Rank"] = item["Organic Rank"]
                    
                    # Update top 24 advertised status if needed
                    if item["Is Top 24 Advertised"] == "Yes":
                        existing_item["Is Top 24 Advertised"] = "Yes"
                    
                    print(f"🔄 Updated existing entry for product ID {item_id}")
                else:
                    # Add new item and track its index
                    all_data.append(item)
                    found_products[item_id] = len(all_data) - 1
                    print(f"➕ Added new entry for product ID {item_id}")
        else:
            all_data.append({
                "Product URL": product_url,
                "Product Title": "No",
                "Keyword": str(search_keyword), 
                "sku": str(sku),
                "Product ID": str(product_id),
                "Sponsored Rank": "No",
                "Organic Rank": "No",
                "Is Top 24 Advertised": "No"
            })


        try:
            next_btn = driver.find_element(By.XPATH, "//a[contains(@class, 'pagination__next')]")
            if "pagination__next--disabled" in next_btn.get_attribute("class"):
                print("✅ No more pages.")
                break
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            
            time.sleep(random.uniform(3, 6))
            next_btn.click()
            current_page += 1
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            print("✅ No next button found or error clicking next:", e)
            break
    if all_data:
        return all_data
    else:
        return None
        
        
def close_browser(driver):
    try:
        driver.quit()
        print("✅ Browser closed successfully.")
    except Exception as e:
        print(f"❌ Error closing browser: {e}")
        
        
open_browser(base_url="https://www.kogan.com/au/")