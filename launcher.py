import os
import sys
import subprocess
import shutil
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

print('Starting Streamlit...')
# --- تعديل رئيسي: إضافة --server.headless=false لإجبار المتصفح على الفتح ---
cmd = [
    venv_python if os.path.exists(venv_python) else sys.executable, 
    '-m', 'streamlit', 'run', 
    os.path.join(project_dir, 'app.py'),
    '--server.headless=false'
]
rc = run(cmd)
sys.exit(rc)
