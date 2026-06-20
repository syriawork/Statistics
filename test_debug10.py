import pandas as pd

# Test when df has duplicate column names (the real way)
print("Test: DataFrame with TRUE duplicate column names")
df = pd.DataFrame([[101.1, 102.1],
                    [101.0, 102.0],
                    [100.9, 100.9]])
df.columns = ['B', 'B']

print(f"DataFrame:\n{df}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nAccessing df['B']:")
print(f"Type: {type(df['B'])}")
print(f"Content:\n{df['B']}")

# Try pd.to_numeric on duplicate columns
print("\n\nTrying pd.to_numeric on duplicate 'B' columns:")
try:
    result = pd.to_numeric(df['B'], errors='coerce')
    print(f"Success! Type: {type(result)}")
    print(result)
except TypeError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"Other error: {type(e).__name__}: {e}")
