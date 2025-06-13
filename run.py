from amazon_test import open_browser, search_amazon, close_browser, setup_location, scrape_amazon
import pandas as pd
import csv
import time
import random
import os 




def amazon_search_many(postcode: str, city: str, search_keyword: str, product_id: str, product_url: str, run_count: int, driver, sku:str, max_pages: int = 3):
    time.sleep(random.uniform(3, 6))

    if run_count == 0:        
        if driver:
            setup_location(driver, postcode=postcode, city_name=city)
            time.sleep(random.uniform(3, 6))
            search_amazon(driver, keyword=search_keyword)
            time.sleep(random.uniform(3, 6))

            data=scrape_amazon(
                driver=driver,
                keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                sku=sku,
                max_pages=max_pages
            )
            
            if data:
                return data
    else:
        search_amazon(driver, keyword=search_keyword)
        time.sleep(random.uniform(3, 6))
        data=scrape_amazon(
                driver=driver,
                keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                sku=sku,
                max_pages=max_pages
        )
            
        
        if data:
            return data

    return None

def ebay_search_one(postcode: str, city: str, search_keyword: str, product_id: str, product_url: str, driver, sku, max_pages: int = 3):
    time.sleep(random.uniform(3, 6))

    if driver:
        search_amazon(driver, keyword=search_keyword)
        setup_location(driver, postcode=postcode, city_name=city)
        
        
        time.sleep(random.uniform(3, 6))
        

        data=scrape_amazon(
                driver=driver,
                keyword=search_keyword,
                product_id=product_id,
                product_url=product_url,
                sku=sku,
                max_pages=max_pages
            )
            
            
        if data:
            return data
    return None 

def main():
    df = pd.read_excel("Amazonkeywords.xlsx")
    output_file = "amazon_output.csv"
    base_url="https://www.amazon.com.au/"
    
    
    driver = open_browser(base_url=base_url)


    for row_index, row in df.iterrows():
        print(f"\nProcessing Row: {row_index + 1} of {len(df)}")
        print(f"\nSearching Keyword: {row['Keyword text']}")

        data = None
        
        product_id = str(row['ASIN'])
        
        try:
            data = amazon_search_many(
                postcode="2143",
                city="REGENTS PARK",
                search_keyword=str(row['Keyword text']),
                product_id=product_id,
                sku=str(row['SKU']),
                product_url=str(row['URL of the product']),
                run_count=row_index,
                driver=driver,
                max_pages=3
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
                    "Product URL": str(row['URL of the product']),
                    "Product Title": "No",
                    "Keyword": str(row['Keyword text']), 
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