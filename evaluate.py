"""Reproducible synthetic evaluation; no remote calls or pass-rate inflation."""
import argparse
import json
from pathlib import Path
from time import perf_counter
from evidence import Index, ROOT


def evaluate():
    index = Index.load()
    cases = json.loads((ROOT / 'data/evaluation.json').read_text(encoding='utf-8'))['cases']
    rows = []
    for case in cases:
        start = perf_counter()
        answer = index.answer(case['question'])
        ids = [h['id'] for h in answer['retrieved']]
        expected = case['expected']
        returned = answer['citations'][0]['id'] if answer['citations'] else None
        rows.append({**case, 'returned': returned, 'retrieved': ids,
                     'correct': returned == expected,
                     'reciprocal_rank': 1 / (ids.index(expected) + 1) if expected in ids else 0,
                     'latency_ms': round((perf_counter() - start) * 1000, 3)})
    positive = [r for r in rows if r['expected']]
    negative = [r for r in rows if not r['expected']]
    metrics = {'cases': len(rows), 'answerable': len(positive), 'unanswerable': len(negative),
               'recall_at_3': sum(r['expected'] in r['retrieved'] for r in positive) / len(positive),
               'mrr_at_3': sum(r['reciprocal_rank'] for r in positive) / len(positive),
               'correct_source_or_abstention': sum(r['correct'] for r in rows) / len(rows),
               'unanswerable_abstention': sum(r['returned'] is None for r in negative) / len(negative),
               'restricted_document_leaks': sum('STAFF-001' in r['retrieved'] for r in rows)}
    return {'benchmark': 'synthetic-author-written-v1', 'limitations': 'Small lexical smoke test; not a held-out benchmark. No real users. Latency is local single-run, not an SLA.', 'metrics': metrics, 'cases': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Enforce access isolation and minimum smoke-test retrieval only')
    args = parser.parse_args()
    report = evaluate()
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/evaluation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['metrics'], indent=2))
    if args.check and (report['metrics']['restricted_document_leaks'] or report['metrics']['recall_at_3'] < .7):
        raise SystemExit(1)
