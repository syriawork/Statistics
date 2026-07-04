import argparse
import os
import shutil
import socket
import subprocess
import sys
import time

# Determine project directory: when frozen, use the exe location; otherwise use file location
if getattr(sys, 'frozen', False):
    exe_path = os.path.abspath(sys.argv[0])
    exe_dir = os.path.dirname(exe_path)
    # If exe is inside a dist/ folder and parent contains app.py, use parent as project dir
    parent = os.path.dirname(exe_dir)
    if os.path.exists(os.path.join(parent, 'app.py')):
        project_dir = parent
    else:
        project_dir = exe_dir
else:
    project_dir = os.path.dirname(os.path.abspath(__file__))

venv_dir = os.path.join(project_dir, '.venv')
venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
requirements = os.path.join(project_dir, 'requirements.txt')


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def _stop_previous_streamlit_processes():
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


def run(cmd):
    print('Running:', ' '.join(cmd))
    
    # --- تعديل رئيسي لإخفاء النافذة السوداء في الويندوز ---
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    # تمرير إعدادات الإخفاء، وفصل القنوات القياسية لتجنب تعليق البرنامج
    proc = subprocess.Popen(
        cmd, 
        startupinfo=startupinfo, 
        stdin=subprocess.DEVNULL, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    proc.wait()
    return proc.returncode

if not os.path.exists(venv_python):
    print('Creating virtual environment...')
    def find_system_python():
        for name in ('python', 'python3', 'py'):
            p = shutil.which(name)
            if p:
                return p
        return None

    system_py = find_system_python()
    if not system_py:
        print('No system Python found in PATH to create venv. Please install Python.')
        sys.exit(1)
    rc = run([system_py, '-m', 'venv', venv_dir])
    if rc != 0:
        print('Failed to create virtualenv')
        sys.exit(rc)
    print('Installing requirements...')
    pip_cmd = [venv_python, '-m', 'pip', 'install', '--upgrade', 'pip']
    run(pip_cmd)
    if os.path.exists(requirements):
        rc = run([venv_python, '-m', 'pip', 'install', '-r', requirements])
        if rc != 0:
            print('Failed to install requirements')
            sys.exit(rc)
    else:
        print('No requirements.txt found; skipping pip install')

# Give a short pause to ensure venv is ready
time.sleep(1)

parser = argparse.ArgumentParser(description='Launch the statistical application')
parser.add_argument('--gui', action='store_true', help='Run the local Tkinter data entry GUI instead of Streamlit')
args = parser.parse_args()

if args.gui:
    print('Starting local Tkinter GUI...')
    cmd = [
        venv_python if os.path.exists(venv_python) else sys.executable,
        os.path.join(project_dir, 'data_entry_gui.py'),
    ]
else:
    print('Stopping previous Streamlit processes...')
    _stop_previous_streamlit_processes()
    print('Starting Streamlit...')
    streamlit_port = _get_free_port()
    cmd = [
        venv_python if os.path.exists(venv_python) else sys.executable,
        '-m', 'streamlit', 'run',
        os.path.join(project_dir, 'app.py'),
        '--server.headless=true',
        f'--server.port={streamlit_port}',
        '--server.address=127.0.0.1'
    ]
rc = run(cmd)
sys.exit(rc)
