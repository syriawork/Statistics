import os
import sys
import socket
import importlib.metadata
import subprocess
from pathlib import Path

# When running as a frozen EXE, help tkinter find bundled Tcl/Tk data
if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    candidates = [
        os.path.join(base_path, '_internal', '_tcl_data'),
        os.path.join(base_path, '_tcl_data'),
        os.path.join(os.path.dirname(sys.executable), '_tcl_data'),
    ]
    for c in candidates:
        if os.path.exists(c):
            os.environ.setdefault('TCL_LIBRARY', c)
            os.environ.setdefault('TK_LIBRARY', c)
            break

# حل مشكلة الإصدار بشكل ديناميكي (يمنع 404 بسبب الميتا-داتا)
if getattr(sys, 'frozen', False):
    def get_streamlit_version():
        try:
            import streamlit
            return getattr(streamlit, '__version__', "1.35.0")
        except Exception:
            return "1.35.0"

    st_version = get_streamlit_version()
    orig_version = importlib.metadata.version
    def patched_version(name):
        if name == 'streamlit':
            return st_version
        return orig_version(name)
    importlib.metadata.version = patched_version

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # البحث في مجلد الاستخراج المؤقت وفي مجلد _internal
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        for p in [base_path, os.path.join(base_path, '_internal')]:
            full_p = os.path.join(p, relative_path)
            if os.path.exists(full_p):
                return os.path.abspath(full_p)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))

def run_streamlit(port):
    app_path = get_resource_path("app.py")
    app_dir = str(Path(app_path).resolve().parent)
    try:
        os.chdir(app_dir or os.getcwd())
    except Exception:
        pass

    if getattr(sys, 'frozen', False):
        # A PyInstaller executable cannot be used as ``python -m streamlit``.
        # Run Streamlit in this process instead of recursively launching the EXE.
        import streamlit.web.cli as stcli
        sys.argv = [
            'streamlit', 'run', app_path,
            '--server.port', str(int(port)),
            '--server.headless', 'true',
            '--server.address', '127.0.0.1',
            '--global.developmentMode', 'false',
            '--browser.gatherUsageStats', 'false',
        ]
        stcli.main()
        return

    import streamlit.web.cli as stcli
    sys.argv = [
        'streamlit', 'run', app_path,
        '--server.port', str(int(port)),
        '--server.headless', 'true',
        '--server.address', '127.0.0.1',
        '--global.developmentMode', 'false',
        '--browser.gatherUsageStats', 'false',
    ]
    stcli.main()

if __name__ == "__main__":
    if "--server" in sys.argv:
        idx = sys.argv.index("--server")
        port = int(sys.argv[idx + 1]) if idx + 1 < len(sys.argv) else 8501
        run_streamlit(port)
    else:
        from data_entry_gui import main
        main()
