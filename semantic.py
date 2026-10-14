"""Optional, local CPU retrieval experiment. Never generates answer text."""
from __future__ import annotations
import hashlib
from pathlib import Path
import threading
import re
from evidence import Index, ROOT, normalize, tokens, identifiers

MODEL = 'Qdrant/paraphrase-multilingual-MiniLM-L12-v2-onnx-Q'
REVISION = 'faf4aa4225822f3bc6376869cb1164e8e3feedd0'
FILES = {
    'model_optimized.onnx': '634d0f66c29dc934c8fa72b8a4fe91dd4d420a22f1d82a241058d4316e659a99',
    'tokenizer.json': 'fa685fc160bbdbab64058d4fc91b60e62d207e8dc60b9af5c002c5ab946ded00',
}


class Encoder:
    def __init__(self, directory=ROOT / '.runtime/multilingual'):
        import onnxruntime as ort
        from tokenizers import Tokenizer
        self.np = __import__('numpy')
        directory = Path(directory)
        for name, digest in FILES.items():
            with (directory / name).open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                    raise ValueError('Embedding file digest mismatch: ' + name)
        self.tokenizer = Tokenizer.from_file(str(directory / 'tokenizer.json'))
        self.tokenizer.enable_truncation(max_length=128)
        self.tokenizer.enable_padding(pad_id=1, pad_token='<pad>')
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(directory / 'model_optimized.onnx'), options,
                                           providers=['CPUExecutionProvider'])
        self.lock = threading.Lock()

    def encode(self, texts):
        np = self.np
        with self.lock:
            encoded = self.tokenizer.encode_batch(texts)
            ids = np.array([e.ids for e in encoded], dtype=np.int64)
            mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
            values = {'input_ids': ids, 'attention_mask': mask, 'token_type_ids': np.zeros_like(ids)}
            inputs = {i.name: values[i.name] for i in self.session.get_inputs()}
            output = self.session.run(None, inputs)[0]
        pooled = ((output * mask[:, :, None]).sum(1) / mask.sum(1)[:, None]
                  if output.ndim == 3 else output)
        norms = np.linalg.norm(pooled, axis=1, keepdims=True)
        if not np.isfinite(pooled).all() or (norms <= 0).any():
            raise ValueError('Invalid embedding')
        return pooled / norms


def missing_facets(question, text):
    """Narrow literal guard for requested data not supplied by a procedure.

    This is not a general entailment, confidentiality or injection classifier.
    """
    q, body = normalize(question), set(tokens(text))
    monetary = {'قیمت', 'هزینه', 'اقساطی', 'اقساط', 'اشتراک', 'حقوق', 'بودجه', 'دستمزد', 'وام'}
    missing = set(tokens(q)) & monetary - body
    if re.search(r'(رمز|پسورد|گذرواژه).*(همه|مشترک|کارکنان|سرور)', q) or re.search(r'(همه|مشترک).*(رمز|پسورد|گذرواژه)', q):
        missing.add('credential_value')
    if re.search(r'(شماره|ادرس|آدرس).*(مدیر|مسئول|شخصی)', q):
        missing.add('private_contact')
    return sorted(missing)


class SemanticIndex(Index):
    """Rescue lexical abstentions only; preserve the existing baseline decisions.

    Similarity and runner-up margin are heuristics, not answer confidence.
    Restricted documents are excluded before embedding as well as ranking.
    """
    def __init__(self, documents, encoder, threshold=.55, margin=.08, dataset='synthetic-runbooks/v1'):
        super().__init__(documents, dataset)
        self.encoder, self.threshold, self.margin = encoder, threshold, margin
        self.public = [d for d in documents if d.scope == 'public']
        self.vectors = encoder.encode([d.title + '\n' + d.text for d in self.public]) if self.public else None

    def answer(self, question, scope='public'):
        result = super().answer(question, scope)
        result['semantic'] = {'status': 'not_needed', 'model': MODEL, 'revision': REVISION}
        if result['status'] == 'evidence_found' or scope != 'public' or self.vectors is None:
            return result
        scores = (self.vectors @ self.encoder.encode([question])[0]).tolist()
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], self.public[i].id))
        first = order[0]
        gap = scores[first] - (scores[order[1]] if len(order) > 1 else 0)
        missing = missing_facets(question, self.public[first].text)
        missing += sorted(identifiers(question) - identifiers(self.public[first].id+' '+self.public[first].text))
        accepted = scores[first] >= self.threshold and gap >= self.margin and not missing
        result['semantic'].update(status='accepted' if accepted else 'abstained',
                                  similarity=round(scores[first], 6), margin=round(gap, 6),
                                  threshold=self.threshold, required_margin=self.margin,
                                  missing_facets=missing, candidate_id=self.public[first].id)
        if accepted:
            doc = self.public[first]
            hit = {'id': doc.id, 'title': doc.title, 'excerpt': doc.text, 'source': doc.source,
                   'score': round(scores[first], 6), 'coverage': None,
                   **self.receipt(doc)}
            result.update(mode='lexical-with-semantic-rescue', status='evidence_found',
                          answer=doc.text, citations=[hit], retrieved=[hit])
        return result
