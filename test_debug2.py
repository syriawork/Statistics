import pandas as pd

# Test different scenarios
test_csv1 = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

# Scenario where first column has index-like behavior
test_csv2 = """A,B,C
1,101.1,102.1
2,101.0,102.0
3,100.9,100.9"""

# Scenario with unnamed index
test_csv3 = """,A,B,C
0,,101.1,102.1
1,,101.0,102.0
2,,100.9,100.9"""

for i, test_csv in enumerate([test_csv1, test_csv2, test_csv3], 1):
    print(f"\n=== Test {i} ===")
    with open(f'test_data_{i}.csv', 'w') as f:
        f.write(test_csv)
    
    df = pd.read_csv(f'test_data_{i}.csv')
    print(f"DataFrame:\n{df}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nData types:\n{df.dtypes}")
    
    # Try selecting columns
    try:
        subset = df[['B', 'C']]
        print(f"\nSubset df[['B', 'C']] type: {type(subset)}")
        print(subset)
    except Exception as e:
        print(f"Error selecting columns: {e}")
