import pandas as pd

# Test when column name contains leading/trailing spaces or special characters
test_cases = [
    # Case 1: Column with spaces
    ("A,B,C\n,101.1,102.1\n,101.0,102.0\n,100.9,100.9", "Case 1: Normal"),
    # Case 2: Column names with leading spaces
    (" A,B,C\n,101.1,102.1\n,101.0,102.0\n,100.9,100.9", "Case 2: Leading space in first column"),
    # Case 3: Column names with trailing spaces
    ("A ,B,C\n,101.1,102.1\n,101.0,102.0\n,100.9,100.9", "Case 3: Trailing space in first column"),
]

for i, (csv_content, description) in enumerate(test_cases):
    print(f"\n{'='*60}")
    print(description)
    print('='*60)
    
    with open(f'test_data_{i}.csv', 'w') as f:
        f.write(csv_content)
    
    df = pd.read_csv(f'test_data_{i}.csv')
    print(f"\nDataFrame:\n{df}")
    print(f"\nColumns: {repr(df.columns.tolist())}")
    
    # Try accessing different columns
    for col in df.columns:
        print(f"\nColumn {repr(col)}:")
        print(f"  Type when accessing df[{repr(col)}]: {type(df[col])}")
        try:
            result = pd.to_numeric(df[col], errors='coerce')
            print(f"  pd.to_numeric: Success")
        except TypeError as e:
            print(f"  pd.to_numeric ERROR: {e}")
