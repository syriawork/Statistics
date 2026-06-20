import pandas as pd

# Test data from the image
test_csv = """A,B,C
,101.1,102.1
,101.0,102.0
,100.9,100.9"""

# Write and read
with open('test_data.csv', 'w') as f:
    f.write(test_csv)

df = pd.read_csv('test_data.csv')
print('DataFrame:')
print(df)
print('\nColumn types:')
print(df.dtypes)
print('\nColumn A:')
print(repr(df['A']))
print('\nTrying pd.to_numeric on column A:')
try:
    result = pd.to_numeric(df['A'], errors='coerce')
    print(result)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
