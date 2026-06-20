import pandas as pd

# Create a DataFrame with unique temporary column names first
selected_data = {
    'temp_value': [101.1, 101.0, 100.9],
    'temp_group': [102.1, 102.0, 100.9]
}
df = pd.DataFrame(selected_data)

print(f"DataFrame before renaming:")
print(df)
print(f"Columns: {df.columns.tolist()}")

# Rename to final names
value_col = 'C'
group_col = 'C'
df.columns = [value_col, group_col]

print(f"\nDataFrame after renaming to ['{value_col}', '{group_col}']:")
print(df)
print(f"Columns: {df.columns.tolist()}")

# Test accessing df[value_col]
print(f"\nAccessing df['{value_col}']:")
print(f"Type: {type(df[value_col])}")
print(df[value_col])

# Test pd.to_numeric
print(f"\nTesting pd.to_numeric:")
try:
    result = pd.to_numeric(df[value_col], errors='coerce')
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
