import os
import subprocess
import time
import http.client

launcher = r'e:\programs and applications\Statistics\dist_final\launcher\launcher.exe'
if not os.path.exists(launcher):
    raise FileNotFoundError(launcher)
port = 55321
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
    while True:
        line = proc.stdout.readline()
        if line == '' and proc.poll() is not None:
            break
        if line:
            print('OUT>', line.rstrip())
        if time.time() - t0 > 15:
            break
    try:
        conn = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
        conn.request('GET', '/')
        res = conn.getresponse()
        print('status', res.status)
        print('reason', res.reason)
        print('headers', res.getheaders())
        print('body', res.read(500))
        conn.close()
    except Exception as e:
        print('http error', repr(e))
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
