import undetected_chromedriver as uc
import time

options = uc.ChromeOptions()

# Replace with your proxy: format is IP:PORT or IP:PORT:USER:PASS
proxy = "34.102.48.89:8080"

# Add proxy argument
options.add_argument(f'--proxy-server=http://{proxy}')

# Start the browser with options
driver = uc.Chrome(options=options)

driver.get("https://httpbin.org/ip")  # To test if the IP is the proxy

time.sleep(5)  # Wait for the page to load

print(driver.page_source)  # Print the page source to verify the proxy is working



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
                #title = product.find_element(By.XPATH, ".//span[@role='heading']").get_attribute("innerText").strip()
                print(f"Product {index}: {title}")
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
                
                if index <24 and label == "Sponsored":
                    is_top_24_advertised = "Yes"
                else:
                    is_top_24_advertised = "No"
                
                if label == "Sponsored" or label == "Sponsored-Pickup From ebay":
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
        
        
if __name__ == "__main__":
    driver = open_browser(base_url="https://www.ebay.com.au")
    
    output_file = "output_2.csv"

    data = ebay_search_one(
        postcode="2143",
        country="Australia - AUS",
        search_keyword="foam cutter",
        product_id="124097292698",
        product_url="https://www.ebay.com.au/itm/124097292698?_skw=foam+cutter&epid=18048015038&itmmeta=01JWZ5PSZ9MACKBWK4SB7HXCRN&hash=item1ce4c6699a:g:8uYAAOSwspZnEigh&itmprp=enc%3AAQAKAAAA0FkggFvd1GGDu0w3yXCmi1c3ECIiWlZNhXThdakb%2F8QEwa%2BQURSo2EN6a11MZ6XgkhVUyXLg9kumZH8S3S9qYI9in9TtzKL%2B9sC66v0bIkN4BP6aeEBvLGxtW8Z3tcs%2FYKxehNAuFJNS1YhmnQuCbNPZViWSj7upr9IoRtJSDkWbiWsTULOZr5Kg3lD405YAe6kO7hiW7IgSRrJ7gBMc%2BPTfAXK7WbRA%2Bz%2FDI06jVVO%2FOFDAnzFXP4gVgyufsCJw4kAczf%2Bu5J0N0NuYofMUAY4%3D%7Ctkp%3ABk9SR-yf2-XnZQ",
        driver=driver,
        max_pages=3
    )
    
    if data:
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=data[0].keys(),
                quoting=csv.QUOTE_ALL
            )

            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                writer.writeheader()

            writer.writerows(data)
    else:
        default_row = {
            "Product URL": str(row['Link of the Product']),
            "Product Title": "N/A",
            "Keyword": str(row['Keyword']), 
            "Product ID": str(row['Product ID']),
            "Sponsored Rank": "N/A",
            "Organic Rank": "N/A",
            "Is Top 24 Advertised": "N/A"
        }
        
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(
                file,
                fieldnames=default_row.keys(),
                quoting=csv.QUOTE_ALL
            )

            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                writer.writeheader()

            writer.writerow(default_row)

    print("All rows processed. Closing browser in 5 seconds...")
    time.sleep(5)
    close_browser(driver)