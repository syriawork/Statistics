import sys
sys.path.insert(0, 'E:\\programs and applications\\Statistics')

import pandas as pd
from stats_analysis.analysis import analyze_groups

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

print("Test DataFrame with duplicate columns:")
print(f"DataFrame:\n{df}")
print(f"Columns: {df.columns.tolist()}")

# Test with duplicate columns
print("\n\nTesting analyze_groups with duplicate column names:")
try:
    result = analyze_groups(df, 'C', 'C', alpha=0.05)
    print("SUCCESS! No error occurred.")
    print(f"Result keys: {result.keys()}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test with normal DataFrame
print("\n\nTesting analyze_groups with normal DataFrame:")
df2 = pd.DataFrame({
    'value': [101.1, 101.0, 100.9, 102.1, 102.0, 100.9],
    'group': ['A', 'A', 'A', 'B', 'B', 'B']
})
try:
    result = analyze_groups(df2, 'value', 'group', alpha=0.05)
    print("SUCCESS! analyze_groups worked with normal DataFrame")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
