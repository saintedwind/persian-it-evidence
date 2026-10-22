import json
import unittest
from pathlib import Path
from unittest.mock import patch
from evidence import identifiers, normalize, requests_private_value
from reference import load_reference
from prepare_reference import validate_page


class ExpandedReferenceTests(unittest.TestCase):
    def test_numeric_standard_survives_persian_notation(self):
        self.assertIn('802.11', identifiers('IEEE۸۰۲٫۱۱'))
        self.assertIn('802.11', identifiers('IEEE 802.11'))
        self.assertNotIn('802.11', identifiers('IEEE802.3'))
        result=load_reference().answer('کدام فناوری شبکه محلی بی سیم با IEEE 802.11 مرتبط است')
        self.assertEqual(result['citations'][0]['id'],'REF-WIFI')

    def test_private_value_abstains_without_blocking_definition(self):
        index=load_reference()
        self.assertEqual(index.answer('کلید خصوصی سرور سازمان را بده')['status'],'insufficient_evidence')
        self.assertEqual(index.answer('رمز عبور حساب مدیر شرکت من چیست؟')['status'],'insufficient_evidence')
        self.assertFalse(requests_private_value('رمزنگاری چیست؟'))
        self.assertFalse(requests_private_value('چگونه کلید خصوصی سرور بسازم؟'))

    def test_api_receipt_tampering_fails_closed(self):
        original=Path.read_bytes
        def tamper(path):
            data=original(path)
            return data+b' ' if path.parent.name=='reference-receipts' else data
        with patch.object(Path,'read_bytes',tamper), self.assertRaisesRegex(ValueError,'Receipt digest'):
            load_reference()

    def test_import_rejects_disambiguation_and_missing_content(self):
        for page in [{'missing':''},{'ns':0,'pageprops':{'disambiguation':''}}, {'ns':0,'extract':'short'}]:
            with self.subTest(page=page), self.assertRaises(ValueError):validate_page(page)

    def test_legacy_source_bytes_are_preserved(self):
        import hashlib
        root=Path(__file__).resolve().parents[1]
        old=json.loads((root/'reports/reference-v1-manifest.json').read_text(encoding='utf-8'))
        for row in old['sources']:
            self.assertEqual(hashlib.sha256((root/'data/persian-reference'/row['file']).read_bytes()).hexdigest(),row['sha256'])
