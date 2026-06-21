from __future__ import annotations

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        'Biostat Decision Tool': 'Biostat Decision Tool',
        'Language': 'Language',
        'Select language': 'Select language',
        'Upload CSV': 'Upload CSV',
        'Preview': 'Preview',
        'Value column': 'Value column',
        'Group column': 'Group column',
        'Alpha': 'Alpha',
        'Outlier removal method': 'Outlier removal method',
        'Z-score threshold': 'Z-score threshold',
        'Paired samples (paired t-test / Wilcoxon)': 'Paired samples (paired t-test / Wilcoxon)',
        'Calculate Cp/CpK': 'Calculate Cp/CpK',
        'USL': 'USL',
        'LSL': 'LSL',
        'P-value correction': 'P-value correction',
        'Run analysis': 'Run analysis',
        'Outlier removal summary': 'Outlier removal summary',
        'USL must be greater than LSL to calculate Cp/CpK.': 'USL must be greater than LSL to calculate Cp/CpK.',
        'Shapiro-Wilk normality': 'Shapiro-Wilk normality',
        'Biostat Decision Tool report': 'Biostat Decision Tool report',
        'Graphs are available in the PDF or separate PNG exports.': 'Graphs are available in the PDF or separate PNG exports.',
        'Unable to render graph:': 'Unable to render graph:',
        'Analysis Results': 'Analysis Results',
        'Descriptive Statistics': 'Descriptive Statistics',
        'Assumption Checks': 'Assumption Checks',
        'Main Test': 'Main Test',
        'Post-hoc Results': 'Post-hoc Results',
        'No post-hoc comparisons performed.': 'No post-hoc comparisons performed.',
        'Outlier Summary': 'Outlier Summary',
        'Outlier method:': 'Outlier method:',
        'Process Capability': 'Process Capability',
        'Interpretation': 'Interpretation',
        'Graphs': 'Graphs',
        'Download': 'Download',
        'Download Excel report': 'Download Excel report',
        'Download PDF report': 'Download PDF report',
        'Graph images were not provided for PDF embedding.': 'Graph images were not provided for PDF embedding.',
        'Biostatistical Analysis Report': 'Biostatistical Analysis Report',
        'Study Information': 'Study Information',
        '1. Study Information': '1. Study Information',
        '2. Descriptive Statistics': '2. Descriptive Statistics',
        '3. Assumption Checks': '3. Assumption Checks',
        '4. Main Statistical Test': '4. Main Statistical Test',
        '5. Effect Size': '5. Effect Size',
        '6. Outlier Summary': '6. Outlier Summary',
        '7. Process Capability': '7. Process Capability',
        '8. Confidence Intervals': '8. Confidence Intervals',
        '7. Pairwise Comparisons': '7. Pairwise Comparisons',
        '8. Interpretation': '8. Interpretation',
        '9. Graphs': '9. Graphs',
        "Levene's test p = {_value}": "Levene's test p = {_value}",
        'to': 'to',
        'Only one group is available for analysis. No group comparison was performed.': 'Only one group is available for analysis. No group comparison was performed.',
        'Only one group present; no inferential test applied.': 'Only one group present; no inferential test applied.',
        'Biostat Decision Tool automated report for pharmaceutical R&D.': 'Biostat Decision Tool automated report for pharmaceutical R&D.',
        'Effect Size': 'Effect Size',
        'Outlier Summary Table': 'Outlier Summary',
        'Process Capability': 'Process Capability',
        'Confidence Intervals': 'Confidence Intervals',
        'Pairwise Comparisons': 'Pairwise Comparisons',
        'No pairwise comparisons were performed.': 'No pairwise comparisons were performed.',
        'Interpretation Section': 'Interpretation',
        'Analysis Results': 'Analysis Results',
        'A Note About Graphs': 'Graph images were not provided for PDF embedding.',
        'Comparison': 'Comparison',
        'Test': 'Test',
        'Mean Diff': 'Mean Diff',
        'p-value': 'p-value',
        'p-adj': 'p-adj',
        'Decision': 'Decision',
        'Group': 'Group',
        'N': 'N',
        'Mean': 'Mean',
        'Median': 'Median',
        'Std': 'Std',
        'SEM': 'SEM',
        'Min': 'Min',
        'Max': 'Max',
        'CV%': 'CV%',
        'Q1': 'Q1',
        'Q3': 'Q3',
        'IQR': 'IQR',
        'N Before': 'N Before',
        'N After': 'N After',
        'Removed': 'Removed',
        'Last Outlier Value': 'Last Outlier Value',
        'Statistic': 'Statistic',
        'Critical': 'Critical',
        'Rejected': 'Rejected',
        'Mean difference': 'Mean difference',
        '95% CI:': '95% CI:',
        'No valid numeric observations found after cleaning the selected columns.': 'No valid numeric observations found after cleaning the selected columns.',
        'Normality was assessed by Shapiro-Wilk test for each group: ': 'Normality was assessed by Shapiro-Wilk test for each group: ',
        'Normality could not be assessed for one or more groups due to sample size or invalid values.': 'Normality could not be assessed for one or more groups due to sample size or invalid values.',
        'Variance homogeneity was evaluated by Levene\'s test (p = {p}).': "Variance homogeneity was evaluated by Levene's test (p = {p}).",
        'The main test applied was {test}. The resulting p-value was {pvalue}.': 'The main test applied was {test}. The resulting p-value was {pvalue}.',
        'Decision: {decision}.': 'Decision: {decision}.',
        'Post-hoc analysis identified significant differences for: {comparisons}.': 'Post-hoc analysis identified significant differences for: {comparisons}.',
        'Post-hoc analysis did not identify significant pairwise differences.': 'Post-hoc analysis did not identify significant pairwise differences.',
        'paired t-test': 'paired t-test',
        'Wilcoxon signed-rank': 'Wilcoxon signed-rank',
        't-test': 't-test',
        'Welch t-test': 'Welch t-test',
        'Mann-Whitney U': 'Mann-Whitney U',
        'ANOVA': 'ANOVA',
        'Kruskal-Wallis': 'Kruskal-Wallis',
        'No comparison': 'No comparison',
        'Accept': 'Accept',
        'Reject': 'Reject',
        'Fail to Reject H0': 'Fail to Reject H0',
        'Reject H0': 'Reject H0',
        'None': 'None',
        'none': 'none',
        'iqr': 'IQR',
        'three-sigma': 'three-sigma',
        'grubbs': 'Grubbs',
        'dixon': 'Dixon',
        'bonferroni': 'bonferroni',
        'holm': 'holm',
        'fdr_bh': 'fdr_bh',
    },
}

OUTLIER_METHOD_LABELS: Dict[str, Dict[str, str]] = {
    'none': {'en': 'none'},
    'iqr': {'en': 'IQR'},
    'zscore': {'en': 'Z-score'},
    'three-sigma': {'en': 'three-sigma'},
    'grubbs': {'en': 'Grubbs'},
    'dixon': {'en': 'Dixon'},
}

P_CORRECTION_LABELS: Dict[str, Dict[str, str]] = {
    'none': {'en': 'none'},
    'bonferroni': {'en': 'bonferroni'},
    'holm': {'en': 'holm'},
    'fdr_bh': {'en': 'fdr_bh'},
}

TEST_LABELS: Dict[str, Dict[str, str]] = {
    'paired t-test': {'en': 'paired t-test'},
    'Wilcoxon signed-rank': {'en': 'Wilcoxon signed-rank'},
    't-test': {'en': 't-test'},
    'Welch t-test': {'en': 'Welch t-test'},
    'Mann-Whitney U': {'en': 'Mann-Whitney U'},
    'ANOVA': {'en': 'ANOVA'},
    'Kruskal-Wallis': {'en': 'Kruskal-Wallis'},
    'No comparison': {'en': 'No comparison'},
}

DECISION_LABELS: Dict[str, Dict[str, str]] = {
    'Accept': {'en': 'Accept'},
    'Reject': {'en': 'Reject'},
    'Fail to Reject H0': {'en': 'Fail to Reject H0'},
    'Reject H0': {'en': 'Reject H0'},
}


def translate(key: str, lang: str = 'en') -> str:
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS['en'].get(key, key))


def translate_option(option_key: str, lang: str = 'en') -> str:
    if option_key in OUTLIER_METHOD_LABELS:
        return OUTLIER_METHOD_LABELS[option_key].get(lang, option_key)
    if option_key in P_CORRECTION_LABELS:
        return P_CORRECTION_LABELS[option_key].get(lang, option_key)
    if option_key in TEST_LABELS:
        return TEST_LABELS[option_key].get(lang, option_key)
    if option_key in DECISION_LABELS:
        return DECISION_LABELS[option_key].get(lang, option_key)
    return TRANSLATIONS.get(lang, {}).get(option_key, TRANSLATIONS['en'].get(option_key, option_key))


def translate_test_name(name: str, lang: str = 'en') -> str:
    return TEST_LABELS.get(name, {}).get(lang, name)


def translate_decision(decision: str, lang: str = 'en') -> str:
    return DECISION_LABELS.get(decision, {}).get(lang, decision)


def translate_dataframe_columns(df, lang: str = 'en'):
    return df
