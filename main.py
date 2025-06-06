from utils import search_ebay
import pandas as pd
import csv
import time
import random
import os

df = pd.read_csv("results.csv")


output_file = "output.csv"


for row_index, row in df.iterrows():
    print(f"\nSearching Keyword: {row['Keyword']}")

    data = None

    try:
        data = search_ebay(
            base_url="https://www.ebay.com.au",
            postcode="2143",
            country="Australia - AUS",
            search_keyword=row['Keyword'],
            product_id=str(row['Product ID']),
            product_url=row['Link of the Product'], 
            max_pages=3
        )
        
        
        if data:
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=data[0].keys(),
                    quoting=csv.QUOTE_ALL
                )

                # ✅ Write headers only if file is new or empty
                if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                    writer.writeheader()

                writer.writerows(data)

    except Exception as e:
        print(f"❌ Error processing row {row_index}: {e.args}")


    if row_index % 10 == 0:
        df.to_csv("backup_results.csv", index=False)

    time.sleep(random.uniform(3, 6))
    
    if row_index == 13:
        print("Reached the limit of 13 iterations, stopping further processing.")
        break




