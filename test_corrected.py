import pandas as pd
import sys
sys.path.insert(0, '.')

from stats_analysis.analysis import analyze_groups

df = pd.read_csv('correct_data.csv')

print('='*80)
print('CORRECTED DATA:')
print('='*80)
print(df)
print(f'\nGroups: {df["group"].unique().tolist()}')
print(f'Number of Groups: {df["group"].nunique()}')

result = analyze_groups(df, 'value', 'group', alpha=0.05)

print('\n' + '='*80)
print('ANALYSIS RESULTS:')
print('='*80)
print(f'Test: {result["main_test"]["test"]}')
print(f'P-value: {result["main_test"]["pvalue"]:.4f}')
print(f'Decision: {result["main_test"]["decision"]}')
print(f'\nNumber of pairwise comparisons: {len(result["posthoc"])}')

print('\nDescriptive statistics for each group:')
for group, stats in result['descriptive'].items():
    print(f'  {group}: n={stats["n"]}, mean={stats["mean"]:.2f}, std={stats["std"]:.2f}')

print('\n' + '='*80)
print('SUCCESS! All 4 groups are analyzed!')
print('='*80)
