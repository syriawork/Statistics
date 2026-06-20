import pandas as pd

# Test various CSV reading scenarios that could cause duplicate columns
test_cases = [
    # Case 1: Columns with same names separated by spaces
    ("A,B,C,B\n,101.1,102.1,101.5\n,101.0,102.0,101.0\n,100.9,100.9,100.5", "Two 'B' columns with spaces"),
    
    # Case 2: User copies data incorrectly
    ("B,C,B\n101.1,102.1,101.5\n101.0,102.0,101.0\n100.9,100.9,100.5", "Duplicate 'B' columns"),
    
    # Case 3: Empty header gets filled by pandas
    ("A,,C\n,101.1,102.1\n,101.0,102.0\n,100.9,100.9", "Empty column header"),
    
    # Case 4: MultiIndex columns
    ("Level0,Level0\nB,C\n101.1,102.1\n101.0,102.0\n100.9,100.9", "MultiIndex style"),
]

for csv_content, description in test_cases:
    print(f"\n{'='*70}")
    print(f"Test: {description}")
    print('='*70)
    
    with open('test_scenario.csv', 'w') as f:
        f.write(csv_content)
    
    try:
        df = pd.read_csv('test_scenario.csv')
        print(f"DataFrame:\n{df}")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"Column dtypes:\n{df.dtypes}")
        
        # Check for duplicate columns
        if len(df.columns) != len(set(df.columns)):
            print("\n⚠️  WARNING: Duplicate column names detected!")
            duplicate_cols = [col for col in df.columns if list(df.columns).count(col) > 1]
            print(f"Duplicate columns: {set(duplicate_cols)}")
            
            for col in set(duplicate_cols):
                print(f"\n  Accessing df[{repr(col)}]:")
                accessed = df[col]
                print(f"    Type: {type(accessed)}")
                if isinstance(accessed, pd.DataFrame):
                    print(f"    Shape: {accessed.shape}")
                    print(f"    Columns in returned DataFrame: {accessed.columns.tolist()}")
    except Exception as e:
        print(f"Error reading CSV: {type(e).__name__}: {e}")
