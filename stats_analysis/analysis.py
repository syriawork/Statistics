from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.stats.multitest as smm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from utilities.interpretation import generate_interpretation


def remove_outliers_iqr(df: pd.DataFrame, value_col: str, group_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Remove outliers per group using the IQR rule."""
    frames: List[pd.DataFrame] = []
    summary: List[Dict[str, object]] = []
    for g, sub in df.groupby(group_col, observed=True):
        numeric = pd.to_numeric(sub[value_col], errors='coerce')
        q1 = numeric.quantile(0.25)
        q3 = numeric.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = numeric.between(lower, upper)
        removed = (~mask.fillna(False)).sum()
        summary.append({
            'group': g,
            'n_before': int(len(sub)),
            'n_after': int(mask.sum()),
            'removed': int(removed),
            'q1': float(q1) if pd.notna(q1) else None,
            'q3': float(q3) if pd.notna(q3) else None,
            'iqr': float(iqr) if pd.notna(iqr) else None,
        })
        frames.append(sub.loc[mask.fillna(False)])
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def _mode_value(series: pd.Series) -> Optional[float]:
    mode_vals = series.mode()
    if mode_vals.empty:
        return None
    return float(mode_vals.iloc[0])


def _describe_series(series: pd.Series) -> Dict[str, Optional[float]]:
    n = int(series.count())
    mean = float(series.mean()) if n else None
    std = float(series.std(ddof=1)) if n else None
    sem = float(series.sem(ddof=1)) if n else None
    q1 = float(series.quantile(0.25)) if n else None
    q3 = float(series.quantile(0.75)) if n else None
    iqr = float(q3 - q1) if n else None
    return {
        'n': n,
        'mean': mean,
        'mode': _mode_value(series) if n else None,
        'median': float(series.median()) if n else None,
        'std': std,
        'variance': float(series.var(ddof=1)) if n else None,
        'sem': sem,
        'min': float(series.min()) if n else None,
        'max': float(series.max()) if n else None,
        'range': float(series.max() - series.min()) if n else None,
        'cv_pct': float(std / mean * 100) if n and mean not in (0, None) else None,
        'skewness': float(stats.skew(series, bias=False)) if n > 2 else None,
        'kurtosis': float(stats.kurtosis(series, fisher=True, bias=False)) if n > 3 else None,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
    }


def _numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors='coerce').dropna()


def z_score_outlier_mask(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    numeric = _numeric_series(series)
    if numeric.empty:
        return pd.Series([], dtype=bool)
    z_scores = np.abs((numeric - numeric.mean()) / numeric.std(ddof=1))
    return z_scores > threshold


def three_sigma_outlier_mask(series: pd.Series) -> pd.Series:
    numeric = _numeric_series(series)
    if numeric.empty:
        return pd.Series([], dtype=bool)
    mean = numeric.mean()
    std = numeric.std(ddof=1)
    lower = mean - 3 * std
    upper = mean + 3 * std
    return ~numeric.between(lower, upper)


def remove_outliers_zscore(df: pd.DataFrame, value_col: str, group_col: str, threshold: float = 3.0) -> Tuple[pd.DataFrame, pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    summary: List[Dict[str, object]] = []
    for g, sub in df.groupby(group_col, observed=True):
        numeric = pd.to_numeric(sub[value_col], errors='coerce')
        mask = ~z_score_outlier_mask(numeric, threshold)
        removed = (~mask.fillna(False)).sum()
        summary.append({
            'group': g,
            'n_before': int(len(sub)),
            'n_after': int(mask.sum()),
            'removed': int(removed),
            'threshold': threshold,
        })
        frames.append(sub.loc[mask.fillna(False)])
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def remove_outliers_three_sigma(df: pd.DataFrame, value_col: str, group_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    summary: List[Dict[str, object]] = []
    for g, sub in df.groupby(group_col, observed=True):
        numeric = pd.to_numeric(sub[value_col], errors='coerce')
        mask = ~three_sigma_outlier_mask(numeric)
        removed = (~mask.fillna(False)).sum()
        summary.append({
            'group': g,
            'n_before': int(len(sub)),
            'n_after': int(mask.sum()),
            'removed': int(removed),
        })
        frames.append(sub.loc[mask.fillna(False)])
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def remove_outliers_grubbs(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    summary: List[Dict[str, object]] = []
    for g, sub in df.groupby(group_col, observed=True):
        current = sub.copy()
        removed_count = 0
        last_detection: Dict[str, Optional[object]] = {}
        while True:
            numeric = pd.to_numeric(current[value_col], errors='coerce')
            result = detect_grubbs_outlier(numeric, alpha)
            if not result['rejected'] or result['outlier_index'] is None:
                break
            mask = numeric.index != result['outlier_index']
            current = current.loc[mask]
            removed_count += 1
            last_detection = result
            if len(current) < 3:
                break
        summary.append({
            'group': g,
            'n_before': int(len(sub)),
            'n_after': int(len(current)),
            'removed': int(removed_count),
            'last_outlier_value': last_detection.get('outlier_value'),
            'last_statistic': last_detection.get('statistic'),
            'last_critical_value': last_detection.get('critical_value'),
            'last_rejected': last_detection.get('rejected', False),
        })
        frames.append(current)
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def remove_outliers_dixon(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    alpha: float = 0.05,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    summary: List[Dict[str, object]] = []
    for g, sub in df.groupby(group_col, observed=True):
        current = sub.copy()
        removed_count = 0
        last_detection: Dict[str, Optional[object]] = {}
        while True:
            numeric = pd.to_numeric(current[value_col], errors='coerce')
            result = detect_dixon_outlier(numeric)
            if not result['rejected'] or result['outlier_index'] is None:
                break
            mask = numeric.index != result['outlier_index']
            current = current.loc[mask]
            removed_count += 1
            last_detection = result
            if len(current) < 3:
                break
        summary.append({
            'group': g,
            'n_before': int(len(sub)),
            'n_after': int(len(current)),
            'removed': int(removed_count),
            'last_outlier_value': last_detection.get('outlier_value'),
            'last_statistic': last_detection.get('statistic'),
            'last_critical_value': last_detection.get('critical_value'),
            'last_rejected': last_detection.get('rejected', False),
        })
        frames.append(current)
    clean = pd.concat(frames, ignore_index=True)
    return clean, pd.DataFrame(summary)


def remove_outliers(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    method: str = 'iqr',
    z_threshold: float = 3.0,
    alpha: float = 0.05,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    method = method.lower()
    if method == 'none':
        return df.copy(), pd.DataFrame([])
    if method == 'iqr':
        return remove_outliers_iqr(df, value_col, group_col)
    if method == 'zscore':
        return remove_outliers_zscore(df, value_col, group_col, threshold=z_threshold)
    if method == 'three-sigma':
        return remove_outliers_three_sigma(df, value_col, group_col)
    if method == 'grubbs':
        return remove_outliers_grubbs(df, value_col, group_col, alpha=alpha)
    if method == 'dixon':
        return remove_outliers_dixon(df, value_col, group_col, alpha=alpha)
    raise ValueError(f"Unsupported outlier removal method: {method}")


def detect_grubbs_outlier(series: pd.Series, alpha: float = 0.05) -> Dict[str, Optional[object]]:
    numeric = _numeric_series(series)
    n = len(numeric)
    if n < 3:
        return {'outlier_index': None, 'outlier_value': None, 'statistic': None, 'critical_value': None, 'rejected': False}
    mean_value = numeric.mean()
    std_value = numeric.std(ddof=1)
    deviations = np.abs(numeric - mean_value)
    outlier_index = int(deviations.idxmax())
    outlier_value = float(numeric.loc[outlier_index])
    g_stat = float(deviations.max() / std_value)
    t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    g_crit = float(((n - 1) / math.sqrt(n)) * math.sqrt(t_crit ** 2 / (n - 2 + t_crit ** 2)))
    return {
        'outlier_index': outlier_index,
        'outlier_value': outlier_value,
        'statistic': g_stat,
        'critical_value': g_crit,
        'rejected': g_stat > g_crit,
    }


_DIXON_CRITICAL_VALUES = {
    3: 0.941,
    4: 0.765,
    5: 0.642,
    6: 0.560,
    7: 0.507,
    8: 0.468,
    9: 0.437,
    10: 0.412,
    11: 0.392,
    12: 0.376,
    13: 0.361,
    14: 0.349,
    15: 0.338,
    16: 0.329,
    17: 0.320,
    18: 0.313,
    19: 0.305,
    20: 0.299,
    21: 0.294,
    22: 0.289,
    23: 0.284,
    24: 0.279,
    25: 0.276,
}


def detect_dixon_outlier(series: pd.Series) -> Dict[str, Optional[object]]:
    numeric = _numeric_series(series)
    n = len(numeric)
    if n < 3 or n > 25:
        return {'outlier_index': None, 'outlier_value': None, 'statistic': None, 'critical_value': None, 'rejected': False}
    sorted_values = numeric.sort_values()
    x1 = sorted_values.iloc[0]
    x2 = sorted_values.iloc[1]
    xn = sorted_values.iloc[-1]
    xn1 = sorted_values.iloc[-2]
    q_low = float((x2 - x1) / (xn - x1)) if xn != x1 else float('nan')
    q_high = float((xn - xn1) / (xn - x1)) if xn != x1 else float('nan')
    critical = _DIXON_CRITICAL_VALUES.get(n)
    if critical is None:
        return {'outlier_index': None, 'outlier_value': None, 'statistic': None, 'critical_value': None, 'rejected': False}
    if q_low > q_high:
        outlier_value = float(x1)
        outlier_index = int(sorted_values.index[0])
        statistic = q_low
    else:
        outlier_value = float(xn)
        outlier_index = int(sorted_values.index[-1])
        statistic = q_high
    return {
        'outlier_index': outlier_index,
        'outlier_value': outlier_value,
        'statistic': statistic,
        'critical_value': critical,
        'rejected': statistic > critical,
    }


def _following_ttest_ci(
    a: np.ndarray,
    b: np.ndarray,
    equal_var: bool,
    alpha: float,
) -> Tuple[float, float, float]:
    n1 = len(a)
    n2 = len(b)
    mean_diff = float(np.mean(a) - np.mean(b))
    var1 = np.var(a, ddof=1)
    var2 = np.var(b, ddof=1)
    if equal_var:
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        se = math.sqrt(pooled_var * (1 / n1 + 1 / n2))
        df = n1 + n2 - 2
    else:
        se = math.sqrt(var1 / n1 + var2 / n2)
        df = (var1 / n1 + var2 / n2) ** 2 / (
            (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
        )
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    lower = mean_diff - t_crit * se
    upper = mean_diff + t_crit * se
    return mean_diff, float(lower), float(upper)


def _paired_ttest_ci(a: np.ndarray, b: np.ndarray, alpha: float) -> Tuple[float, float, float]:
    diffs = a - b
    mean_diff = float(np.mean(diffs))
    sd_diff = float(np.std(diffs, ddof=1))
    n = len(diffs)
    if n < 2 or sd_diff == 0:
        return float(mean_diff), float('nan'), float('nan')
    se = sd_diff / math.sqrt(n)
    df = n - 1
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    lower = mean_diff - t_crit * se
    upper = mean_diff + t_crit * se
    return mean_diff, float(lower), float(upper)


def cohens_d(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    n1 = len(a)
    n2 = len(b)
    if n1 < 2 or n2 < 2:
        return None
    var1 = np.var(a, ddof=1)
    var2 = np.var(b, ddof=1)
    pooled_sd = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return None
    return float((np.mean(a) - np.mean(b)) / pooled_sd)


def hedges_g(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    d = cohens_d(a, b)
    if d is None:
        return None
    n1 = len(a)
    n2 = len(b)
    df = n1 + n2 - 2
    if df <= 0:
        return float(d)
    correction = 1 - 3 / (4 * df - 1)
    return float(d * correction)


def rank_biserial_correlation(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    if len(a) < 1 or len(b) < 1:
        return None
    try:
        u_stat = stats.mannwhitneyu(a, b, alternative='two-sided').statistic
    except Exception:
        return None
    return float(1 - 2 * u_stat / (len(a) * len(b)))


def _effect_size_label(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    mag = abs(value)
    if mag < 0.2:
        return 'Very Small'
    if mag < 0.5:
        return 'Small'
    if mag < 0.8:
        return 'Medium'
    return 'Large'


def _anova_effect_sizes(groups: Dict[str, np.ndarray]) -> Dict[str, Optional[float]]:
    all_values = np.concatenate(list(groups.values()))
    grand_mean = np.mean(all_values)
    ss_between = sum(len(values) * (np.mean(values) - grand_mean) ** 2 for values in groups.values())
    ss_within = sum(((values - np.mean(values)) ** 2).sum() for values in groups.values())
    df_between = len(groups) - 1
    df_within = len(all_values) - len(groups)
    mse = ss_within / df_within if df_within > 0 else float('nan')
    eta_sq = float(ss_between / (ss_between + ss_within)) if ss_between + ss_within > 0 else None
    omega_sq = (
        float((ss_between - df_between * mse) / (ss_between + ss_within + mse))
        if df_within > 0 and ss_between + ss_within + mse > 0
        else None
    )
    return {'eta_squared': eta_sq, 'omega_squared': omega_sq}


def _dunn_posthoc(df: pd.DataFrame, value_col: str, group_col: str, alpha: float, correction: str) -> List[Dict[str, object]]:
    df = df[[value_col, group_col]].dropna()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()
    groups = df.groupby(group_col, observed=True)
    ranked = stats.rankdata(df[value_col])
    df = df.assign(rank=ranked)
    n = len(df)
    group_ranks = df.groupby(group_col, observed=True)['rank'].mean().to_dict()
    group_counts = df[group_col].value_counts().to_dict()
    comparisons: List[Dict[str, object]] = []
    labels = list(group_ranks.keys())
    z_values: List[float] = []
    raw_pvalues: List[float] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            g1 = labels[i]
            g2 = labels[j]
            r1 = group_ranks[g1]
            r2 = group_ranks[g2]
            n1 = group_counts[g1]
            n2 = group_counts[g2]
            se = math.sqrt((n * (n + 1) / 12) * (1 / n1 + 1 / n2))
            if se == 0:
                z = 0.0
            else:
                z = (r1 - r2) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
            comparisons.append({
                'groups': f"{g1} vs {g2}",
                'test': 'Dunn',
                'mean_diff': float(r1 - r2),
                'pvalue': float(p_value),
                'z': float(z),
            })
            raw_pvalues.append(p_value)
    if raw_pvalues:
        method = correction if correction != 'fdr' else 'fdr_bh'
        _, p_adj, _, _ = smm.multipletests(raw_pvalues, alpha=alpha, method=method)
        for idx, row in enumerate(comparisons):
            row['pvalue_corrected'] = float(p_adj[idx])
            row['decision'] = (
                'Fail to Reject H0' if p_adj[idx] >= alpha else 'Reject H0'
            )
    return comparisons


def _tukey_posthoc(df: pd.DataFrame, value_col: str, group_col: str, alpha: float) -> List[Dict[str, object]]:
    df = df[[value_col, group_col]].dropna()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()
    try:
        tukey = pairwise_tukeyhsd(endog=df[value_col], groups=df[group_col], alpha=alpha)
        table = tukey.summary().data[1:]
    except Exception:
        return []
    results: List[Dict[str, object]] = []
    for row in table:
        g1, g2, meandiff, p_adj, lower, upper, reject = row
        results.append({
            'groups': f"{g1} vs {g2}",
            'test': 'Tukey HSD',
            'mean_diff': float(meandiff),
            'pvalue': float(p_adj),
            'pvalue_corrected': float(p_adj),
            'lower_ci': float(lower),
            'upper_ci': float(upper),
            'decision': 'Fail to Reject H0' if p_adj >= alpha else 'Reject H0',
            'significant': bool(reject),
        })
    return results


def _format_decision(pvalue: float, alpha: float) -> Tuple[str, str]:
    if pvalue >= alpha:
        return (
            'Fail to Reject H0',
            'P-value is greater than or equal to alpha. Therefore, there is insufficient evidence to reject the null hypothesis.',
        )
    return (
        'Reject H0',
        'P-value is less than alpha. Therefore, there is sufficient evidence to reject the null hypothesis.',
    )


def analyze_groups(
    df: pd.DataFrame,
    value_col: str,
    group_col: str,
    alpha: float = 0.05,
    p_correction: Optional[str] = None,
    paired: bool = False,
) -> Dict[str, object]:
    """Analyze groups with assumptions, main test, post-hoc, effect size, and interpretation."""
    if value_col not in df.columns or group_col not in df.columns:
        raise ValueError('Selected value or group column is not present in the DataFrame.')

    df = df[[value_col, group_col]].copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna(subset=[value_col, group_col])
    if df.empty:
        raise ValueError('No valid numeric observations found after cleaning the selected columns.')

    groups = {g: grp[value_col].astype(float).to_numpy() for g, grp in df.groupby(group_col, observed=True)}
    descriptive = {g: _describe_series(pd.Series(values)) for g, values in groups.items()}
    normality: Dict[str, Optional[float]] = {}
    for g, values in groups.items():
        if len(values) < 3 or len(values) > 5000:
            normality[g] = None
            continue
        try:
            pvalue = float(stats.shapiro(values)[1])
            normality[g] = pvalue
        except Exception:
            normality[g] = None

    levene_p: Optional[float]
    if len(groups) > 1:
        try:
            levene_p = float(stats.levene(*groups.values())[1])
        except Exception:
            levene_p = None
    else:
        levene_p = None

    result: Dict[str, object] = {
        'descriptive': descriptive,
        'assumptions': {
            'normality': normality,
            'levene_p': levene_p,
            'alpha': alpha,
        },
    }

    if len(groups) == 1:
        result['main_test'] = {
            'test': 'No comparison',
            'pvalue': None,
            'decision': 'Fail to Reject H0',
            'interpretation': 'Only one group is available for analysis. No group comparison was performed.',
        }
        result['interpretation'] = 'Only one group present; no inferential test applied.'
        return result

    if len(groups) == 2:
        names = list(groups.keys())
        a = groups[names[0]]
        b = groups[names[1]]
        if paired:
            if len(a) != len(b):
                raise ValueError('Paired t-test requires equal sample sizes for both groups.')
            diffs = a - b
            test_name = 'paired t-test'
            all_normal_diffs = len(diffs) >= 3 and float(stats.shapiro(diffs)[1]) >= alpha
            if all_normal_diffs:
                try:
                    tstat, pvalue = stats.ttest_rel(a, b)
                except Exception:
                    pvalue = 1.0
            else:
                try:
                    tstat, pvalue = stats.wilcoxon(a, b)
                    test_name = 'Wilcoxon signed-rank'
                except Exception:
                    pvalue = 1.0
            mean_diff, lower_ci, upper_ci = _paired_ttest_ci(a, b, alpha)
            effect = {
                'paired_cohens_d': _safe_float(np.mean(diffs) / np.std(diffs, ddof=1)) if len(diffs) > 1 else None,
                'effect_size_label': _effect_size_label(_safe_float(np.mean(diffs) / np.std(diffs, ddof=1)) if len(diffs) > 1 else None),
            }
            ci = {'mean_diff': float(mean_diff), 'lower_ci': lower_ci, 'upper_ci': upper_ci}
            decision, interpretation = _format_decision(float(pvalue), alpha)
            result['main_test'] = {
                'test': test_name,
                'pvalue': float(pvalue),
                'decision': decision,
                'interpretation': interpretation,
                'paired': True,
                'confidence_interval': ci,
                'effect_size': effect,
            }
            result['posthoc'] = []
            result['interpretation'] = generate_interpretation(result)
            return result

        equal_var = levene_p is not None and levene_p >= alpha
        if normality.get(names[0], 0) is not None and normality.get(names[1], 0) is not None:
            test_name = 't-test' if equal_var else 'Welch t-test'
            try:
                tstat, pvalue = stats.ttest_ind(a, b, equal_var=equal_var)
            except Exception:
                pvalue = 1.0
            mean_diff, lower_ci, upper_ci = _following_ttest_ci(a, b, equal_var, alpha)
            effect = {
                'cohens_d': _safe_float(cohens_d(a, b)),
                'hedges_g': _safe_float(hedges_g(a, b)),
                'effect_size_label': _effect_size_label(_safe_float(cohens_d(a, b))),
            }
            ci = {'mean_diff': float(mean_diff), 'lower_ci': lower_ci, 'upper_ci': upper_ci}
        else:
            test_name = 'Mann-Whitney U'
            try:
                u_stat, pvalue = stats.mannwhitneyu(a, b, alternative='two-sided')
            except Exception:
                pvalue = 1.0
            ci = {'mean_diff': None, 'lower_ci': None, 'upper_ci': None}
            effect = {
                'rank_biserial': _safe_float(rank_biserial_correlation(a, b)),
                'effect_size_label': _effect_size_label(_safe_float(rank_biserial_correlation(a, b))),
            }
        decision, interpretation = _format_decision(float(pvalue), alpha)
        result['main_test'] = {
            'test': test_name,
            'pvalue': float(pvalue),
            'decision': decision,
            'interpretation': interpretation,
            'equal_variance': equal_var,
            'confidence_interval': ci,
            'effect_size': effect,
        }
        result['posthoc'] = []
        result['interpretation'] = generate_interpretation(result)
        return result

    all_normal = all(value is not None and value >= alpha for value in normality.values())
    equal_var = levene_p is not None and levene_p >= alpha
    if all_normal and equal_var:
        group_arrays = list(groups.values())
        try:
            fstat, pvalue = stats.f_oneway(*group_arrays)
        except Exception:
            pvalue = 1.0
        test_name = 'ANOVA'
        effect = _anova_effect_sizes(groups)
        posthoc = _tukey_posthoc(df, value_col, group_col, alpha)
    else:
        try:
            hstat, pvalue = stats.kruskal(*groups.values())
        except Exception:
            pvalue = 1.0
        test_name = 'Kruskal-Wallis'
        effect = {'eta_squared': None, 'omega_squared': None}
        correction = p_correction or 'bonferroni'
        correction = 'fdr_bh' if correction == 'fdr_bh' else correction
        posthoc = _dunn_posthoc(df, value_col, group_col, alpha, correction)

    decision, interpretation = _format_decision(float(pvalue), alpha)
    result['main_test'] = {
        'test': test_name,
        'pvalue': float(pvalue),
        'decision': decision,
        'interpretation': interpretation,
        'equal_variance': equal_var,
        'effect_size': {
            'eta_squared': effect.get('eta_squared'),
            'omega_squared': effect.get('omega_squared'),
            'interpretation': _effect_size_label(effect.get('eta_squared')) if effect.get('eta_squared') is not None else None,
        },
    }
    result['posthoc'] = posthoc
    result['interpretation'] = generate_interpretation(result)
    return result


def _safe_float(value: Optional[float]) -> Optional[float]:
    return float(value) if value is not None and not isinstance(value, str) else None
