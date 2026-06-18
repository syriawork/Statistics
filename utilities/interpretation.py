from __future__ import annotations

from typing import Dict


def generate_interpretation(result: Dict[str, object]) -> str:
    assumptions = result.get('assumptions', {})
    main_test = result.get('main_test', {})
    posthoc = result.get('posthoc', [])

    lines = []
    normality = assumptions.get('normality', {})
    normal_groups = [f"{group} (p={p:.4f})" for group, p in normality.items() if p is not None]
    if normal_groups:
        lines.append('Normality was assessed by Shapiro-Wilk test for each group: ' + ', '.join(normal_groups) + '.')
    else:
        lines.append('Normality could not be assessed for one or more groups due to sample size or invalid values.')

    levene_p = assumptions.get('levene_p')
    if levene_p is not None:
        lines.append(f"Variance homogeneity was evaluated by Levene's test (p = {levene_p:.4f}).")

    main_pvalue = main_test.get('pvalue')
    main_pvalue_str = f"{main_pvalue:.4g}" if main_pvalue is not None else 'None'
    lines.append(f"The main test applied was {main_test.get('test')}. The resulting p-value was {main_pvalue_str}.")
    lines.append(f"Decision: {main_test.get('decision')}.")
    interpretation = main_test.get('interpretation')
    if interpretation:
        lines.append(interpretation)

    if posthoc:
        significant = [row for row in posthoc if row.get('decision') == 'Reject H0']
        if significant:
            comparisons = ', '.join([row.get('groups', '') for row in significant])
            lines.append(f"Post-hoc analysis identified significant differences for: {comparisons}.")
        else:
            lines.append('Post-hoc analysis did not identify significant pairwise differences.')

    return ' '.join(lines)
