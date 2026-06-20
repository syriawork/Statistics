import pandas as pd

# Test when df has duplicate column names
print("Test: DataFrame with duplicate column names")
df = pd.DataFrame({
    'B': [101.1, 101.0, 100.9],
    'C': [102.1, 102.0, 100.9]
})

# Add another column with the same name
df['B'] = [110.1, 110.0, 109.9]

print(f"DataFrame:\n{df}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\ndf['B'] type: {type(df['B'])}")
print(f"df['B']:\n{df['B']}")

# Try pd.to_numeric on duplicate columns
print("\n\nTrying pd.to_numeric on duplicate 'B' column:")
try:
    result = pd.to_numeric(df['B'], errors='coerce')
    print(f"Success! Type: {type(result)}")
    print(result)
except TypeError as e:
    print(f"Error: {e}")
