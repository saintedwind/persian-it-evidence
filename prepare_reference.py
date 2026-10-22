"""Fetch attributed Wikipedia introductions into staging; never invent missing content.

New records are staged with raw API receipts for review before corpus activation.
The existing frozen collection is not modified by this command.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent


def validate_page(page):
    if page.get('missing') is not None or page.get('ns') != 0:
        raise ValueError('Missing or non-article page')
    if 'disambiguation' in page.get('pageprops', {}):
        raise ValueError('Disambiguation page')
    text = page.get('extract', '')
    if not isinstance(text, str) or len(text.strip()) < 180 or len(text) > 30000:
        raise ValueError('Empty, undersized or oversized introduction')
    if not isinstance(page.get('lastrevid'), int) or not isinstance(page.get('pageid'), int):
        raise ValueError('Missing revision identity')
    return text


def fetch(topic, opener):
    params = {'action':'query','format':'json','redirects':1,'prop':'extracts|info|pageprops',
              'exintro':1,'explaintext':1,'titles':topic['title']}
    url = 'https://fa.wikipedia.org/w/api.php?' + urlencode(params)
    request = Request(url, headers={'User-Agent':'PersianITEvidence/0.6 (curated attributed educational references)'})
    with opener.open(request, timeout=30) as response:
        raw = response.read(500001)
    if len(raw) > 500000:
        raise ValueError('API receipt exceeded size bound')
    data = json.loads(raw)
    pages = list(data['query']['pages'].values())
    if len(pages) != 1:
        raise ValueError('Expected one resolved article')
    page = pages[0]
    text = validate_page(page)
    row = {'id':topic['id'],'title':page['title'],'requested_title':topic['title'],
           'file':topic['id']+'.txt','sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),
           'source':f"https://fa.wikipedia.org/w/index.php?oldid={page['lastrevid']}",
           'history':f"https://fa.wikipedia.org/w/index.php?curid={page['pageid']}&action=history",
           'revision':page['lastrevid'],'pageid':page['pageid'],'license':'CC-BY-SA-4.0',
           'authors':'Persian Wikipedia contributors','retrieved_at':datetime.now(timezone.utc).isoformat(),
           'category':topic['category'],'aliases':topic.get('aliases',''),
           'receipt_sha256':hashlib.sha256(raw).hexdigest(),'receipt_file':topic['id']+'.json',
           'method':'MediaWiki exintro/explaintext with info and redirect resolution; unchanged introduction'}
    return row, text, raw


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New staging directory; active corpus is never edited')
    parser.add_argument('--resume', action='store_true', help='Keep successful staged records and retry missing topics')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=args.resume)
    plan = json.loads((ROOT/'data/reference-expansion-plan.json').read_text(encoding='utf-8'))
    opener = build_opener(ProxyHandler({}))
    prior = json.loads((args.output/'staging-manifest.json').read_text(encoding='utf-8')) if args.resume else {}
    rows, failures = prior.get('sources', []), []
    for topic in plan['topics']:
        if any(row['id'] == topic['id'] for row in rows):
            continue
        try:
            try:
                row, text, raw = fetch(topic, opener)
            except HTTPError as exc:
                if exc.code != 429:
                    raise
                # Respect upstream rate limiting; no proxy, account or host rotation.
                delay = max(60, int(exc.headers.get('Retry-After', '60')))
                if delay > 300:
                    raise
                print(f'Upstream rate limit: waiting {delay}s before one retry', flush=True)
                time.sleep(delay)
                row, text, raw = fetch(topic, opener)
            if any(r['revision'] == row['revision'] or r['sha256'] == row['sha256'] for r in rows):
                raise ValueError('Duplicate resolved article')
            (args.output/row['file']).write_bytes(text.encode('utf-8'))
            (args.output/row['receipt_file']).write_bytes(raw)
            rows.append(row)
            print(topic['id']+' OK',flush=True)
        except (OSError, ValueError, KeyError) as exc:
            failures.append({'id':topic['id'],'title':topic['title'],'error':str(exc)})
            print(topic['id']+' REJECTED: '+type(exc).__name__,flush=True)
        time.sleep(2)
    result={'dataset':plan['version'],'sources':rows,'failures':failures}
    (args.output/'staging-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Staged {len(rows)} articles; rejected {len(failures)}. Review before activation.',flush=True)


if __name__ == '__main__':
    main()
