import pandas as pd

# Read the CSV file
df = pd.read_csv('output.csv')

# Filter out rows where "Is Top 24 Advertised" is "Yes"
filtered_df = df[df["Is Top 24 Advertised"] != "Yes"]

# Save the filtered data to a new CSV file
filtered_df.to_csv('filtered_output.csv', index=False)

# Print summary
print(f"Original file had {len(df)} rows.")
print(f"Filtered file has {len(filtered_df)} rows.")
print(f"Removed {len(df) - len(filtered_df)} rows where 'Is Top 24 Advertised' was 'Yes'.")