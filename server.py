from test1 import open_browser, search_ebay, close_browser, setup_location, scrape_web
import pandas as pd
import csv
import time
import random
import os 

def get_ebay_item_id(url):
    item_id = url.rstrip('/').split('/')[-1]
    return item_id



def ebay_search(postcode: str, country: str, search_keyword: str, product_id: str, product_url: str, run_count: int, driver, sku:str, max_pages: int = 3):
    time.sleep(random.uniform(3, 6))

    if run_count == 0:        
        if driver:
            search_ebay(driver, search_keyword=search_keyword)
            setup_location(driver, postcode=postcode, country=country)
            
            time.sleep(random.uniform(3, 6))

            data=scrape_web(
                driver=driver,
                search_keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                sku=sku,
                max_pages=max_pages
            )
            
            if data:
                return data
    else:
        search_ebay(driver, search_keyword=search_keyword)
        data = scrape_web(
            driver=driver,
            search_keyword=search_keyword,
            product_id=product_id,
            product_url=product_url,
            sku=sku,
            max_pages=max_pages
        )
        
        if data:
            return data

    return None

def ebay_search_one(postcode: str, country: str, search_keyword: str, product_id: str, product_url: str, driver, max_pages: int = 3):
    time.sleep(random.uniform(3, 6))

    if driver:
        search_ebay(driver, search_keyword=search_keyword)
        setup_location(driver, postcode=postcode, country=country)
        
        time.sleep(random.uniform(3, 6))
        

        data = scrape_web(
            driver=driver,
            search_keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                max_pages=max_pages
            )
            
        if data:
            return data
    return None 

def main():
    df = pd.read_csv("PriorityAds.csv")
    output_file = "output.csv"
    base_url="https://www.ebay.com.au"
    
    
    driver = open_browser(base_url=base_url)


    for row_index, row in df.iterrows():
        print(f"\nProcessing Row: {row_index + 1} of {len(df)}")
        print(f"\nSearching Keyword: {row['Keywords']}")

        data = None
        
        product_id = get_ebay_item_id(str(row['Link of the Product']))
        
        try:
            data = ebay_search(
                postcode="2143",
                country="Australia - AUS",
                search_keyword=str(row['Keywords']),
                product_id=product_id,
                sku=str(row['SKU']),
                product_url=str(row['Link of the Product']),
                run_count=row_index,
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
                    "Product Title": "No",
                    "Keyword": str(row['Keywords']), 
                    "Product ID": product_id,
                    "sku": str(row['SKU']),
                    "Sponsored Rank": "No",
                    "Organic Rank": "No",
                    "Is Top 24 Advertised": "No"
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
                    
        except Exception as e:
            print(f"❌ Error processing row {row_index}: {e.args}")


        if row_index % 10 == 0:
            df.to_csv("backup_results.csv", index=False)

        time.sleep(random.uniform(3, 6))
        
        
    return driver


if __name__ == "__main__":
    driver = main()
    print("All rows processed. Closing browser in 5 seconds...")
    time.sleep(5)
    close_browser(driver)