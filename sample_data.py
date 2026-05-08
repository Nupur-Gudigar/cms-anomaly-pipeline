import pandas as pd

input_file = "data/raw/2023/MUP_DPR_RY25_P04_V10_DY23_NPIBN.csv"
output_file = "data/raw/2023/cms_partd_2023_sample.csv"

print("Reading file... this may take a minute.")
# Read only 500,000 rows
df = pd.read_csv(
    input_file,
    nrows=500000,
    low_memory=False
)
print(f"Rows loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 3 rows preview:")
print(df.head(3))

# Save the sample
df.to_csv(output_file, index=False)
print(f"\nSample saved to {output_file}")