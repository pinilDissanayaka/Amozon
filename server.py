from turtle import st

from regex import R
from test1 import open_browser, search_ebay, close_browser, setup_location, scrape_web
import pandas as pd
import csv
import time
import random
import os 

def get_ebay_item_id(url):
    item_id = url.rstrip('/').split('/')[-1]
    return item_id



def ebay_search(postcode: str, country: str, search_keyword: str, product_id: str, product_url: str, run_count: int, driver, sku:str, reference_id:str, is_24:str=None, max_pages: int = 3):
    time.sleep(random.uniform(3, 6))

    if run_count == 0:        
        if driver:
            search_ebay(driver, search_keyword=search_keyword)
            time.sleep(random.uniform(3, 6))
            setup_location(driver, postcode=postcode, country=country)
            
            time.sleep(random.uniform(3, 6))

            if is_24 == "Yes":
                print("Skipping search for Top 24 Advertised products")
                return None
                
            data=scrape_web(
                driver=driver,
                search_keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                sku=sku,
                reference_id=reference_id,
                max_pages=max_pages
            )
            
            if data:
                return data
    else:
        if is_24 == "Yes":
            print("Skipping search for Top 24 Advertised products")
            return None
        search_ebay(driver, search_keyword=search_keyword)
        time.sleep(random.uniform(3, 6))
        data = scrape_web(
            driver=driver,
            search_keyword=search_keyword,
            product_id=product_id,
            product_url=product_url,
            sku=sku,
            reference_id=reference_id,
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
    df = pd.read_csv("output_1_formatted.csv")
    output_file = "output_1.csv"
    base_url="https://www.ebay.com.au"
    
    
    driver = open_browser(base_url=base_url)


    for row_index, row in df.iterrows():
        print(f"\nProcessing Row: {row_index + 1} of {len(df)}")
        print(f"\nSearching Keyword: {row['Keywords']}")

        data = None
        
        product_id = get_ebay_item_id(str(row['Product URL']))
        
        
        try:
            data = ebay_search(
                postcode="2143",
                country="Australia - AUS",
                search_keyword=str(row['Keywords']),
                product_id=product_id,
                sku=str(row['SKU']),
                product_url=str(row['Product URL']),
                run_count=row_index,
                driver=driver,
                reference_id=str(row['ReferenceID']),
                is_24=str(row['Is Top 24 Advertised']),                 
                max_pages=2
            )
            
            
            if data:
                # Consolidate data for the same product
                consolidated_data = {}
                for item in data:
                    # Use product ID as the key to identify unique products
                    key = item["Product ID"]
                    
                    if key not in consolidated_data:
                        consolidated_data[key] = item
                    else:
                        # Combine sponsored and organic rankings if both exist
                        if item["Sponsored Rank"] != "No" and consolidated_data[key]["Sponsored Rank"] == "No":
                            consolidated_data[key]["Sponsored Rank"] = item["Sponsored Rank"]
                        
                        if item["Organic Rank"] != "No" and consolidated_data[key]["Organic Rank"] == "No":
                            consolidated_data[key]["Organic Rank"] = item["Organic Rank"]
                        
                        # Update top 24 advertised status if needed
                        if item["Is Top 24 Advertised"] == "Yes":
                            consolidated_data[key]["Is Top 24 Advertised"] = "Yes"
                
                # Convert the dictionary to a list
                final_data = list(consolidated_data.values())
                
                with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(
                        file,
                        fieldnames=final_data[0].keys(),
                        quoting=csv.QUOTE_ALL
                    )

                    if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                        writer.writeheader()

                    writer.writerows(final_data)
            else:
                default_row = {
                    "Reference ID": str(row['ReferenceID']),
                    "Product URL": str(row['Product URL']),
                    "Product Title": "No",
                    "Keyword": str(row['Keywords']), 
                    "sku": str(row['SKU']),
                    "Product ID": product_id,
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