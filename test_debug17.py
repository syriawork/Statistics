import pandas as pd

# Test if creating DataFrame from Series works correctly
df_orig = pd.DataFrame({
    'C': [101.1, 101.0, 100.9],
    'C': [102.1, 102.0, 100.9]
})
print(f"Original df with duplicate columns:")
print(df_orig)
print(f"Columns: {df_orig.columns.tolist()}")

# Simulate the solution
value_col_internal = '__selected_value__'
group_col_internal = '__selected_group__'

df = pd.DataFrame({
    value_col_internal: [101.1, 101.0, 100.9],
    group_col_internal: [102.1, 102.0, 100.9]
})

print(f"\nDataFrame with internal names:")
print(df)
print(f"Columns: {df.columns.tolist()}")

# Recreate with original column names
value_col = 'C'
group_col = 'C'

df_for_posthoc = pd.DataFrame({
    value_col: df[value_col_internal].values,
    group_col: df[group_col_internal].values
})

print(f"\nDataFrame recreated with original names:")
print(df_for_posthoc)
print(f"Columns: {df_for_posthoc.columns.tolist()}")

# Test groupby
print(f"\nTesting groupby:")
try:
    result = df_for_posthoc.groupby('C', observed=True)
    print(f"Groupby succeeded: {result}")
except Exception as e:
    print(f"Groupby failed: {type(e).__name__}: {e}")
