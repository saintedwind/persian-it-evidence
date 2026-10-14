"""Actual loopback HTTP checks with real multilingual CPU inference."""
import hashlib
import json
import os
import threading
from urllib.request import Request, build_opener, ProxyHandler
from evidence import ROOT


def run():
    os.environ['HANDBOOK_RETRIEVER'] = 'hybrid'
    from server import LocalServer, Handler, get_index
    get_index('sample')
    get_index('reference')
    reports = {}
    opener = build_opener(ProxyHandler({}))
    server = LocalServer(('127.0.0.1',0),Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        for group,collection in [('golden','sample'),('audit','sample'),('reference','reference')]:
            if group=='golden':
                cases=[(r['question'],r['expected']) for r in json.loads((ROOT/'data/evaluation.json').read_text(encoding='utf8'))['cases']]
            else:
                file='semantic-cases.json' if group=='audit' else 'reference-cases.json'
                cases=json.loads((ROOT/'data'/file).read_text(encoding='utf8'))['audit' if group=='audit' else 'cases']
            rows=[]
            for question,expected in cases:
                req=Request(f'http://127.0.0.1:{server.server_port}/api/ask',data=json.dumps({'question':question,'collection':collection}).encode(),headers={'Content-Type':'application/json'})
                with opener.open(req,timeout=15) as response:
                    answer=json.load(response)
                returned=answer['citations'][0]['id'] if answer['citations'] else None
                for citation in answer['citations']:
                    assert hashlib.sha256(citation['excerpt'].encode('utf8')).hexdigest()==citation['text_sha256']
                    assert citation['end_char']==len(citation['excerpt'])
                    assert not citation['id'].startswith('STAFF')
                rows.append({'question':question,'expected':expected,'returned':returned,'correct':returned==expected})
            reports[group]={'correct':sum(r['correct'] for r in rows),'total':len(rows),'cases':rows}
        reports['receipt_checks']='All returned source text hashes, character bounds and public scope reconciled over actual HTTP.'
        reports['model']='Actual pinned multilingual MiniLM ONNX CPU; no mocks or paid API.'
        (ROOT/'reports/live-semantic-v05.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf8')
        print(json.dumps({k:{'correct':v['correct'],'total':v['total']} for k,v in reports.items() if isinstance(v,dict)},indent=2))
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)


if __name__=='__main__':
    run()
