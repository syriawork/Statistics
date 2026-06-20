import pandas as pd
import sys
sys.path.insert(0, 'E:\\programs and applications\\Statistics')

from stats_analysis.analysis import analyze_groups

# Create test data similar to what the user provided in the image
# The image shows columns A (empty), B (101.1, 101.0, 100.9), C (102.1, 102.0, 100.9)
test_csv_content = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

# Save as CSV
with open('user_test_data.csv', 'w') as f:
    f.write(test_csv_content)

# Read back
df = pd.read_csv('user_test_data.csv')

print("=" * 70)
print("TEST: User's data from image")
print("=" * 70)
print(f"\nDataFrame loaded from CSV:")
print(df)
print(f"\nColumns: {df.columns.tolist()}")
print(f"Column types: {df.dtypes.to_dict()}")

# Try the analysis as the user would
value_col = 'B'
group_col = 'C'

print(f"\n\nAttempting analysis with:")
print(f"  value_col = '{value_col}'")
print(f"  group_col = '{group_col}'")

try:
    result = analyze_groups(df, value_col, group_col, alpha=0.05)
    print("\n✓ SUCCESS! Analysis completed without error!")
    print(f"\nResults keys: {result.keys()}")
    print(f"\nDescriptive statistics:")
    for group, stats in result.get('descriptive', {}).items():
        print(f"  Group {group}: n={stats.get('n')}, mean={stats.get('mean'):.4f}, std={stats.get('std'):.4f}")
except Exception as e:
    print(f"\n✗ FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Clean up
import os
os.remove('user_test_data.csv')
