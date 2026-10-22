"""Local support handbook. Public documents only; no authentication service."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from functools import lru_cache
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
from evidence import Index
from local_draft import draft, enabled
from local_answer import answer as synthesize, enabled as answer_enabled

ROOT = Path(__file__).resolve().parent
INDEX = Index.load()


@lru_cache(maxsize=2)
def get_index(collection='sample'):
    if collection == 'sample':
        index = INDEX
    elif collection == 'reference':
        from reference import load_reference
        index = load_reference()
    else:
        raise ValueError('Unknown collection')
    if os.environ.get('HANDBOOK_RETRIEVER', 'lexical') == 'hybrid':
        metadata = getattr(index, 'reference_metadata', None)
        from semantic import Encoder, SemanticIndex
        settings = json.loads((ROOT/'data/semantic-settings.json').read_text(encoding='utf8'))
        index = SemanticIndex(index.documents, get_encoder(), settings['threshold'], settings['margin'], index.dataset)
        if metadata is not None:
            index.reference_metadata = metadata
    return index


@lru_cache(maxsize=1)
def get_encoder():
    from semantic import Encoder
    return Encoder()


class LocalServer(ThreadingHTTPServer):
    # A timed-out request must not prevent the local application from stopping.
    daemon_threads = True
    allow_reuse_address = True


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def send(self, code, payload, mime='application/json; charset=utf-8'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass  # The caller may have cancelled; never log its question.

    def do_GET(self):
        url = urlsplit(self.path)
        routes = {'/': ('index.html', 'text/html; charset=utf-8'),
                  '/demo': ('demo.html', 'text/html; charset=utf-8'),
                  '/demo.js': ('demo.js', 'application/javascript; charset=utf-8'),
                  '/demo.css': ('demo.css', 'text/css; charset=utf-8'),
                  '/app.js': ('app.js', 'application/javascript; charset=utf-8'),
                  '/style.css': ('style.css', 'text/css; charset=utf-8'),
                  '/Gandom.woff2': ('Gandom.woff2', 'font/woff2')}
        if url.path == '/health':
            return self.send(200, {'status': 'ok', 'version':'0.6.0',
                'retriever': os.environ.get('HANDBOOK_RETRIEVER','lexical'), 'local_draft': enabled(), 'local_answer':answer_enabled()})
        if url.path == '/api/documents':
            try:
                index = get_index(parse_qs(url.query).get('collection',['sample'])[0])
            except ValueError:
                return self.send(400, {'error':'Unknown collection'})
            documents = [{'id': d.id, 'title': d.title, 'text': d.text, 'source': d.source, **index.receipt(d),
                          **getattr(index, 'reference_metadata', {}).get(d.id, {})}
                         for d in index.documents if d.scope == 'public']
            doc_id = parse_qs(url.query).get('id', [None])[0]
            if doc_id is not None:
                match = next((d for d in documents if d['id'] == doc_id), None)
                return self.send(200, match) if match else self.send(404, {'error': 'Document not found'})
            return self.send(200, {'documents': documents, 'dataset': index.dataset, 'corpus_sha256':index.corpus_digest()})
        if url.path not in routes:
            return self.send(404, {'error': 'Not found'})
        file, mime = routes[url.path]
        self.send(200, (ROOT / 'web' / file).read_bytes(), mime)

    def do_POST(self):
        if self.path not in {'/api/ask', '/api/draft', '/api/answer'}:
            return self.send(404, {'error': 'Not found'})
        host = self.headers.get('Host', '')
        permitted = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        origin = self.headers.get('Origin')
        if host not in permitted or (origin and origin not in {'http://' + h for h in permitted}):
            return self.send(403, {'error': 'Local same-origin requests only'})
        if self.headers.get('Transfer-Encoding'):
            return self.send(400, {'error': 'Transfer encoding is not supported'})
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            return self.send(415, {'error': 'Content-Type must be application/json'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 16000:
                return self.send(413, {'error': 'Request size must be 1–16000 bytes'})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict) or 'question' not in data or set(data) - {'question','collection'}:
                return self.send(400, {'error': 'Only question and optional collection are allowed'})
            index = get_index(data.get('collection','sample'))
            # The browser cannot select staff access; trusted application decides scope.
            result = (synthesize(index, data['question']) if self.path == '/api/answer' else
                      draft(index, data['question']) if self.path == '/api/draft' else
                      index.answer(data['question'], scope='public'))
            self.send(200, result)
        except (ValueError, TypeError, UnicodeDecodeError):
            self.send(400, {'error': 'Invalid JSON or question'})

    def log_message(self, format, *args):
        pass  # Do not store user questions in access logs.


if __name__ == '__main__':
    if os.environ.get('HANDBOOK_RETRIEVER','lexical') not in {'lexical','hybrid'}:
        raise ValueError('HANDBOOK_RETRIEVER must be lexical or hybrid')
    if os.environ.get('HANDBOOK_RETRIEVER') == 'hybrid':
        get_index('sample'); get_index('reference')  # Fail startup explicitly if model/dependencies are absent.
    print('Local demo: http://127.0.0.1:8765 (Ctrl+C to stop)', flush=True)
    with LocalServer(('127.0.0.1', 8765), Handler) as app:
        try:
            app.serve_forever()
        except KeyboardInterrupt:
            pass
