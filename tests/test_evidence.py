import json
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from evidence import Document, Index, normalize, tokens
from server import Handler


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.index = Index.load()

    def test_persian_variants(self):
        self.assertEqual(normalize('كِتاب يک'), normalize('کتاب یک'))

    def test_zwnj(self):
        self.assertEqual(tokens('وای‌فای'), tokens('وای فای'))

    def test_exact_topic(self):
        self.assertEqual(self.index.search('VPN certificate')[0]['id'], 'IT-002')

    def test_unknown_abstains(self):
        self.assertEqual(self.index.answer('quasar astronomy')['status'], 'insufficient_evidence')

    def test_private_absent_from_public(self):
        self.assertEqual(self.index.search('اطلس DR42'), [])

    def test_trusted_staff_scope(self):
        self.assertEqual(self.index.search('اطلس DR42', 'staff')[0]['id'], 'STAFF-001')

    def test_invalid_inputs(self):
        for value in ['', ' ', None, 13, 'x' * 2001]:
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                self.index.answer(value)

    def test_invalid_scope(self):
        with self.assertRaises(ValueError):
            self.index.search('VPN', 'admin')

    def test_source_text_is_exact(self):
        result = self.index.answer('صف چاپ پرینتر')
        self.assertEqual(result['answer'], result['citations'][0]['excerpt'])

    def test_duplicate_ids_rejected(self):
        d = Document('x', 'x', 'x', 'x', 'public', 'x')
        with self.assertRaises(ValueError):
            Index([d, d])

    def test_stable_ranking(self):
        self.assertEqual(self.index.search('رمز عبور'), self.index.search('رمز عبور'))

    def test_empty_index(self):
        self.assertEqual(Index([]).answer('VPN')['citations'], [])


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, payload):
        return urlopen(Request(self.url + '/api/ask', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'}), timeout=3)

    def test_health(self):
        with urlopen(self.url + '/health') as response:
            self.assertEqual(json.load(response)['status'], 'ok')

    def test_answer(self):
        with self.post({'question':'VPN گواهی'}) as response:
            self.assertEqual(json.load(response)['citations'][0]['id'], 'IT-002')

    def test_reject_caller_scope(self):
        with self.assertRaises(HTTPError) as ctx:
            self.post({'question':'اطلس', 'scope':'staff'})
        self.assertEqual(ctx.exception.code, 400)

    def test_invalid_body(self):
        with self.assertRaises(HTTPError) as ctx:
            self.post(['VPN'])
        self.assertEqual(ctx.exception.code, 400)

    def test_no_file_traversal(self):
        with self.assertRaises(HTTPError) as ctx:
            urlopen(self.url + '/../data/documents.json')
        self.assertEqual(ctx.exception.code, 404)

    def test_ui_and_headers(self):
        with urlopen(self.url) as response:
            self.assertIn('frame-ancestors', response.headers['Content-Security-Policy'])
            self.assertIn(b'id="question"', response.read())

    def test_catalog_has_public_documents_only(self):
        with urlopen(self.url + '/api/documents') as response:
            docs = json.load(response)['documents']
        self.assertEqual(len(docs), 12)
        self.assertTrue(all(not d['id'].startswith('STAFF') for d in docs))

    def test_catalog_does_not_trust_scope_query(self):
        with urlopen(self.url + '/api/documents?scope=staff') as response:
            self.assertNotIn('STAFF-001', response.read().decode())

    def test_public_document_can_be_read(self):
        with urlopen(self.url + '/api/documents?id=IT-004') as response:
            self.assertEqual(json.load(response)['id'], 'IT-004')

    def test_private_document_cannot_be_read_directly(self):
        for doc_id in ['STAFF-001', 'does-not-exist', '..%2Fdata%2Fdocuments.json']:
            with self.subTest(doc_id=doc_id), self.assertRaises(HTTPError) as ctx:
                urlopen(self.url + '/api/documents?id=' + doc_id)
            self.assertEqual(ctx.exception.code, 404)

    def test_local_font_is_valid_woff2(self):
        with urlopen(self.url + '/Gandom.woff2') as response:
            self.assertEqual(response.headers['Content-Type'], 'font/woff2')
            self.assertEqual(response.read(4), b'wOF2')


if __name__ == '__main__':
    unittest.main()
