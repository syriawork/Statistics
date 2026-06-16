from __future__ import annotations

import pandas as pd
from pandas import ExcelWriter


def _auto_adjust_column_width(writer: ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df.columns):
        max_len = max(
            df[col].astype(str).map(len).max() if not df[col].empty else 0,
            len(col),
        ) + 2
        worksheet.set_column(idx, idx, max_len)


def _format_pvalues(writer: ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    fmt = workbook.add_format({'num_format': '0.0000'})
    red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    for idx, col in enumerate(df.columns):
        if 'pvalue' in col.lower() or 'p_value' in col.lower():
            worksheet.set_column(idx, idx, 12, fmt)
            worksheet.conditional_format(1, idx, len(df), idx, {
                'type': 'cell',
                'criteria': '<',
                'value': 0.05,
                'format': red,
            })
            worksheet.conditional_format(1, idx, len(df), idx, {
                'type': 'cell',
                'criteria': '>=',
                'value': 0.05,
                'format': green,
            })


def generate_excel_report(result: dict, df: pd.DataFrame, out_path: str) -> None:
    """Generate a formatted Excel report with multiple sheets."""
    with pd.ExcelWriter(out_path, engine='xlsxwriter') as writer:
        descriptive = pd.DataFrame(
            [
                {'group': group, **values}
                for group, values in result.get('descriptive', {}).items()
            ]
        )
        descriptive.to_excel(writer, sheet_name='Descriptive Statistics', index=False)
        _auto_adjust_column_width(writer, 'Descriptive Statistics', descriptive)

        assumptions = pd.DataFrame([
            {
                'assumption': 'Shapiro-Wilk normality',
                **{
                    f'{group} pvalue': pvalue
                    for group, pvalue in result.get('assumptions', {}).get('normality', {}).items()
                },
                'levene_p': result.get('assumptions', {}).get('levene_p'),
                'alpha': result.get('assumptions', {}).get('alpha'),
            }
        ])
        assumptions.to_excel(writer, sheet_name='Assumption Tests', index=False)
        _auto_adjust_column_width(writer, 'Assumption Tests', assumptions)
        _format_pvalues(writer, 'Assumption Tests', assumptions)

        main_test = result.get('main_test', {})
        main_df = pd.DataFrame([main_test])
        main_df.to_excel(writer, sheet_name='Main Test', index=False)
        _auto_adjust_column_width(writer, 'Main Test', main_df)
        _format_pvalues(writer, 'Main Test', main_df)

        if result.get('posthoc'):
            posthoc = pd.DataFrame(result['posthoc'])
            posthoc.to_excel(writer, sheet_name='Post-Hoc Results', index=False)
            _auto_adjust_column_width(writer, 'Post-Hoc Results', posthoc)
            _format_pvalues(writer, 'Post-Hoc Results', posthoc)

        summary = pd.DataFrame([
            {
                'study_information': 'Biostat Decision Tool report',
                'groups': len(result.get('descriptive', {})),
                'observations': int(sum(values.get('n', 0) for values in result.get('descriptive', {}).values())),
                'main_test': main_test.get('test'),
                'decision': main_test.get('decision'),
            }
        ])
        summary.to_excel(writer, sheet_name='Summary', index=False)
        _auto_adjust_column_width(writer, 'Summary', summary)

        df.to_excel(writer, sheet_name='Raw Data', index=False)
        _auto_adjust_column_width(writer, 'Raw Data', df)

        graphs = pd.DataFrame([{'note': 'Graphs are available in the PDF or separate PNG exports.'}])
        graphs.to_excel(writer, sheet_name='Graphs', index=False)
        _auto_adjust_column_width(writer, 'Graphs', graphs)
