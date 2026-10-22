"""Record expanded-corpus development results without replacing historical evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from reference import load_reference

ROOT=Path(__file__).resolve().parent


def evaluate(index, cases):
    rows=[]
    for case in cases:
        response=index.answer(case['question'])
        actual=response['citations'][0]['id'] if response['citations'] else None
        rows.append({**case,'actual':actual,'correct':actual==case['expected'],
                     'status':response['status'],'retrieved':[r['id'] for r in response['retrieved']]})
    return {'passed':sum(r['correct'] for r in rows),'total':len(rows),'cases':rows}


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Select a new evidence output path')
    index=load_reference()
    new_path=ROOT/'data/reference-expansion-cases.json'
    old_path=ROOT/'data/reference-cases.json'
    new=json.loads(new_path.read_text(encoding='utf-8'))['cases']
    old=[{'id':f'legacy-{i+1}','question':question,'expected':expected} for i,(question,expected) in enumerate(json.loads(old_path.read_text(encoding='utf-8'))['cases'])]
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'dataset':index.dataset,
            'corpus_sha256':index.corpus_digest(),'documents':len(index.documents),
            'scope':'Authored development source-selection/abstention probes, not blind user testing or factual verification',
            'cases_sha256':hashlib.sha256(new_path.read_bytes()).hexdigest(),
            'expansion':evaluate(index,new),'legacy':evaluate(index,old)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:{'passed':report[k]['passed'],'total':report[k]['total']} for k in ['expansion','legacy']}))


if __name__=='__main__':main()
