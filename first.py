import pandas as pd

# Read the CSV file
input_file = "output_1.csv"
output_file = "output_1_formatted.csv"

# Load the data
df = pd.read_csv(input_file)

# Convert Reference ID to 4-digit format with leading zeros
df['Reference ID'] = df['Reference ID'].apply(lambda x: f'{int(x):04d}')

# Save the modified data
df.to_csv(output_file, index=False)

print(f"Converted {len(df)} Reference IDs to 4-digit format")
print(f"Modified file saved as: {output_file}")