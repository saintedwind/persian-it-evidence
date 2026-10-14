"""Verified, attributed Persian reference extracts; not approved support procedures."""
import hashlib
import json
from evidence import ROOT, Document, Index


def load_reference():
    manifest = json.loads((ROOT / 'data/reference-manifest.json').read_text(encoding='utf8'))
    root = ROOT / 'data/persian-reference'
    expected = {row['file'] for row in manifest['sources']}
    if {p.name for p in root.iterdir() if p.is_file()} != expected:
        raise ValueError('Reference inventory mismatch')
    docs = []
    for row in manifest['sources']:
        path = root / row['file']
        if path.resolve().parent != root.resolve():
            raise ValueError('Invalid reference path')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Reference digest mismatch')
        docs.append(Document(row['id'], row['title'], data.decode('utf8'), '', 'public', row['source']))
    return Index(docs, dataset='public-persian-reference/v1')
