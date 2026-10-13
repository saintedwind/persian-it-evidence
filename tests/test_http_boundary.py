import json
import unittest
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError
from unittest.mock import patch
import test_evidence


class HttpBoundaryTests(unittest.TestCase):
    setUpClass = classmethod(test_evidence.ApiTests.setUpClass.__func__)
    tearDownClass = classmethod(test_evidence.ApiTests.tearDownClass.__func__)

    def request(self, headers):
        req = Request(self.url + '/api/draft', data=json.dumps({'question':'VPN'}).encode(),
                      headers={'Content-Type':'application/json', **headers})
        return build_opener(ProxyHandler({})).open(req, timeout=3)

    def test_foreign_origin_cannot_invoke_model(self):
        with patch('server.draft') as call, self.assertRaises(HTTPError) as error:
            self.request({'Origin':'https://unrelated.example'})
        self.assertEqual(error.exception.code, 403)
        call.assert_not_called()

    def test_foreign_host_cannot_invoke_model(self):
        with patch('server.draft') as call, self.assertRaises(HTTPError) as error:
            self.request({'Host':'unrelated.example'})
        self.assertEqual(error.exception.code, 403)
        call.assert_not_called()

    def test_plain_text_cannot_invoke_model(self):
        with patch('server.draft') as call, self.assertRaises(HTTPError) as error:
            self.request({'Content-Type':'text/plain'})
        self.assertEqual(error.exception.code, 415)
        call.assert_not_called()

    def test_same_origin_still_works(self):
        with patch('server.draft', return_value={'status':'busy'}) as call:
            with self.request({'Origin':self.url}) as response:
                self.assertEqual(json.load(response)['status'], 'busy')
        call.assert_called_once()

    def test_chunked_body_rejected(self):
        with patch('server.draft') as call, self.assertRaises(HTTPError) as error:
            self.request({'Transfer-Encoding':'chunked'})
        self.assertEqual(error.exception.code, 400)
        call.assert_not_called()
