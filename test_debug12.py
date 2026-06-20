import pandas as pd
import io

# Create a CSV with actual duplicate column names
csv_string = """B,C,B
101.1,102.1,101.5
101.0,102.0,101.0
100.9,100.9,100.5"""

print("Test 1: Reading CSV with duplicate header names using read_csv")
df = pd.read_csv(io.StringIO(csv_string))
print(f"DataFrame:\n{df}")
print(f"Columns: {df.columns.tolist()}")

# Try to reproduce the error
value_col = 'B'
group_col = 'C'
print(f"\nTrying analyze_groups logic with value_col='{value_col}', group_col='{group_col}'")
df_subset = df[[value_col, group_col]].copy()
print(f"df_subset columns: {df_subset.columns.tolist()}")

print("\n\nTest 2: What if we read CSV without renaming duplicates?")
# Use a different approach - manually set columns
df2 = pd.read_csv(io.StringIO(csv_string), header=0, on_bad_lines='skip')
print(f"DataFrame with default duplicate handling:\n{df2}")
print(f"Columns: {df2.columns.tolist()}")

print("\n\nTest 3: Force duplicate columns by manipulating after read")
df3 = pd.read_csv(io.StringIO(csv_string))
# Try to manually create duplicates
original_cols = list(df3.columns)
new_cols = original_cols.copy()
if len(new_cols) >= 2:
    new_cols[0] = new_cols[1]  # Make first column same as second
    df3.columns = new_cols
    
print(f"DataFrame after forcing duplicates:\n{df3}")
print(f"Columns: {df3.columns.tolist()}")

# Now test the error
print(f"\nAccessing df3['C']:")
try:
    result = df3['C']
    print(f"Type: {type(result)}")
    print(f"Result:\n{result}")
except Exception as e:
    print(f"Error: {e}")

print(f"\nTrying pd.to_numeric on df3['C']:")
try:
    result = pd.to_numeric(df3['C'], errors='coerce')
    print(f"Success!")
except TypeError as e:
    print(f"ERROR: {e}")
