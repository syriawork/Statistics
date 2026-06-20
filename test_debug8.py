import pandas as pd

test_csv = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

with open('test.csv', 'w') as f:
    f.write(test_csv)

df = pd.read_csv('test.csv')

# Test when value_col == group_col
print("Test: When value_col == group_col")
value_col = 'B'
group_col = 'B'  # Same column!

try:
    df_subset = df[[value_col, group_col]].copy()
    print(f"df_subset shape: {df_subset.shape}")
    print(f"df_subset columns: {df_subset.columns.tolist()}")
    print(df_subset)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# What if one of them doesn't exist?
print("\n\nTest: When column doesn't exist")
value_col = 'NonExistent'
group_col = 'C'

try:
    df_subset = df[[value_col, group_col]].copy()
    print(f"df_subset: {df_subset}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
