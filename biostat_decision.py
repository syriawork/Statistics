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
from pharma_tools import calculate_process_capability
from stats_analysis.analysis import analyze_groups, remove_outliers
from visualization.plots import generate_all_plots


def parse_args():
    p = argparse.ArgumentParser(description="Biostat decision tool")
    p.add_argument("--data", required=True, help="CSV file with data")
    p.add_argument("--value", required=True, help="Column name for numeric values")
    p.add_argument("--group", required=True, help="Column name for group labels")
    p.add_argument("--alpha", type=float, default=0.05, help="Significance level (default 0.05)")
    p.add_argument(
        "--outlier-method",
        choices=['none', 'iqr', 'zscore', 'three-sigma', 'grubbs', 'dixon'],
        default='none',
        help="Outlier removal method to apply before analysis",
    )
    p.add_argument("--zscore-threshold", type=float, default=3.0, help="Z-score threshold for zscore outlier removal")
    p.add_argument("--usl", type=float, default=None, help="Upper specification limit for Cp/CpK")
    p.add_argument("--lsl", type=float, default=None, help="Lower specification limit for Cp/CpK")
    p.add_argument("--paired", action="store_true", help="Use paired t-test / Wilcoxon for two-group analysis")
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

    outlier_summary = None
    if args.outlier_method != 'none':
        df, out_summary = remove_outliers(
            df,
            args.value,
            args.group,
            method=args.outlier_method,
            z_threshold=args.zscore_threshold,
            alpha=args.alpha,
        )
        outlier_summary = out_summary
        print(f"Outlier removal method: {args.outlier_method}")
        if not out_summary.empty:
            print("Outlier removal summary:")
            print(out_summary.to_string(index=False))

    p_corr = None if args.p_correction == 'none' else args.p_correction
    result = analyze_groups(
        df,
        args.value,
        args.group,
        alpha=args.alpha,
        p_correction=p_corr,
        paired=args.paired,
    )
    if outlier_summary is not None and not outlier_summary.empty:
        result['outlier_summary'] = outlier_summary.to_dict(orient='records')
        result['outlier_method'] = args.outlier_method

    if args.usl is not None and args.lsl is not None:
        if args.usl > args.lsl:
            capability = calculate_process_capability(df[args.value].astype(float).dropna(), args.usl, args.lsl)
            result['capability'] = capability
            print(f"Cp/CpK computed with USL={args.usl} and LSL={args.lsl}")
        else:
            print('Warning: USL must be greater than LSL to compute Cp/CpK.')

    print("\nTest summary:")
    print(result.get('main_test', {}))
    if result.get('posthoc'):
        print("Pairwise tests:")
        for r in result['posthoc']:
            pvalue = r.get('pvalue')
            p_str = f"{pvalue:.4g}" if pvalue is not None else 'None'
            print(f"  {r['groups']}: {r['test']} p={p_str} => {r.get('decision')}")

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
