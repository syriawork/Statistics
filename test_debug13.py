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

# Test get_loc
value_col = 'C'
group_col = 'C'

value_loc = df.columns.get_loc(value_col)
group_loc = df.columns.get_loc(group_col)

print(f"\nvalue_loc = {repr(value_loc)} (type: {type(value_loc)})")
print(f"group_loc = {repr(group_loc)} (type: {type(group_loc)})")

# Test the conversion logic
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

# Test iloc
df_new = df.iloc[:, [value_idx, group_idx]].copy()
print(f"\ndf_new after iloc:")
print(df_new)
print(f"Columns: {df_new.columns.tolist()}")

# Rename columns
df_new.columns = ['C', 'C']
print(f"\ndf_new after renaming:")
print(df_new)
print(f"Columns: {df_new.columns.tolist()}")

# Test accessing df_new['C']
print(f"\nAccessing df_new['C']:")
print(f"Type: {type(df_new['C'])}")
print(df_new['C'])
