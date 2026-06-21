from __future__ import annotations

from typing import Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from utilities.translations import translate, translate_test_name, translate_decision


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


def generate_pdf_report(result: dict, out_path: str, plot_paths: Optional[List[str]] = None, lang: str = 'en') -> None:
    """Generate a styled PDF report with tables and optional graphs."""
    doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    body_style = styles['BodyText']
    heading_style = styles['Heading2']
    title_style = styles['Title']

    story = []

    header = Paragraph(translate('Biostatistical Analysis Report', lang), title_style)
    story.append(header)
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('1. Study Information', lang), heading_style))
    story.append(Paragraph(translate('Biostat Decision Tool automated report for pharmaceutical R&D.', lang), body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('2. Descriptive Statistics', lang), heading_style))
    descriptive = result.get('descriptive', {})
    if descriptive:
        headers = [
            translate('Group', lang),
            translate('N', lang),
            translate('Mean', lang),
            translate('Median', lang),
            translate('Std', lang),
            translate('SEM', lang),
            translate('Min', lang),
            translate('Max', lang),
            translate('CV%', lang),
            translate('Q1', lang),
            translate('Q3', lang),
            translate('IQR', lang),
        ]
        data = [headers]
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

    story.append(Paragraph(translate('3. Assumption Checks', lang), heading_style))
    assumptions = result.get('assumptions', {})
    normality = assumptions.get('normality', {})
    for group, pvalue in normality.items():
        story.append(Paragraph(f'{group}: {translate("Shapiro-Wilk normality", lang)} p = {_safe_str(pvalue)}', body_style))
    story.append(Paragraph(translate("Levene's test p = {_value}", lang).format(_value=_safe_str(assumptions.get('levene_p'))), body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('4. Main Statistical Test', lang), heading_style))
    main_test = result.get('main_test', {})
    story.append(Paragraph(f"{translate('Test', lang)}: {_safe_str(translate_test_name(str(main_test.get('test')), lang))}", body_style))
    story.append(Paragraph(f"{translate('p-value', lang)}: {_safe_str(main_test.get('pvalue'))}", body_style))
    story.append(Paragraph(f"{translate('Decision', lang)}: {_safe_str(translate_decision(str(main_test.get('decision')), lang))}", body_style))
    story.append(Paragraph(f"{translate('Interpretation', lang)}: {_safe_str(main_test.get('interpretation'))}", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('5. Effect Size', lang), heading_style))
    effect = main_test.get('effect_size', {})
    for label, value in effect.items():
        story.append(Paragraph(f"{translate(label.replace('_', ' ').title(), lang)}: {_safe_str(value)}", body_style))
    story.append(Spacer(1, 12))

    if result.get('outlier_summary'):
        story.append(Paragraph(translate('6. Outlier Summary', lang), heading_style))
        headers = [
            translate('Group', lang),
            translate('N Before', lang),
            translate('N After', lang),
            translate('Removed', lang),
            translate('Last Outlier Value', lang),
            translate('Statistic', lang),
            translate('Critical', lang),
            translate('Rejected', lang),
        ]
        data = [headers]
        for row in result['outlier_summary']:
            data.append([
                _safe_str(row.get('group')),
                _safe_str(row.get('n_before')),
                _safe_str(row.get('n_after')),
                _safe_str(row.get('removed')),
                _safe_str(row.get('last_outlier_value')),
                _safe_str(row.get('last_statistic')),
                _safe_str(row.get('last_critical_value')),
                _safe_str(row.get('last_rejected')),
            ])
        story.append(_build_table(data, [3 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2 * cm, 2 * cm, 1.5 * cm]))
        story.append(Spacer(1, 12))

    if result.get('capability'):
        story.append(Paragraph(translate('7. Process Capability', lang), heading_style))
        capability = result['capability']
        for label, value in capability.items():
            story.append(Paragraph(f"{translate(str(label).replace('_', ' ').title(), lang)}: {_safe_str(value)}", body_style))
        story.append(Spacer(1, 12))

    story.append(Paragraph(translate('8. Confidence Intervals', lang), heading_style))
    ci = main_test.get('confidence_interval', {})
    story.append(Paragraph(f"{translate('Mean difference', lang)}: {_safe_str(ci.get('mean_diff'))}", body_style))
    story.append(Paragraph(f"{translate('95% CI:', lang)} {_safe_str(ci.get('lower_ci'))} {translate('to', lang)} {_safe_str(ci.get('upper_ci'))}", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('7. Pairwise Comparisons', lang), heading_style))
    posthoc = result.get('posthoc', [])
    if posthoc:
        headers = [
            translate('Comparison', lang),
            translate('Test', lang),
            translate('Mean Diff', lang),
            translate('p-value', lang),
            translate('p-adj', lang),
            translate('Decision', lang),
        ]
        data = [headers]
        for row in posthoc:
            data.append([
                _safe_str(row.get('groups')),
                _safe_str(translate_test_name(str(row.get('test')), lang)),
                _safe_str(row.get('mean_diff')),
                _safe_str(row.get('pvalue')),
                _safe_str(row.get('pvalue_corrected')),
                _safe_str(translate_decision(str(row.get('decision')), lang)),
            ])
        story.append(_build_table(data, [5 * cm, 3 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm]))
    else:
        story.append(Paragraph(translate('No pairwise comparisons were performed.', lang), body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('8. Interpretation', lang), heading_style))
    story.append(Paragraph(_safe_str(result.get('interpretation')), body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph(translate('9. Graphs', lang), heading_style))
    if plot_paths:
        for path in plot_paths:
            try:
                story.append(Image(path, width=16 * cm, height=10 * cm))
                story.append(Spacer(1, 12))
            except Exception:
                story.append(Paragraph(f"{translate('Unable to render graph:', lang)} {path}", body_style))
    else:
        story.append(Paragraph(translate('Graph images were not provided for PDF embedding.', lang), body_style))

    doc.build(story)
