import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from datetime import datetime
import tkinter.scrolledtext as scrolledtext
import webbrowser
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict


def _get_project_dir():
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        if os.path.exists(os.path.join(base_dir, 'app.py')):
            return base_dir
        parent_dir = os.path.dirname(base_dir)
        if os.path.exists(os.path.join(parent_dir, 'app.py')):
            return parent_dir
        return base_dir
    return os.path.dirname(os.path.abspath(__file__))


def _get_streamlit_pid_file_path():
    project_dir = _get_project_dir()
    return os.path.join(project_dir, '.streamlit_launcher.pid')


def _get_streamlit_state_path():
    project_dir = _get_project_dir()
    return os.path.join(project_dir, '.streamlit_launcher.state.json')


def _read_streamlit_pid():
    pid_file = _get_streamlit_pid_file_path()
    if not os.path.exists(pid_file):
        return None
    try:
        with open(pid_file, 'r', encoding='utf-8') as fh:
            value = fh.read().strip()
        return int(value) if value.isdigit() else None
    except Exception:
        return None


def _write_streamlit_pid(pid):
    pid_file = _get_streamlit_pid_file_path()
    with open(pid_file, 'w', encoding='utf-8') as fh:
        fh.write(str(pid))


def _clear_streamlit_pid():
    pid_file = _get_streamlit_pid_file_path()
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception:
            pass


def _read_streamlit_state():
    state_path = _get_streamlit_state_path()
    if not os.path.exists(state_path):
        return {}
    try:
        with open(state_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _write_streamlit_state(pid, port):
    state_path = _get_streamlit_state_path()
    with open(state_path, 'w', encoding='utf-8') as fh:
        json.dump({'pid': pid, 'port': port}, fh, ensure_ascii=False, indent=2)


def _clear_streamlit_state():
    state_path = _get_streamlit_state_path()
    if os.path.exists(state_path):
        try:
            os.remove(state_path)
        except Exception:
            pass


def _is_port_open(port):
    if not port:
        return False
    try:
        with socket.create_connection(('127.0.0.1', int(port)), timeout=0.5):
            return True
    except OSError:
        return False


def _terminate_process_tree(pid):
    if not pid:
        return
    try:
        if os.name == 'nt':
            subprocess.run(
                ['taskkill', '/PID', str(pid), '/T', '/F'],
                check=False,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except Exception:
        pass


def _get_streamlit_log_path():
    project_dir = _get_project_dir()
    return os.path.join(project_dir, '.streamlit_launcher.log')


def _get_shared_session_store_path():
    project_dir = _get_project_dir()
    return os.path.join(project_dir, '.shared_analysis_session.json')


def _write_shared_session_store(df):
    store_path = _get_shared_session_store_path()
    payload = {
        'columns': df.columns.tolist(),
        'rows': df.to_dict(orient='records'),
    }
    with open(store_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return store_path

import pandas as pd

from stats_analysis.analysis import analyze_groups, remove_outliers


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def _stop_previous_streamlit_processes():
    previous_pid = _read_streamlit_pid()
    if previous_pid is not None:
        _terminate_process_tree(previous_pid)
        _clear_streamlit_pid()
        _clear_streamlit_state()
        return

    if os.name != 'nt':
        return
    try:
        subprocess.run(
            [
                'powershell', '-NoProfile', '-Command',
                "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|pythonw|streamlit' -and $_.CommandLine -match 'streamlit' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
            ],
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


class DataEntryApp:
    def _setup_style(self):
        style = ttk.Style(self.root)
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        else:
            style.theme_use('default')

        default_font = ('Segoe UI', 10)
        style.configure('.', font=default_font)
        style.configure('Card.TFrame', background='#f7f9fc')
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1f2937', background='#f7f9fc')
        style.configure('Section.TLabelframe', background='#f7f9fc', borderwidth=0)
        style.configure('Section.TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground='#334155')
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=(12, 8), background='#2563eb', foreground='white')
        style.map('Accent.TButton', background=[('active', '#1d4ed8'), ('disabled', '#93c5fd')], foreground=[('active', 'white')])
        style.configure('TEntry', padding=5)
        style.configure('Treeview', rowheight=28, background='white', fieldbackground='white')
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#e2e8f0', foreground='#0f172a')
        self.root.option_add('*Font', default_font)
        self.root.configure(background='#f7f9fc')

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Data Entry - Statistical Analysis')
        self._setup_style()

        frame = ttk.Frame(root, padding=12, style='Card.TFrame')
        frame.pack(fill=tk.BOTH, expand=True)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(entry_frame, text='Group:', style='Header.TLabel').grid(column=0, row=0, sticky=tk.W)
        self.group_var = tk.StringVar()
        self.group_entry = ttk.Entry(entry_frame, textvariable=self.group_var, width=24)
        self.group_entry.grid(column=1, row=0, padx=6, pady=4)

        ttk.Label(entry_frame, text='Value:', style='Header.TLabel').grid(column=2, row=0, sticky=tk.W, padx=(12, 0))
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(entry_frame, textvariable=self.value_var, width=24)
        self.value_entry.grid(column=3, row=0, padx=6, pady=4)
        self.value_entry.bind('<Return>', self._on_value_return)

        ttk.Button(entry_frame, text='Add', command=self.add_entry, style='Accent.TButton').grid(column=4, row=0, padx=6, pady=4)

        # Treeview for entries with a scrollbar
        tree_frame = ttk.Frame(frame, padding=10, style='Card.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        cols = ('group', 'value')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=10)
        self.tree.heading('group', text='Group')
        self.tree.heading('value', text='Value')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('oddrow', background='#f8fafc')

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text='Remove Selected', command=self.remove_selected, style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(btn_frame, text='Save CSV', command=self.save_csv, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Import CSV', command=self.import_csv, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Run Analysis', command=self.run_analysis, style='Accent.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Run in Streamlit', command=self.run_analysis_in_streamlit, style='Accent.TButton').pack(side=tk.LEFT, padx=6)

        self.entries: List[Dict[str, object]] = []

    def add_entry(self):
        g = self.group_var.get().strip()
        v = self.value_var.get().strip()
        if g == '' or v == '':
            messagebox.showwarning('Input', 'Please provide both group and value.')
            return
        try:
            num = float(v)
        except Exception:
            messagebox.showerror('Input', 'Value must be numeric.')
            return
        self.entries.append({'group': g, 'value': num})
        tag = 'evenrow' if len(self.entries) % 2 == 0 else 'oddrow'
        self.tree.insert('', tk.END, values=(g, num), tags=(tag,))
        self.value_var.set('')
        self.value_entry.focus_set()

    def _refresh_tree_tags(self):
        for index, item in enumerate(self.tree.get_children()):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.item(item, tags=(tag,))

    def _on_value_return(self, event):
        self.add_entry()

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for item in sel:
            vals = self.tree.item(item, 'values')
            try:
                # remove first matching entry
                for i, e in enumerate(self.entries):
                    if str(e['group']) == str(vals[0]) and float(e['value']) == float(vals[1]):
                        self.entries.pop(i)
                        break
            except Exception:
                pass
            self.tree.delete(item)
        self._refresh_tree_tags()

    def save_csv(self):
        if not self.entries:
            messagebox.showinfo('Save', 'No entries to save.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        df = pd.DataFrame(self.entries)
        df.to_csv(path, index=False)
        messagebox.showinfo('Save', f'Saved {len(df)} rows to {path}')

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror('Import Error', f'Unable to read CSV: {e}')
            return

        if 'group' not in df.columns or 'value' not in df.columns:
            messagebox.showerror('Import Error', 'CSV must contain "group" and "value" columns.')
            return

        try:
            entries = []
            for _, row in df.iterrows():
                g = str(row['group']).strip()
                v = float(row['value'])
                entries.append({'group': g, 'value': v})
        except Exception as e:
            messagebox.showerror('Import Error', f'Invalid data in CSV: {e}')
            return

        self.entries = entries
        for item in self.tree.get_children():
            self.tree.delete(item)
        for e in self.entries:
            self.tree.insert('', tk.END, values=(e['group'], e['value']))
        messagebox.showinfo('Import CSV', f'Imported {len(self.entries)} rows from {path}')

    def run_analysis(self):
        if not self.entries:
            messagebox.showinfo('Analysis', 'No entries to analyze.')
            return
        df = pd.DataFrame(self.entries)
        try:
            result = analyze_groups(df, value_col='value', group_col='group', language='en')
        except Exception as e:
            messagebox.showerror('Analysis Error', str(e))
            return
        self.show_result_window(result)

    def run_analysis_in_streamlit(self):
        import subprocess
        import os
        import sys
        import threading
        import webbrowser
        import shutil
        import pandas as pd

        if not self.entries:
            messagebox.showinfo('Analysis', 'No entries to analyze.')
            return

        df = pd.DataFrame(self.entries)
        session_store_path = _write_shared_session_store(df)

        state = _read_streamlit_state()
        existing_port = state.get('port')
        if existing_port and _is_port_open(existing_port):
            messagebox.showinfo(
                'Streamlit',
                'Streamlit is already running. Refreshing data without restarting the server.'
            )
            threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{existing_port}/?refresh={os.getpid()}', new=0)).start()
            return

        if state.get('pid') is not None:
            _terminate_process_tree(state.get('pid'))
        _clear_streamlit_pid()
        _clear_streamlit_state()
        _stop_previous_streamlit_processes()

        project_dir = _get_project_dir()
        app_path = os.path.join(project_dir, 'app.py')

        if not os.path.exists(app_path):
            messagebox.showerror(
                'Streamlit Error',
                f'Cannot locate app.py\nExpected: {app_path}'
            )
            return

        streamlit_port = _get_free_port()

        streamlit_exec = shutil.which("streamlit")

        if not streamlit_exec:
            messagebox.showerror(
                'Streamlit Error',
                'Streamlit is not installed or not in PATH.'
            )
            return

        cmd = [
            streamlit_exec,
            "run",
            app_path,
            f"--server.port={streamlit_port}",
            "--server.address=127.0.0.1",
            "--server.headless=true",
            "--",
            f"--session-store-path={session_store_path}",
        ]

        env = os.environ.copy()
        env.update({
            'STAT_APP_SESSION_STORE_PATH': session_store_path,
            'DEFAULT_SESSION_STORE_PATH': session_store_path,
        })

        log_path = _get_streamlit_log_path()
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        popen_kwargs = dict(
            cwd=os.path.dirname(app_path),
            env=env,
            stdin=subprocess.DEVNULL,
        )

        if os.name == 'nt':
            popen_kwargs['creationflags'] = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
            if hasattr(subprocess, 'CREATE_NO_WINDOW'):
                popen_kwargs['creationflags'] |= subprocess.CREATE_NO_WINDOW
        else:
            popen_kwargs['start_new_session'] = True

        try:
            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Starting Streamlit from {app_path}\n')
                log_file.flush()
                proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT, **popen_kwargs)
                _write_streamlit_pid(proc.pid)
                _write_streamlit_state(proc.pid, streamlit_port)
        except Exception as e:
            messagebox.showerror('Streamlit Error', str(e))
            return

        messagebox.showinfo(
            'Streamlit',
            'Streamlit is starting... Browser will open shortly.'
        )

        def open_browser():
            webbrowser.open(f'http://127.0.0.1:{streamlit_port}')

        threading.Timer(3.5, open_browser).start()

    def show_result_window(self, result: dict):
        win = tk.Toplevel(self.root)
        win.title('Analysis Results')
        txt = scrolledtext.ScrolledText(win, width=100, height=40)
        txt.pack(fill=tk.BOTH, expand=True)
        def safe_format(obj):
            try:
                return pd.DataFrame(obj).to_string() if isinstance(obj, (list, dict)) and not isinstance(obj, str) else str(obj)
            except Exception:
                return str(obj)

        txt.insert(tk.END, 'Descriptive Statistics:\n')
        txt.insert(tk.END, safe_format(result.get('descriptive', {})) + '\n\n')
        txt.insert(tk.END, 'Assumptions:\n')
        txt.insert(tk.END, safe_format(result.get('assumptions', {})) + '\n\n')
        txt.insert(tk.END, 'Main Test:\n')
        txt.insert(tk.END, safe_format(result.get('main_test', {})) + '\n\n')
        txt.insert(tk.END, 'Post-hoc:\n')
        txt.insert(tk.END, safe_format(result.get('posthoc', [])) + '\n\n')
        txt.insert(tk.END, 'Interpretation:\n')
        txt.insert(tk.END, str(result.get('interpretation', '')) + '\n')
        txt.configure(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = DataEntryApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
