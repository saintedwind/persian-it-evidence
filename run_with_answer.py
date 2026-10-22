"""Own a verified local model process and the evidence server; stop both together."""
import argparse
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.request import build_opener, ProxyHandler

EXPECTED_SHA='061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a'


def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--port',type=int,default=18765)
    p.add_argument('--model-port',type=int,default=18817)
    p.add_argument('--stop-file',type=Path)
    args=p.parse_args()
    if not args.runtime.is_file() or not args.model.is_file():p.error('Runtime/model missing')
    if args.stop_file and args.stop_file.exists():p.error('Choose a fresh stop marker')
    if args.port==args.model_port or any(not 1024<=v<=65535 for v in [args.port,args.model_port]):p.error('Invalid ports')
    for port in [args.port,args.model_port]:
        with socket.socket() as probe:
            try:probe.bind(('127.0.0.1',port))
            except OSError:p.error(f'Port {port} unavailable; no existing process will be stopped')
    with args.model.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=EXPECTED_SHA:p.error('Model checksum mismatch')
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    child=subprocess.Popen([str(args.runtime.resolve()),'-m',str(args.model.resolve()),'--host','127.0.0.1',
        '--port',str(args.model_port),'-c','8192','-t','4','-np','1','--jinja','--log-disable'],
        creationflags=flags,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        op=build_opener(ProxyHandler({}));deadline=time.monotonic()+90
        while True:
            if child.poll() is not None:raise RuntimeError('Owned model exited')
            if args.stop_file and args.stop_file.exists():return
            try:
                with op.open(f'http://127.0.0.1:{args.model_port}/health',timeout=1) as response:
                    if response.status==200:break
            except OSError:pass
            if time.monotonic()>deadline:raise TimeoutError('Model startup')
            time.sleep(.5)
        os.environ['HANDBOOK_LOCAL_ANSWER']='1'
        os.environ['HANDBOOK_ANSWER_ENDPOINT']=f'http://127.0.0.1:{args.model_port}/v1/chat/completions'
        from server import LocalServer, Handler
        with LocalServer(('127.0.0.1',args.port),Handler) as app:
            app.timeout=.5
            print(f'Live model and RAG: http://127.0.0.1:{args.port}/demo',flush=True)
            while child.poll() is None:
                if args.stop_file and args.stop_file.exists():break
                app.handle_request()
    except KeyboardInterrupt:pass
    finally:
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:child.kill();child.wait()


if __name__=='__main__':main()
