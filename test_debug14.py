import numpy as np
import pandas as pd

# Create a DataFrame with duplicate column names
df = pd.DataFrame({
    'B': [101.1, 101.0, 100.9],
    'C': [102.1, 102.0, 100.9]
})

# Manually create duplicate column names
original_cols = list(df.columns)
new_cols = original_cols.copy()
if len(new_cols) >= 2:
    new_cols[0] = new_cols[1]  # Make first column same as second
    df.columns = new_cols

print("Original DataFrame:")
print(df)
print(f"Columns: {df.columns.tolist()}")

value_col = 'C'
group_col = 'C'

value_loc = df.columns.get_loc(value_col)
group_loc = df.columns.get_loc(group_col)

print(f"\nvalue_loc = {repr(value_loc)}")
print(f"group_loc = {repr(group_loc)}")

# Convert
def extract_index(loc):
    if isinstance(loc, slice):
        return loc.start
    elif isinstance(loc, np.ndarray):
        return np.where(loc)[0][0]
    else:
        return loc

value_idx = extract_index(value_loc)
group_idx = extract_index(group_loc)

print(f"\nvalue_idx = {value_idx}")
print(f"group_idx = {group_idx}")

# Create new DataFrame
selected_data = {
    'value': df.iloc[:, value_idx].values,
    'group': df.iloc[:, group_idx].values
}
df_new = pd.DataFrame(selected_data)
df_new.columns = [value_col, group_col]

print(f"\ndf_new:")
print(df_new)
print(f"Columns: {df_new.columns.tolist()}")

# Test accessing df_new[value_col]
print(f"\nAccessing df_new['{value_col}']:")
print(f"Type: {type(df_new[value_col])}")
print(df_new[value_col])

# Test pd.to_numeric
print(f"\nTesting pd.to_numeric:")
try:
    result = pd.to_numeric(df_new[value_col], errors='coerce')
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
