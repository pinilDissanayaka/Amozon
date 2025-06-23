import csv

# Read the input CSV file
input_file = 'output.csv'
output_file = 'output_converted.csv'

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
     open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in reader:
        # Convert "Reference ID" to a four-digit number
        row["Reference ID"] = f'{int(row["Reference ID"]):04}'
        writer.writerow(row)
