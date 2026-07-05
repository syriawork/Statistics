import argparse
import inspect
import json
import os
import sys
import tempfile

import pandas as pd
import streamlit as st

from pharma_tools import calculate_process_capability
from reports.excel import generate_excel_report
from reports.pdf import generate_pdf_report
from stats_analysis.analysis import analyze_groups, remove_outliers
from utilities.translations import translate, translate_option
from visualization.plots import generate_all_plots


def _maybe_translate_df(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    return df


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--default-csv-path', type=str, default=None)
    parser.add_argument('--session-store-path', type=str, default=None)
    return parser.parse_known_args(argv or sys.argv[1:])


def _get_session_store_path(argv=None, environ=None):
    parsed_args, _ = _parse_args(argv)
    path = parsed_args.session_store_path
    if path:
        return path

    env = environ or os.environ
    for key in ('STAT_APP_SESSION_STORE_PATH', 'DEFAULT_SESSION_STORE_PATH'):
        candidate = env.get(key)
        if candidate:
            return candidate
    return None


def _get_default_csv_path(argv=None, environ=None):
    parsed_args, _ = _parse_args(argv)
    path = parsed_args.default_csv_path
    if path:
        return path

    env = environ or os.environ
    for key in ('STAT_APP_DEFAULT_CSV_PATH', 'DEFAULT_CSV_PATH'):
        candidate = env.get(key)
        if candidate:
            return candidate
    # If no arg or env var provided, try some common filenames in the project
    cwd = os.path.dirname(__file__) or os.getcwd()
    common_names = [
        'user_data.csv',
        'test.csv',
        'test_scenario.csv',
        os.path.join('data', 'example.csv'),
        'report.csv',
    ]
    for name in common_names:
        candidate = os.path.join(cwd, name) if not os.path.isabs(name) else name
        if os.path.isfile(candidate):
            return candidate
    return None


def _load_dataframe_from_session_store(session_store_path=None):
    if not session_store_path or not os.path.isfile(session_store_path):
        return None, False

    try:
        with open(session_store_path, 'r', encoding='utf-8') as fh:
            payload = json.load(fh)
        if isinstance(payload, dict) and 'columns' in payload and 'rows' in payload:
            return pd.DataFrame(payload['rows'], columns=payload.get('columns', [])), True
        if isinstance(payload, list):
            return pd.DataFrame(payload), True
    except Exception:
        return None, False

    return None, False


def _load_dataframe(default_csv_path=None):
    lang_code = 'en'
    session_store_path = _get_session_store_path()
    if session_store_path:
        session_df, loaded_from_store = _load_dataframe_from_session_store(session_store_path)
        if session_df is not None:
            st.info(translate('Loaded data from the shared session store.', lang_code))
            return session_df, loaded_from_store

    if default_csv_path and os.path.isfile(default_csv_path):
        st.info(translate('Loaded data from the local GUI.', lang_code))
        return pd.read_csv(default_csv_path), True

    uploaded = st.file_uploader(translate('Upload CSV', lang_code), type=['csv'])
    if uploaded is not None:
        return pd.read_csv(uploaded), False
    return None, False


def main():
    lang_code = 'en'
    st.title(translate('Biostat Decision Tool', lang_code))

    default_csv_path = _get_default_csv_path()
    df, loaded_from_default = _load_dataframe(default_csv_path)

    if df is not None:
        st.markdown(f"### {translate('Preview', lang_code)}")
        st.dataframe(df.head())

        cols = df.columns.tolist()
        value_col = st.selectbox(translate('Value column', lang_code), cols)
        group_col = st.selectbox(translate('Group column', lang_code), cols)
        alpha = st.number_input(translate('Alpha', lang_code), value=0.05, step=0.01)
        outlier_method = st.selectbox(
            translate('Outlier removal method', lang_code),
            ['none', 'iqr', 'zscore', 'three-sigma', 'grubbs', 'dixon'],
            format_func=lambda x: translate_option(x, lang_code),
        )
        zscore_threshold = st.number_input(translate('Z-score threshold', lang_code), value=3.0, step=0.1)
        paired = st.checkbox(translate('Paired samples (paired t-test / Wilcoxon)', lang_code))
        calculate_capability = st.checkbox(translate('Calculate Cp/CpK', lang_code))
        usl = None
        lsl = None
        if calculate_capability:
            usl = st.number_input(translate('USL', lang_code), value=0.0, step=0.1)
            lsl = st.number_input(translate('LSL', lang_code), value=0.0, step=0.1)
        p_corr = st.selectbox(
            translate('P-value correction', lang_code),
            ['none', 'bonferroni', 'holm', 'fdr_bh'],
            format_func=lambda x: translate_option(x, lang_code),
        )

        if st.button(translate('Run analysis', lang_code)):
            d = df.copy()

            unique_groups = d[group_col].nunique()
            if paired and unique_groups > 2:
                st.warning(
                    f"⚠️ Paired t-test only works with 2 groups. You have {unique_groups} groups. The analysis will use Kruskal-Wallis or ANOVA instead."
                )

            if outlier_method != 'none':
                d, summary = remove_outliers(d, value_col, group_col, method=outlier_method, z_threshold=zscore_threshold)
                st.markdown(f"### {translate('Outlier removal summary', lang_code)}")
                st.dataframe(_maybe_translate_df(summary, lang_code))

            p_corr_arg = None if p_corr == 'none' else p_corr
            analyze_kwargs = {
                'df': d,
                'value_col': value_col,
                'group_col': group_col,
                'alpha': alpha,
                'p_correction': p_corr_arg,
                'paired': paired,
            }
            if 'language' in inspect.signature(analyze_groups).parameters:
                analyze_kwargs['language'] = lang_code
            result = analyze_groups(**analyze_kwargs)
            if calculate_capability and usl is not None and lsl is not None and usl > lsl:
                capability = calculate_process_capability(d[value_col].astype(float).dropna(), usl, lsl)
                result['capability'] = capability
            elif calculate_capability:
                st.warning(translate('USL must be greater than LSL to calculate Cp/CpK.', lang_code))

            st.markdown(f"## {translate('Analysis Results', lang_code)}")
            st.info(f"📊 Groups analyzed: {unique_groups} ({', '.join(sorted(d[group_col].unique().astype(str)))})")

            st.markdown(f"### {translate('Descriptive Statistics', lang_code)}")
            desc_df = pd.DataFrame([
                {'Group': group, **values} for group, values in result.get('descriptive', {}).items()
            ])
            st.dataframe(_maybe_translate_df(desc_df, lang_code))

            st.markdown(f"### {translate('Assumption Checks', lang_code)}")
            assumptions = result.get('assumptions', {})
            assumptions_df = pd.DataFrame([assumptions])
            st.dataframe(_maybe_translate_df(assumptions_df, lang_code))

            st.markdown(f"### {translate('Main Test', lang_code)}")
            main_test = result.get('main_test', {})
            main_df = pd.DataFrame([main_test])
            st.dataframe(_maybe_translate_df(main_df, lang_code))

            st.markdown(f"### {translate('Post-hoc Results', lang_code)}")
            posthoc = result.get('posthoc', [])
            if posthoc:
                posthoc_df = pd.DataFrame(posthoc)
                st.dataframe(_maybe_translate_df(posthoc_df, lang_code))
            else:
                st.write(translate('No post-hoc comparisons were performed.', lang_code))

            if result.get('outlier_summary'):
                st.markdown(f"### {translate('Outlier Summary', lang_code)}")
                st.dataframe(_maybe_translate_df(pd.DataFrame(result['outlier_summary']), lang_code))
                st.markdown(f"**{translate('Outlier method:', lang_code)}** {translate_option(result.get('outlier_method', 'none'), lang_code)}")

            if result.get('capability'):
                st.markdown(f"### {translate('Process Capability', lang_code)}")
                capability_df = pd.DataFrame([result['capability']])
                st.dataframe(_maybe_translate_df(capability_df, lang_code))

            st.markdown(f"### {translate('Interpretation', lang_code)}")
            st.write(result.get('interpretation', ''))

            st.markdown(f"### {translate('Graphs', lang_code)}")
            plot_dir = tempfile.mkdtemp(prefix='plots_')
            plot_paths = generate_all_plots(d, value_col, group_col, plot_dir)
            for title, path in plot_paths.items():
                st.image(path, caption=title, width=700)
                with open(path, 'rb') as f:
                    st.download_button(f"{translate('Download', lang_code)} {title}", data=f, file_name=os.path.basename(path), mime='image/png')

            tmp_x = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            if 'lang' in inspect.signature(generate_excel_report).parameters:
                generate_excel_report(result, d, tmp_x.name, lang=lang_code)
            else:
                generate_excel_report(result, d, tmp_x.name)
            with open(tmp_x.name, 'rb') as f:
                st.download_button(translate('Download Excel report', lang_code), data=f, file_name='report.xlsx')

            tmp_p = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            if 'lang' in inspect.signature(generate_pdf_report).parameters:
                generate_pdf_report(result, tmp_p.name, plot_paths=list(plot_paths.values()), lang=lang_code)
            else:
                generate_pdf_report(result, tmp_p.name, plot_paths=list(plot_paths.values()))
            with open(tmp_p.name, 'rb') as f:
                st.download_button(translate('Download PDF report', lang_code), data=f, file_name='report.pdf')


if __name__ == '__main__':
    main()
