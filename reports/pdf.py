from __future__ import annotations

from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _build_table(data: List[List[str]], column_widths: List[float]) -> Table:
    table = Table(data, colWidths=column_widths, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    table.setStyle(style)
    return table


def _safe_str(value: Optional[object]) -> str:
    if value is None:
        return ''
    return str(value)


def generate_pdf_report(result: dict, out_path: str, plot_paths: Optional[List[str]] = None) -> None:
    """Generate a styled PDF report with tables and optional graphs."""
    doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    story = []

    header = Paragraph('Biostatistical Analysis Report', styles['Title'])
    story.append(header)
    story.append(Spacer(1, 12))

    story.append(Paragraph('1. Study Information', styles['Heading2']))
    story.append(Paragraph('Biostat Decision Tool automated report for pharmaceutical R&D.', styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('2. Descriptive Statistics', styles['Heading2']))
    descriptive = result.get('descriptive', {})
    if descriptive:
        data = [['Group', 'N', 'Mean', 'Median', 'Std', 'SEM', 'Min', 'Max', 'CV%', 'Q1', 'Q3', 'IQR']]
        for group, stats_row in descriptive.items():
            data.append([
                _safe_str(group),
                _safe_str(stats_row.get('n')),
                _safe_str(stats_row.get('mean')),
                _safe_str(stats_row.get('median')),
                _safe_str(stats_row.get('std')),
                _safe_str(stats_row.get('sem')),
                _safe_str(stats_row.get('min')),
                _safe_str(stats_row.get('max')),
                _safe_str(stats_row.get('cv_pct')),
                _safe_str(stats_row.get('q1')),
                _safe_str(stats_row.get('q3')),
                _safe_str(stats_row.get('iqr')),
            ])
        story.append(_build_table(data, [3 * cm, 1.3 * cm, 2 * cm, 2 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm]))
    story.append(Spacer(1, 12))

    story.append(Paragraph('3. Assumption Checks', styles['Heading2']))
    assumptions = result.get('assumptions', {})
    normality = assumptions.get('normality', {})
    for group, pvalue in normality.items():
        story.append(Paragraph(f'{group}: Shapiro-Wilk p = {_safe_str(pvalue)}', styles['BodyText']))
    story.append(Paragraph(f"Levene's test p = {_safe_str(assumptions.get('levene_p'))}", styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('4. Main Statistical Test', styles['Heading2']))
    main_test = result.get('main_test', {})
    story.append(Paragraph(f"Test: {_safe_str(main_test.get('test'))}", styles['BodyText']))
    story.append(Paragraph(f"P-value: {_safe_str(main_test.get('pvalue'))}", styles['BodyText']))
    story.append(Paragraph(f"Decision: {_safe_str(main_test.get('decision'))}", styles['BodyText']))
    story.append(Paragraph(f"Interpretation: {_safe_str(main_test.get('interpretation'))}", styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('5. Effect Size', styles['Heading2']))
    effect = main_test.get('effect_size', {})
    for label, value in effect.items():
        story.append(Paragraph(f"{label.replace('_', ' ').title()}: {_safe_str(value)}", styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('6. Confidence Intervals', styles['Heading2']))
    ci = main_test.get('confidence_interval', {})
    story.append(Paragraph(f"Mean difference: {_safe_str(ci.get('mean_diff'))}", styles['BodyText']))
    story.append(Paragraph(f"95% CI: {_safe_str(ci.get('lower_ci'))} to {_safe_str(ci.get('upper_ci'))}", styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('7. Pairwise Comparisons', styles['Heading2']))
    posthoc = result.get('posthoc', [])
    if posthoc:
        data = [['Comparison', 'Test', 'Mean Diff', 'p-value', 'p-adj', 'Decision']]
        for row in posthoc:
            data.append([
                _safe_str(row.get('groups')),
                _safe_str(row.get('test')),
                _safe_str(row.get('mean_diff')),
                _safe_str(row.get('pvalue')),
                _safe_str(row.get('pvalue_corrected')),
                _safe_str(row.get('decision')),
            ])
        story.append(_build_table(data, [5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm]))
    else:
        story.append(Paragraph('No pairwise comparisons were performed.', styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('8. Interpretation', styles['Heading2']))
    story.append(Paragraph(_safe_str(result.get('interpretation')), styles['BodyText']))
    story.append(Spacer(1, 12))

    story.append(Paragraph('9. Graphs', styles['Heading2']))
    if plot_paths:
        for path in plot_paths:
            try:
                story.append(Image(path, width=16 * cm, height=10 * cm))
                story.append(Spacer(1, 12))
            except Exception:
                story.append(Paragraph(f'Unable to render graph: {path}', styles['BodyText']))
    else:
        story.append(Paragraph('Graph images were not provided for PDF embedding.', styles['BodyText']))

    doc.build(story)
