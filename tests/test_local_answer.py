import json
import unittest
from unittest.mock import patch
from reference import load_reference
import local_answer


class LocalAnswerTests(unittest.TestCase):
    def setUp(self):
        self.index=load_reference()
        self.question='باج‌افزار چیست؟'
        self.doc=self.index.answer(self.question)['citations'][0]

    def response(self, **changes):
        value={'answer':'باج‌افزار دسترسی به سامانه را محدود می‌کند.','source_id':self.doc['id'],
               'supported':True,'quote':self.doc['excerpt'][:100]}
        value.update(changes)
        return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}],
                'usage':{'prompt_tokens':50,'completion_tokens':25,'total_tokens':75}}

    def test_no_inference_without_evidence(self):
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}), patch('local_answer.request_model') as model:
            result=local_answer.answer(self.index,'قیمت بلیت کنسرت فردا چقدر است؟')
        self.assertEqual(result['status'],'insufficient_evidence');model.assert_not_called()

    def test_disabled_model_leaves_retrieval_available(self):
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'0'}), patch('local_answer.request_model') as model:
            result=local_answer.answer(self.index,self.question)
        self.assertEqual(result['status'],'unavailable');self.assertTrue(result['citations']);model.assert_not_called()

    def test_source_exact_quote_is_accepted(self):
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}), patch('local_answer.request_model',return_value=self.response()):
            result=local_answer.answer(self.index,self.question)
        self.assertEqual(result['status'],'answer_ready')
        self.assertIn(result['quote'],self.doc['excerpt'])
        self.assertEqual(result['usage']['total_tokens'],75)

    def test_fabricated_quote_or_source_is_not_displayed(self):
        for changes in [{'quote':'متن ساختگی که در هیچ‌کدام از اسناد پروژه وجود ندارد.'},{'source_id':'REF-MISSING'},{'supported':'true'}]:
            with self.subTest(changes=changes), patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}), patch('local_answer.request_model',return_value=self.response(**changes)):
                result=local_answer.answer(self.index,self.question)
            self.assertEqual(result['status'],'invalid_output');self.assertIsNone(result['answer'])

    def test_incomplete_or_offline_model_never_falls_back_to_fake_answer(self):
        value=self.response();value['choices'][0]['finish_reason']='length'
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}), patch('local_answer.request_model',return_value=value):
            self.assertEqual(local_answer.answer(self.index,self.question)['status'],'incomplete')
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}), patch('local_answer.request_model',side_effect=OSError):
            self.assertEqual(local_answer.answer(self.index,self.question)['status'],'unavailable')
        self.assertTrue(local_answer.LOCK.acquire(blocking=False));local_answer.LOCK.release()

    def test_remote_endpoint_is_rejected(self):
        with patch.dict('os.environ',{'HANDBOOK_ANSWER_ENDPOINT':'https://example.com/v1/chat/completions'}):
            with self.assertRaises(ValueError):local_answer.request_model('q',{})
