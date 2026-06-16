from __future__ import annotations

import os
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

sns.set_theme(style='whitegrid')


def _save_figure(fig, path: str) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def generate_all_plots(df: pd.DataFrame, value_col: str, group_col: str, output_dir: str) -> Dict[str, str]:
    """Generate box plot, violin plot, histogram, and Q-Q plots and save them to PNG files."""
    os.makedirs(output_dir, exist_ok=True)
    df = df[[value_col, group_col]].dropna().copy()
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
    df = df.dropna()

    paths: Dict[str, str] = {}

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x=group_col, y=value_col, data=df, ax=ax)
    ax.set_title('Box Plot by Group')
    box_path = os.path.join(output_dir, 'box_plot.png')
    _save_figure(fig, box_path)
    paths['Box plot'] = box_path

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(x=group_col, y=value_col, data=df, inner='quartile', ax=ax)
    ax.set_title('Violin Plot by Group')
    violin_path = os.path.join(output_dir, 'violin_plot.png')
    _save_figure(fig, violin_path)
    paths['Violin plot'] = violin_path

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df, x=value_col, hue=group_col, kde=True, element='step', stat='density', palette='tab10', ax=ax)
    ax.set_title('Histogram by Group')
    hist_path = os.path.join(output_dir, 'histogram.png')
    _save_figure(fig, hist_path)
    paths['Histogram'] = hist_path

    fig, axs = plt.subplots(1, len(df[group_col].unique()), figsize=(len(df[group_col].unique()) * 4, 4))
    if len(df[group_col].unique()) == 1:
        axs = [axs]
    for idx, (group, group_df) in enumerate(df.groupby(group_col, observed=True)):
        ax = axs[idx]
        stats.probplot(group_df[value_col], dist='norm', plot=ax)
        ax.set_title(f'Q-Q plot: {group}')
    qq_path = os.path.join(output_dir, 'qq_plots.png')
    _save_figure(fig, qq_path)
    paths['Q-Q plots'] = qq_path

    return paths
