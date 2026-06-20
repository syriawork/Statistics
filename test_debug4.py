import pandas as pd

# Test when value_col is a list instead of string
test_csv = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

with open('test_data.csv', 'w') as f:
    f.write(test_csv)

df = pd.read_csv('test_data.csv')

# Test 1: Normal case (value_col is a string)
print("Test 1: value_col as string")
value_col = 'B'
try:
    result = df[[value_col]]
    print(f"df[[value_col]] type: {type(result)}")
    print(result)
    print(f"\ndf[value_col] type: {type(df[value_col])}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Problematic case (value_col is a list)
print("\n\nTest 2: value_col as list")
value_col = ['B']
try:
    subset = df[[value_col, 'C']].copy()
    print(f"Created subset")
except Exception as e:
    print(f"Error creating subset: {e}")
    
# Test 3: What happens with nested lists
print("\n\nTest 3: What if value_col becomes nested list")
value_col = 'B'
group_col = 'C'
df_subset = df[[value_col, group_col]].copy()
print(f"df_subset type: {type(df_subset)}")
print(f"df_subset[value_col] type: {type(df_subset[value_col])}")

# What if someone passes [value_col, group_col] with value_col as list?
print("\n\nTest 4: Nested list issue")
try:
    value_col = ['B']
    group_col = 'C'
    df_subset = df[[value_col, group_col]].copy()  # This will fail
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
