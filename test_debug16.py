import pandas as pd

# Test with unique column names from the start
df = pd.DataFrame({
    '__value__': [101.1, 101.0, 100.9],
    '__group__': [102.1, 102.0, 100.9]
})
df.columns = ['C', 'C']

print(f"DataFrame:")
print(df)
print(f"Columns: {df.columns.tolist()}")

# Test accessing df['C']
print(f"\nAccessing df['C']:")
print(f"Type: {type(df['C'])}")
print(df['C'])

# Test pd.to_numeric
print(f"\nTesting pd.to_numeric:")
try:
    result = pd.to_numeric(df['C'], errors='coerce')
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
