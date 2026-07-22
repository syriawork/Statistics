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
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

try:
    print('started launcher')
    for i in range(30):
        time.sleep(1)
        try:
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=2)
            conn.request('GET', '/')
            res = conn.getresponse()
            print('status', res.status)
            print('reason', res.reason)
            print('headers', res.getheaders())
            body = res.read(500)
            print('body', body[:500])
            conn.close()
            break
        except Exception as e:
            print('wait', i, repr(e))
    else:
        print('no response from server')
finally:
    proc.terminate()
    proc.wait(timeout=10)
