import pandas as pd

# Test the exact operation that fails
test_csv = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

with open('test_data.csv', 'w') as f:
    f.write(test_csv)

df = pd.read_csv('test_data.csv')

# Simulate what analyze_groups does
value_col = 'B'
group_col = 'C'

print("Original df:")
print(df)
print(f"\nColumns: {df.columns.tolist()}")

# Line 521: df = df[[value_col, group_col]].copy()
df = df[[value_col, group_col]].copy()
print(f"\nAfter subsetting df:")
print(df)
print(f"Type of df: {type(df)}")
print(f"Type of df[value_col]: {type(df[value_col])}")

# Line 522: df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
print(f"\nTrying pd.to_numeric on df[value_col]:")
try:
    result = pd.to_numeric(df[value_col], errors='coerce')
    print(f"Success! Result type: {type(result)}")
    print(result)
except TypeError as e:
    print(f"ERROR: {e}")
    print(f"df[value_col] = {repr(df[value_col])}")
