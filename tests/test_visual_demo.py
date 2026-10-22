import hashlib
import json
import unittest
from urllib.request import Request, build_opener, ProxyHandler
import test_evidence


class VisualDemoTests(unittest.TestCase):
    setUpClass = classmethod(test_evidence.ApiTests.setUpClass.__func__)
    tearDownClass = classmethod(test_evidence.ApiTests.tearDownClass.__func__)

    def test_demo_assets_use_existing_local_security_boundary(self):
        opener = build_opener(ProxyHandler({}))
        for route, mime in [('/demo', 'text/html'), ('/demo.js', 'application/javascript'), ('/demo.css', 'text/css')]:
            with self.subTest(route=route), opener.open(self.url + route, timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(mime, response.headers['Content-Type'])
                self.assertIn("default-src 'self'", response.headers['Content-Security-Policy'])
                self.assertGreater(len(response.read()), 100)

    def test_reference_answer_is_source_exact_with_valid_receipt(self):
        opener = build_opener(ProxyHandler({}))
        request = Request(self.url + '/api/ask', data=json.dumps({'question':'سامانه نام دامنه چیست؟', 'collection':'reference'}).encode(), headers={'Content-Type':'application/json'})
        with opener.open(request, timeout=3) as response:
            answer = json.load(response)
        self.assertEqual(answer['status'], 'evidence_found')
        citation = answer['citations'][0]
        self.assertEqual(citation['id'], 'REF-DNS')
        self.assertEqual(hashlib.sha256(answer['answer'].encode('utf-8')).hexdigest(), citation['text_sha256'])
        with opener.open(self.url + '/api/documents?collection=reference&id=REF-DNS', timeout=3) as response:
            document = json.load(response)
        self.assertEqual(answer['answer'], document['text'])
