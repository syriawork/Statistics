import os
import tempfile

import pandas as pd
import streamlit as st
from reports.excel import generate_excel_report
from reports.pdf import generate_pdf_report
from stats_analysis.analysis import analyze_groups, remove_outliers_iqr
from visualization.plots import generate_all_plots

st.title('Biostat Decision Tool')

uploaded = st.file_uploader('Upload CSV', type=['csv'])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.write('Preview')
    st.dataframe(df.head())

    cols = df.columns.tolist()
    value_col = st.selectbox('Value column', cols)
    group_col = st.selectbox('Group column', cols)
    alpha = st.number_input('Alpha', value=0.05, step=0.01)
    remove_out = st.checkbox('Remove outliers (IQR)')
    p_corr = st.selectbox('P-value correction', ['none', 'bonferroni', 'holm', 'fdr_bh'])

    if st.button('Run analysis'):
        d = df.copy()
        if remove_out:
            d, summary = remove_outliers_iqr(d, value_col, group_col)
            st.markdown('### Outlier removal summary')
            st.dataframe(summary)

        p_corr_arg = None if p_corr == 'none' else p_corr
        result = analyze_groups(d, value_col, group_col, alpha=alpha, p_correction=p_corr_arg)

        st.markdown('## Analysis Results')
        st.markdown('### Descriptive Statistics')
        desc_df = pd.DataFrame([
            {'Group': group, **values} for group, values in result.get('descriptive', {}).items()
        ])
        st.dataframe(desc_df)

        st.markdown('### Assumption Checks')
        assumptions = result.get('assumptions', {})
        st.write(assumptions)

        st.markdown('### Main Test')
        st.write(result.get('main_test', {}))

        st.markdown('### Post-hoc Results')
        posthoc = result.get('posthoc', [])
        if posthoc:
            st.dataframe(pd.DataFrame(posthoc))
        else:
            st.write('No post-hoc comparisons performed.')

        st.markdown('### Interpretation')
        st.write(result.get('interpretation', ''))

        st.markdown('### Graphs')
        plot_dir = tempfile.mkdtemp(prefix='plots_')
        plot_paths = generate_all_plots(d, value_col, group_col, plot_dir)
        for title, path in plot_paths.items():
            st.image(path, caption=title, use_column_width=True)
            with open(path, 'rb') as f:
                st.download_button(f'Download {title}', data=f, file_name=os.path.basename(path), mime='image/png')

        tmp_x = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        generate_excel_report(result, d, tmp_x.name)
        with open(tmp_x.name, 'rb') as f:
            st.download_button('Download Excel report', data=f, file_name='report.xlsx')

        tmp_p = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        generate_pdf_report(result, tmp_p.name, plot_paths=list(plot_paths.values()))
        with open(tmp_p.name, 'rb') as f:
            st.download_button('Download PDF report', data=f, file_name='report.pdf')
