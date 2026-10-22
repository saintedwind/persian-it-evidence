"""Verified, attributed Persian reference extracts; not approved support procedures."""
import hashlib
import json
import re
from evidence import ROOT, Document, Index


def load_reference():
    manifest = json.loads((ROOT / 'data/reference-manifest.json').read_text(encoding='utf8'))
    root = ROOT / 'data/persian-reference'
    expected = {row['file'] for row in manifest['sources']}
    if {p.name for p in root.iterdir() if p.is_file()} != expected:
        raise ValueError('Reference inventory mismatch')
    docs = []
    metadata = {}
    ids, revisions, digests = set(), set(), set()
    for row in manifest['sources']:
        if not re.fullmatch(r'REF-[A-Z0-9-]+', row['id']) or row['id'] in ids:
            raise ValueError('Invalid or duplicate reference identity')
        if row['revision'] in revisions or row['sha256'] in digests:
            raise ValueError('Duplicate reference content')
        if row['source'] != f"https://fa.wikipedia.org/w/index.php?oldid={row['revision']}" or row['license'] != 'CC-BY-SA-4.0':
            raise ValueError('Invalid source attribution')
        ids.add(row['id']); revisions.add(row['revision']); digests.add(row['sha256'])
        path = root / row['file']
        if path.resolve().parent != root.resolve():
            raise ValueError('Invalid reference path')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Reference digest mismatch')
        if 'receipt_file' in row:
            receipt_root = ROOT / 'data/reference-receipts'
            receipt_path = receipt_root / row['receipt_file']
            if receipt_path.resolve().parent != receipt_root.resolve():
                raise ValueError('Invalid receipt path')
            raw = receipt_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != row['receipt_sha256']:
                raise ValueError('Receipt digest mismatch')
            pages = list(json.loads(raw)['query']['pages'].values())
            if len(pages) != 1 or pages[0]['extract'] != data.decode('utf8') or pages[0]['lastrevid'] != row['revision'] or pages[0]['title'] != row['title']:
                raise ValueError('Reference and API receipt disagree')
        docs.append(Document(row['id'], row['title'], data.decode('utf8'), row.get('aliases',''), 'public', row['source']))
        metadata[row['id']] = {key: row[key] for key in ('category','license','authors','retrieved_at','revision') if key in row}
        metadata[row['id']].setdefault('retrieved_at', manifest['retrieved_at'])
    index = Index(docs, dataset=manifest.get('dataset', 'public-persian-reference/v1'))
    index.reference_metadata = metadata
    return index
