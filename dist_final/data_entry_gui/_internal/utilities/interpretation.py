from __future__ import annotations

from typing import Dict

from utilities.translations import translate, translate_decision, translate_test_name


def generate_interpretation(result: Dict[str, object], lang: str = 'en') -> str:
    assumptions = result.get('assumptions', {})
    main_test = result.get('main_test', {})
    posthoc = result.get('posthoc', [])

    lines = []
    normality = assumptions.get('normality', {})
    normal_groups = [f"{group} (p={p:.4f})" for group, p in normality.items() if p is not None]
    if normal_groups:
        lines.append(translate('Normality was assessed by Shapiro-Wilk test for each group: ', lang) + ', '.join(normal_groups) + '.')
    else:
        lines.append(translate('Normality could not be assessed for one or more groups due to sample size or invalid values.', lang))

    levene_p = assumptions.get('levene_p')
    if levene_p is not None:
        lines.append(translate("Variance homogeneity was evaluated by Levene's test (p = {p}).", lang).format(p=f"{levene_p:.4f}"))

    warning = result.get('sample_size_warning')
    if warning:
        lines.append(translate(warning, lang))

    main_pvalue = main_test.get('pvalue')
    main_pvalue_str = f"{main_pvalue:.4g}" if main_pvalue is not None else translate('None', lang)
    lines.append(translate('The main test applied was {test}. The resulting p-value was {pvalue}.', lang).format(
        test=translate_test_name(str(main_test.get('test')), lang),
        pvalue=main_pvalue_str,
    ))
    lines.append(translate('Decision: {decision}.', lang).format(decision=translate_decision(str(main_test.get('decision')), lang)))
    interpretation = main_test.get('interpretation')
    if interpretation:
        lines.append(interpretation)

    if posthoc:
        significant = [row for row in posthoc if row.get('decision') == 'Reject H0']
        if significant:
            comparisons = ', '.join([row.get('groups', '') for row in significant])
            lines.append(translate('Post-hoc analysis identified significant differences for: {comparisons}.', lang).format(comparisons=comparisons))
        else:
            lines.append(translate('Post-hoc analysis did not identify significant pairwise differences.', lang))

    return ' '.join(lines)
