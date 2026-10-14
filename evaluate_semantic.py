"""Real local model comparison. Calibration sees development cases only."""
import hashlib
import json
import platform
from time import perf_counter
from evidence import Index, ROOT
from semantic import Encoder, SemanticIndex, MODEL, REVISION
from reference import load_reference


class MemoEncoder:
    def __init__(self, encoder):
        self.encoder, self.cache = encoder, {}
    def encode(self, texts):
        missing = list(dict.fromkeys(t for t in texts if t not in self.cache))
        if missing:
            for text, vector in zip(missing, self.encoder.encode(missing)):
                self.cache[text] = vector
        return self.encoder.np.stack([self.cache[t] for t in texts])


def measure(index, cases):
    rows = []
    for question, expected in cases:
        start = perf_counter()
        r = index.answer(question)
        returned = r['citations'][0]['id'] if r['citations'] else None
        rows.append({'question': question, 'expected': expected, 'returned': returned,
                     'correct': returned == expected, 'semantic': r.get('semantic'),
                     'elapsed_ms': round((perf_counter()-start)*1000, 3)})
    positive = [r for r in rows if r['expected']]
    negative = [r for r in rows if not r['expected']]
    return {'correct': sum(r['correct'] for r in rows), 'total': len(rows),
            'supported_correct': sum(r['correct'] for r in positive), 'supported_total': len(positive),
            'false_accepts': sum(not r['correct'] for r in negative), 'unsupported_total': len(negative),
            'cases': rows}


if __name__ == '__main__':
    data = json.loads((ROOT/'data/semantic-cases.json').read_text(encoding='utf8'))
    lexical = Index.load()
    encoder = MemoEncoder(Encoder())
    dev = data['development']
    candidates = []
    for threshold in [.25, .30, .35, .40, .45, .50, .55, .60, .65, .70]:
        for margin in [.04, .08, .12]:
            index = SemanticIndex(lexical.documents, encoder, threshold, margin)
            report = measure(index, dev)
            candidates.append({'threshold': threshold, 'margin': margin,
                               'correct': report['correct'], 'false_accepts': report['false_accepts']})
    selected = max(candidates, key=lambda c: (-c['false_accepts'], c['correct'], c['threshold'], c['margin']))
    # Write the selected parameters before observing audit/real-source results.
    (ROOT/'data/semantic-settings.json').write_text(json.dumps(selected, indent=2), encoding='utf8')
    hybrid = SemanticIndex(lexical.documents, encoder, selected['threshold'], selected['margin'])
    golden = json.loads((ROOT/'data/evaluation.json').read_text(encoding='utf8'))['cases']
    reference = load_reference()
    ref_cases = json.loads((ROOT/'data/reference-cases.json').read_text(encoding='utf8'))['cases']
    r = {'date': '2026-10-14', 'model': MODEL, 'revision': REVISION, 'runtime': platform.platform(),
         'query_set_sha256': hashlib.sha256((ROOT/'data/semantic-cases.json').read_bytes()).hexdigest(),
         'selection': selected, 'development_grid': candidates,
         'limits': 'Author-written source-selection experiment, no independent reviewers. Second development iteration after inspecting first audit: audit is now a regression/transfer set, NOT an untouched holdout. Parameter selection still uses development cases only. Similarity is not entailment. Reference introductions may be outdated. CPU-only, no paid API.',
         'golden': measure(hybrid, [(c['question'],c['expected']) for c in golden]),
         'audit_lexical': measure(lexical, data['audit']), 'audit_hybrid': measure(hybrid, data['audit']),
         'reference_lexical': measure(reference, ref_cases),
         'reference_hybrid': measure(SemanticIndex(reference.documents, encoder, selected['threshold'], selected['margin']), ref_cases)}
    (ROOT/'reports/semantic-v05.json').write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k: {x:v for x,v in r[k].items() if x!='cases'} for k in ['golden','audit_lexical','audit_hybrid','reference_lexical','reference_hybrid']},indent=2))
    print('Selected on development only:', selected)
