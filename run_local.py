"""Start the optional local model and handbook; Ctrl+C stops both."""
import argparse, os, subprocess, sys, time
from pathlib import Path
from urllib.request import build_opener, ProxyHandler

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime',required=True,type=Path,help='Path to llama-server executable')
    p.add_argument('--model',required=True,type=Path,help='Path to Qwen3-0.6B-Q8_0.gguf')
    args=p.parse_args()
    if not args.runtime.is_file() or not args.model.is_file():p.error('Runtime and model must exist')
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    children=[]
    try:
        model=subprocess.Popen([str(args.runtime.resolve()),'-m',str(args.model.resolve()),'--host','127.0.0.1','--port','8081','-c','2048','-t','4','-np','1','-n','96','--jinja','--log-disable'],creationflags=flags,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);children.append(model)
        opener=build_opener(ProxyHandler({}))
        for _ in range(90):
            if model.poll() is not None:raise RuntimeError('Model exited; check runtime compatibility or port 8081')
            try:
                with opener.open('http://127.0.0.1:8081/health',timeout=1) as r:
                    if r.status==200:break
            except OSError:time.sleep(1)
        else:raise RuntimeError('Model startup timed out')
        os.environ['HANDBOOK_LOCAL_MODEL']='1'
        from http.server import ThreadingHTTPServer
        from server import Handler
        app=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
        app.timeout=.5
        print('Open http://127.0.0.1:8765 — local model enabled. Ctrl+C stops both.',flush=True)
        try:
            while model.poll() is None:app.handle_request()
            raise RuntimeError('Model stopped unexpectedly')
        finally:app.server_close()

    except KeyboardInterrupt:pass
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:child.kill();child.wait()

if __name__=='__main__':main()
