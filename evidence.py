"""Dependency-free, Persian-aware retrieval baseline. No generative model."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
STOP = set('از به در با برای و یا که را یک این آن است هست چه چگونه چرا می من the a an is are to of for and how do does my'.split())


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKC', text).lower()
    text = text.translate(str.maketrans('يكۀؤإأ', 'یکهواا'))
    text = re.sub(r'[\u064b-\u065f\u0670\u0640]', '', text)
    return re.sub(r'\s+', ' ', text.replace('\u200c', ' ')).strip()


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r'[^\W_]+', normalize(text), re.UNICODE) if w not in STOP]


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    tags: str
    scope: str
    source: str


class Index:
    """BM25 scores only documents admitted by a trusted server-side scope."""
    def __init__(self, documents: list[Document]):
        if len({d.id for d in documents}) != len(documents):
            raise ValueError('Document IDs must be unique')
        self.documents = documents

    @classmethod
    def load(cls, path: Path = ROOT / 'data/documents.json') -> Index:
        rows = json.loads(path.read_text(encoding='utf-8'))
        return cls([Document(**row) for row in rows])

    def search(self, question: str, scope: str = 'public', limit: int = 3) -> list[dict]:
        if not isinstance(question, str) or not question.strip() or len(question) > 2000:
            raise ValueError('question must contain 1–2000 characters')
        if scope not in {'public', 'staff'}:
            raise ValueError('Unknown scope')
        if not isinstance(limit, int) or not 1 <= limit <= 10:
            raise ValueError('limit must be between 1 and 10')
        docs = [d for d in self.documents if d.scope == 'public' or scope == 'staff']
        query = set(tokens(question))
        if not query or not docs:
            return []
        bags = [Counter(tokens(f'{d.title} {d.title} {d.tags} {d.text}')) for d in docs]
        avg = sum(sum(b.values()) for b in bags) / len(bags) or 1
        df = Counter(t for bag in bags for t in bag)
        rows = []
        for doc, bag in zip(docs, bags):
            score = 0.0
            length = sum(bag.values())
            for t in query & bag.keys():
                idf = math.log(1 + (len(docs) - df[t] + .5) / (df[t] + .5))
                tf = bag[t]
                score += idf * tf * 2.5 / (tf + 1.5 * (.25 + .75 * length / avg))
            if score:
                rows.append({'id': doc.id, 'title': doc.title, 'score': round(score, 6),
                             'coverage': len(query & bag.keys()) / len(query),
                             'excerpt': doc.text, 'source': doc.source})
        return sorted(rows, key=lambda r: (-r['score'], r['id']))[:limit]

    def answer(self, question: str, scope: str = 'public') -> dict:
        hits = self.search(question, scope)
        # Development heuristic, not calibrated probability of correctness.
        accepted = bool(hits and hits[0]['coverage'] >= .45)
        sources = hits[:1] if accepted else []
        return {'mode': 'extractive-bm25', 'status': 'evidence_found' if accepted else 'insufficient_evidence',
                'answer': sources[0]['excerpt'] if accepted else 'در منابع مجاز، شواهد کافی پیدا نشد.',
                'citations': sources, 'retrieved': hits,
                'notice': 'Synthetic demo documents; excerpts are evidence, not a verified answer.'}


if __name__ == '__main__':
    import argparse
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question')
    parser.add_argument('--scope', choices=['public', 'staff'], default='public')
    args = parser.parse_args()
    print(json.dumps(Index.load().answer(args.question, args.scope), ensure_ascii=False, indent=2))
