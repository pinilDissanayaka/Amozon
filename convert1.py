import csv

def format_reference_ids(input_file='output_1_formatted.csv', output_file='output_formatted_2.csv'):
    """
    Reads a CSV file and converts the 'Reference ID' column to a four-digit format.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the formatted CSV file
    """
    try:
        # Open the input and output files
        with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
            # Create reader and writer objects
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            # Write the header row
            writer.writeheader()
            
            # Process each row
            for row in reader:
                # Convert the Reference ID to a four-digit format
                if row['ReferenceID'] and row['ReferenceID'] != 'No':
                    try:
                        ref_id = int(row['ReferenceID'])
                        row['ReferenceID'] = f'{ref_id:04d}'
                    except ValueError:
                        # Keep original value if conversion fails
                        pass
                
                # Write the modified row to the output file
                writer.writerow(row)
        
        print(f"Conversion complete! The formatted CSV has been saved to {output_file}")
    
    except FileNotFoundError:
        print(f"Error: Could not find the file {input_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
if __name__ == "__main__":
    format_reference_ids()