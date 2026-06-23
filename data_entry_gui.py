import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
from typing import List, Dict

import pandas as pd

from stats_analysis.analysis import analyze_groups, remove_outliers


class DataEntryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('Data Entry - Statistical Analysis')

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill=tk.X)

        ttk.Label(entry_frame, text='Group:').grid(column=0, row=0, sticky=tk.W)
        self.group_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.group_var, width=20).grid(column=1, row=0, padx=4)

        ttk.Label(entry_frame, text='Value:').grid(column=2, row=0, sticky=tk.W)
        self.value_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.value_var, width=20).grid(column=3, row=0, padx=4)

        ttk.Button(entry_frame, text='Add', command=self.add_entry).grid(column=4, row=0, padx=4)

        # Treeview for entries with a scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        cols = ('group', 'value')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=10)
        self.tree.heading('group', text='Group')
        self.tree.heading('value', text='Value')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text='Remove Selected', command=self.remove_selected).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text='Save CSV', command=self.save_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Import CSV', command=self.import_csv).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text='Run Analysis', command=self.run_analysis).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text='Run in Streamlit', command=self.run_analysis_in_streamlit).pack(side=tk.LEFT, padx=6)

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
        self.tree.insert('', tk.END, values=(g, num))
        self.value_var.set('')

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
        if not self.entries:
            messagebox.showinfo('Analysis', 'No entries to analyze.')
            return
        df = pd.DataFrame(self.entries)
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.close()
        df.to_csv(temp_file.name, index=False)

        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        csv_arg = f'--default-csv-path={temp_file.name}'
        cmd = [
            sys.executable,
            '-m', 'streamlit',
            'run',
            app_path,
            '--server.headless=false',
            '--',
            csv_arg,
        ]
        try:
            subprocess.Popen(cmd, cwd=os.path.dirname(app_path), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror('Streamlit Error', f'Unable to start Streamlit: {e}')
            return

        messagebox.showinfo('Streamlit', 'Streamlit is starting with your data. It should open in your browser shortly.')
        threading.Timer(2.0, lambda: webbrowser.open('http://localhost:8501', new=0)).start()

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
