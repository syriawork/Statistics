import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.stats.multitest as smm
from utilities.translations import translate


def remove_outliers_iqr(df, value_col, group_col):
    """Remove outliers per group using the IQR rule. Returns (clean_df, summary_df)."""
    frames = []
    summary = []
    for g, sub in df.groupby(group_col):
        # coerce to numeric for IQR calculations; non-numeric become NaN and are excluded
        numeric = pd.to_numeric(sub[value_col], errors='coerce')
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = numeric.between(lower, upper)
        # mask is a boolean Series aligned with `sub`; treat NaN as False
        removed = (~mask.fillna(False)).sum()
        summary.append({'group': g, 'n_before': len(sub), 'n_after': int(mask.sum()), 'removed': int(removed)})
        frames.append(sub.loc[mask.fillna(False)])
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def _group_stats(series):
    return {'n': int(series.count()), 'mean': float(series.mean()), 'std': float(series.std())}


def analyze_groups(df, value_col, group_col, alpha=0.05, p_correction=None, language: str = 'en'):
    """
    Analyze groups and choose appropriate test.
    Returns a dict with overall summary and pairwise decisions.
    Decision: 'Accept' means no significant difference (p >= alpha).
    """
    groups = [g for g, _ in df.groupby(group_col)]

    # ensure the value column is numeric; coerce non-numeric to NaN
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    if df[value_col].dropna().empty:
        raise ValueError(f"No numeric values found in the selected value column: '{value_col}'.\n"
                         "Make sure you selected the numeric column (not the group labels).")

    # build group series of numeric values (NaNs removed)
    grouped = {g: grp[value_col].dropna() for g, grp in df.groupby(group_col)}

    # basic stats
    stats_summary = {g: _group_stats(s) for g, s in grouped.items()}

    result = {'groups': stats_summary}

    k = len(grouped)
    # decide test
    if k == 1:
        result['message'] = translate('Only one group present; no inferential test applied.', language)
        return result

    # check normality per group (Shapiro if n reasonable)
    normal = {}
    for g, s in grouped.items():
        n = len(s)
        if n < 3:
            normal[g] = False
            continue
        if n > 5000:
            normal[g] = False
            continue
        try:
            p = stats.shapiro(s)[1]
            normal[g] = p >= alpha
        except Exception:
            normal[g] = False
    result['normality'] = normal

    # For two groups: use t-test (Welch if unequal variances) or Mann-Whitney if non-normal
    if k == 2:
        gnames = list(grouped.keys())
        a = grouped[gnames[0]]
        b = grouped[gnames[1]]
        # variance test
        try:
            levene_p = stats.levene(a, b)[1]
        except Exception:
            levene_p = 0.0
        equal_var = levene_p >= alpha
        if normal[gnames[0]] and normal[gnames[1]]:
            tstat, pval = stats.ttest_ind(a, b, equal_var=equal_var)
            test_name = 't-test (equal_var)' if equal_var else 'Welch t-test'
        else:
            # use Mann-Whitney U
            test_name = 'Mann-Whitney U'
            try:
                pval = stats.mannwhitneyu(a, b, alternative='two-sided')[1]
            except Exception:
                pval = 1.0

        decision = 'Accept' if pval >= alpha else 'Reject'
        result.update({'test': test_name, 'pvalue': float(pval), 'decision': decision, 'levene_p': float(levene_p)})
        result['pairwise'] = [{'groups': f"{gnames[0]} vs {gnames[1]}", 'test': test_name, 'pvalue': float(pval), 'decision': decision}]
        return result

    # For >2 groups: use ANOVA if normal and variances similar, otherwise Kruskal-Wallis
    samples = list(grouped.values())
    all_normal = all(normal.values())
    try:
        levene_p = stats.levene(*samples)[1]
    except Exception:
        levene_p = 0.0
    equal_var = levene_p >= alpha

    if all_normal and equal_var:
        fstat, pval = stats.f_oneway(*samples)
        test_name = 'ANOVA'
    else:
        try:
            hstat, pval = stats.kruskal(*samples)
            test_name = 'Kruskal-Wallis'
        except Exception:
            pval = 1.0
            test_name = 'Kruskal-Wallis'

    decision = 'Accept' if pval >= alpha else 'Reject'
    result.update({'test': test_name, 'pvalue': float(pval), 'decision': decision, 'levene_p': float(levene_p)})

    # pairwise post-hoc (Dunn or Mann-Whitney) - keep simple: all pairwise Mann-Whitney
    pairs = []
    raw_pvals = []
    names = list(grouped.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = grouped[names[i]]
            b = grouped[names[j]]
            try:
                p = stats.mannwhitneyu(a, b, alternative='two-sided')[1]
                testn = 'Mann-Whitney U'
            except Exception:
                p = 1.0
                testn = 'Mann-Whitney U'
            raw_pvals.append(p)
            pairs.append({'groups': f"{names[i]} vs {names[j]}", 'test': testn, 'pvalue': float(p)})

    # Apply multiple-comparisons correction if requested
    if p_correction in ('bonferroni', 'fdr_bh') and raw_pvals:
        method = 'bonferroni' if p_correction == 'bonferroni' else 'fdr_bh'
        rej, pvals_corr, _, _ = smm.multipletests(raw_pvals, alpha=alpha, method=method)
        # attach corrected p-values and decisions
        for idx, row in enumerate(pairs):
            row['pvalue_corrected'] = float(pvals_corr[idx])
            row['decision'] = 'Accept' if pvals_corr[idx] >= alpha else 'Reject'
    else:
        for row in pairs:
            row['decision'] = 'Accept' if row['pvalue'] >= alpha else 'Reject'
    result['pairwise'] = pairs
    return result
