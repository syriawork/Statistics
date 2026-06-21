from __future__ import annotations

import pandas as pd
from pandas import ExcelWriter
from utilities.translations import translate_dataframe_columns, translate_option, translate_decision


def _auto_adjust_column_width(writer: ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df.columns):
        values = [str(x) for x in df[col].dropna().tolist() if x is not None]
        if values:
            max_len = max([len(v) for v in values] + [len(str(col))]) + 2
        else:
            max_len = len(str(col)) + 2
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


def generate_excel_report(result: dict, df: pd.DataFrame, out_path: str, lang: str = 'en') -> None:
    """Generate a formatted Excel report with multiple sheets."""
    with pd.ExcelWriter(out_path, engine='xlsxwriter') as writer:
        descriptive = pd.DataFrame(
            [
                {'group': group, **values}
                for group, values in result.get('descriptive', {}).items()
            ]
        )
        descriptive = translate_dataframe_columns(descriptive, lang)
        sheet_name = 'Descriptive Statistics'
        descriptive.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, descriptive)

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
        assumptions = translate_dataframe_columns(assumptions, lang)
        sheet_name = 'Assumption Tests'
        assumptions.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, assumptions)
        _format_pvalues(writer, sheet_name, assumptions)

        main_test = result.get('main_test', {})
        main_df = pd.DataFrame([main_test])
        main_df = translate_dataframe_columns(main_df, lang)
        sheet_name = 'Main Test'
        main_df.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, main_df)
        _format_pvalues(writer, sheet_name, main_df)

        if result.get('posthoc'):
            posthoc = pd.DataFrame(result['posthoc'])
            posthoc = translate_dataframe_columns(posthoc, lang)
            sheet_name = 'Post-Hoc Results'
            posthoc.to_excel(writer, sheet_name=sheet_name, index=False)
            _auto_adjust_column_width(writer, sheet_name, posthoc)
            _format_pvalues(writer, sheet_name, posthoc)

        summary = pd.DataFrame([
            {
                'study_information': 'Biostat Decision Tool report',
                'groups': len(result.get('descriptive', {})),
                'observations': int(sum(values.get('n', 0) for values in result.get('descriptive', {}).values())),
                'main_test': main_test.get('test'),
                'decision': main_test.get('decision'),
                'outlier_method': result.get('outlier_method'),
            }
        ])
        summary = translate_dataframe_columns(summary, lang)
        sheet_name = 'Summary'
        summary.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, summary)

        if result.get('outlier_summary'):
            outlier_df = pd.DataFrame(result['outlier_summary'])
            outlier_df = translate_dataframe_columns(outlier_df, lang)
            sheet_name = 'Outlier Summary'
            outlier_df.to_excel(writer, sheet_name=sheet_name, index=False)
            _auto_adjust_column_width(writer, sheet_name, outlier_df)

        if result.get('capability'):
            capability_df = pd.DataFrame([result['capability']])
            capability_df = translate_dataframe_columns(capability_df, lang)
            sheet_name = 'Process Capability'
            capability_df.to_excel(writer, sheet_name=sheet_name, index=False)
            _auto_adjust_column_width(writer, sheet_name, capability_df)

        raw_df = df.copy()
        raw_df = translate_dataframe_columns(raw_df, lang)
        sheet_name = 'Raw Data'
        raw_df.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, raw_df)

        graphs = pd.DataFrame([{'note': 'Graphs are available in the PDF or separate PNG exports.'}])
        graphs = translate_dataframe_columns(graphs, lang)
        sheet_name = 'Graphs'
        graphs.to_excel(writer, sheet_name=sheet_name, index=False)
        _auto_adjust_column_width(writer, sheet_name, graphs)
