#!/usr/bin/env python3
"""
Biostatistical decision tool for pharmaceutical QC.
Usage: python biostat_decision.py --data data/example.csv --value Value --group Group
"""
import argparse
import os

import pandas as pd
from reports.excel import generate_excel_report
from reports.pdf import generate_pdf_report
from stats_analysis.analysis import analyze_groups, remove_outliers_iqr
from visualization.plots import generate_all_plots


def parse_args():
    p = argparse.ArgumentParser(description="Biostat decision tool")
    p.add_argument("--data", required=True, help="CSV file with data")
    p.add_argument("--value", required=True, help="Column name for numeric values")
    p.add_argument("--group", required=True, help="Column name for group labels")
    p.add_argument("--alpha", type=float, default=0.05, help="Significance level (default 0.05)")
    p.add_argument("--remove-outliers", action="store_true", help="Remove outliers by IQR per group")
    p.add_argument("--out-report", default="report.csv", help="CSV file to write test report")
    p.add_argument(
        "--p-correction",
        choices=['none', 'bonferroni', 'holm', 'fdr_bh'],
        default='none',
        help="Multiple comparisons correction",
    )
    p.add_argument("--export-excel", default=None, help="Path to write Excel report")
    p.add_argument("--export-pdf", default=None, help="Path to write PDF report")
    p.add_argument("--export-graphs-dir", default=None, help="Directory to save graph PNG files")
    return p.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.data)

    if args.remove_outliers:
        df, out_summary = remove_outliers_iqr(df, args.value, args.group)
        print("Outlier removal summary:")
        print(out_summary.to_string(index=False))

    p_corr = None if args.p_correction == 'none' else args.p_correction
    result = analyze_groups(df, args.value, args.group, alpha=args.alpha, p_correction=p_corr)

    print("\nTest summary:")
    print(result.get('main_test', {}))
    if result.get('posthoc'):
        print("Pairwise tests:")
        for r in result['posthoc']:
            print(f"  {r['groups']}: {r['test']} p={r.get('pvalue'):.4g} => {r.get('decision')}")

    rows = []
    for r in result.get('posthoc', []):
        row = {
            'groups': r['groups'],
            'test': r.get('test'),
            'pvalue': r.get('pvalue'),
            'pvalue_corrected': r.get('pvalue_corrected'),
            'decision': r.get('decision'),
        }
        rows.append(row)
    if rows:
        pd.DataFrame(rows).to_csv(args.out_report, index=False)
        print(f"CSV report saved to {args.out_report}")

    if args.export_graphs_dir:
        os.makedirs(args.export_graphs_dir, exist_ok=True)
        generate_all_plots(df, args.value, args.group, args.export_graphs_dir)
        print(f"Graphs saved to {args.export_graphs_dir}")

    if args.export_excel:
        generate_excel_report(result, df, args.export_excel)
        print(f"Excel report saved to {args.export_excel}")
    if args.export_pdf:
        plot_paths = None
        if args.export_graphs_dir:
            plot_paths = [os.path.join(args.export_graphs_dir, fname) for fname in os.listdir(args.export_graphs_dir) if fname.endswith('.png')]
        generate_pdf_report(result, args.export_pdf, plot_paths=plot_paths)
        print(f"PDF report saved to {args.export_pdf}")


if __name__ == '__main__':
    main()
