import os
import subprocess
import time
import http.client

launcher = r'e:\programs and applications\Statistics\dist_final\launcher\launcher.exe'
if not os.path.exists(launcher):
    raise FileNotFoundError(launcher)
port = 55322
proc = subprocess.Popen(
    [launcher, '--server', str(port)],
    cwd=r'e:\programs and applications\Statistics\dist_final\launcher',
    stdin=subprocess.DEVNULL,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)
print('started launcher', launcher)
try:
    t0 = time.time()
    while time.time() - t0 < 15:
        line = proc.stdout.readline()
        if not line:
            break
        print('OUT>', line.rstrip())
        if 'You can now view your Streamlit app in your browser.' in line:
            break
    paths = ['/', '/?','/index.html','/_stdata','/healthz','/stream','/static']
    for path in paths:
        try:
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
            conn.request('GET', path)
            res = conn.getresponse()
            body = res.read(300)
            print(path, res.status, res.reason, body[:300])
            conn.close()
        except Exception as e:
            print(path, 'ERROR', repr(e))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
