import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_excel_report(result, df, out_path):
    with pd.ExcelWriter(out_path, engine='xlsxwriter') as writer:
        # groups summary
        groups = result.get('groups', {})
        gdf = pd.DataFrame([{ 'group': k, **v } for k, v in groups.items()])
        gdf.to_excel(writer, sheet_name='Groups', index=False)

        # main test
        main = {k: v for k, v in result.items() if k not in ('groups', 'pairwise')}
        pd.DataFrame([main]).to_excel(writer, sheet_name='Summary', index=False)

        # pairwise
        pairwise = result.get('pairwise', [])
        if pairwise:
            pd.DataFrame(pairwise).to_excel(writer, sheet_name='Pairwise', index=False)

        # raw data (first sheet)
        df.to_excel(writer, sheet_name='Data', index=False)


def generate_pdf_report(result, out_path):
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    y = height - 40
    c.setFont('Helvetica-Bold', 14)
    c.drawString(40, y, 'Biostatistical Analysis Report')
    y -= 30
    c.setFont('Helvetica', 10)
    # summary
    main_items = {k: v for k, v in result.items() if k not in ('groups', 'pairwise')}
    for k, v in main_items.items():
        line = f"{k}: {v}"
        c.drawString(40, y, line)
        y -= 14
        if y < 60:
            c.showPage()
            y = height - 40
    y -= 6
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, 'Pairwise tests:')
    y -= 18
    c.setFont('Helvetica', 10)
    for p in result.get('pairwise', []):
        line = f"{p.get('groups')} | {p.get('test')} | p={p.get('pvalue'):.4g}"
        if 'pvalue_corrected' in p:
            line += f" | p_corr={p.get('pvalue_corrected'):.4g} | {p.get('decision')}"
        else:
            line += f" | {p.get('decision')}"
        c.drawString(40, y, line)
        y -= 12
        if y < 60:
            c.showPage()
            y = height - 40
    c.save()
