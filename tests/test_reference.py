import hashlib
import json
import unittest
from unittest.mock import patch
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from evidence import Document, Index
from reference import load_reference
from semantic import missing_facets, SemanticIndex
import test_evidence


class ReferenceTests(unittest.TestCase):
    def test_reference_inventory_and_receipts(self):
        index = load_reference()
        self.assertEqual(len(index.documents), 34)
        for doc in index.documents:
            self.assertTrue(doc.source.startswith('https://fa.wikipedia.org/w/index.php?oldid='))
            receipt = index.receipt(doc)
            self.assertEqual(hashlib.sha256(doc.text.encode('utf8')).hexdigest(), receipt['text_sha256'])
            self.assertEqual(doc.text[receipt['start_char']:receipt['end_char']], doc.text)

    def test_reference_tampering_fails_closed(self):
        from pathlib import Path
        original = Path.read_bytes
        def corrupt(path):
            data = original(path)
            return data + b'x' if path.name == 'REF-DNS.txt' else data
        with patch.object(Path, 'read_bytes', corrupt), self.assertRaises(ValueError):
            load_reference()

    def test_public_fingerprint_does_not_include_restricted_document(self):
        public = Document('a','a','a','','public','a')
        secret = Document('b','b','secret','','staff','b')
        self.assertEqual(Index([public]).corpus_digest(), Index([public,secret]).corpus_digest())
        self.assertNotEqual(Index([public]).corpus_digest(), Index([public,secret]).corpus_digest('staff'))

    def test_unknown_opaque_identifier_cannot_match_a_related_topic(self):
        index=Index.load()
        self.assertEqual(index.search('VPN DR42'),[])
        self.assertEqual(index.search('VPN STAFF-001'),[])
        self.assertEqual(index.search('VPN certificate')[0]['id'],'IT-002')

    def test_facet_guards(self):
        self.assertTrue(missing_facets('قیمت خرید پرینتر چیست', 'برای چاپ کاغذ را بررسی کنید'))
        self.assertTrue(missing_facets('رمز مشترک کارکنان را بده', 'برای بازیابی رمز عبور درخواست ثبت کنید'))
        self.assertFalse(missing_facets('هزینه تماس چیست', 'تماس ممکن است هزینه داشته باشد'))

    def test_restricted_text_is_never_embedded(self):
        class Encoder:
            def encode(self, texts):
                self.texts = texts
                return []
        encoder = Encoder()
        SemanticIndex([Document('x','private','secret','','staff','x')],encoder)
        self.assertFalse(hasattr(encoder,'texts'))


class ReferenceHttpTests(unittest.TestCase):
    setUpClass = classmethod(test_evidence.ApiTests.setUpClass.__func__)
    tearDownClass = classmethod(test_evidence.ApiTests.tearDownClass.__func__)

    def test_reference_catalog_and_original_source(self):
        with build_opener(ProxyHandler({})).open(self.url+'/api/documents?collection=reference') as r:
            data = json.load(r)
        self.assertEqual(len(data['documents']),34)
        self.assertEqual(data['dataset'],'public-persian-reference/v2')
        self.assertTrue(data['corpus_sha256'])

    def test_unknown_collection_is_rejected(self):
        req = Request(self.url+'/api/ask',data=json.dumps({'question':'VPN','collection':'staff'}).encode(),headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as error:
            build_opener(ProxyHandler({})).open(req)
        self.assertEqual(error.exception.code,400)

    def test_source_hash_over_actual_http(self):
        req = Request(self.url+'/api/ask',data=json.dumps({'question':'فیشینگ چیست','collection':'reference'}).encode(),headers={'Content-Type':'application/json'})
        with build_opener(ProxyHandler({})).open(req) as r:
            data = json.load(r)
        self.assertEqual(data['citations'][0]['id'],'REF-PHISHING')
        self.assertEqual(hashlib.sha256(data['answer'].encode('utf8')).hexdigest(),data['citations'][0]['text_sha256'])
