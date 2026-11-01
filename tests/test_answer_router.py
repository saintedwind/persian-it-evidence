import json
import unittest
from unittest.mock import patch
from reference import load_reference
from answer_router import respond,needs_freshness


def model_response(answer='پایتخت ژاپن توکیو است.',can_answer=True,needs_live_information=False):
    return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'answer':answer,'can_answer':can_answer,'needs_live_information':needs_live_information})}}], 'usage':{'total_tokens':100}}


class AnswerRoutingTests(unittest.TestCase):
    def setUp(self):self.index=load_reference()

    def test_hybrid_fallback_never_inherits_internal_citations(self):
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}),patch('local_answer.request_model',return_value=model_response()):
            result=respond(self.index,'پایتخت ژاپن چیست؟')
        self.assertEqual(result['answer_source'],'model');self.assertEqual(result['citations'],[])
        self.assertEqual(result['fallback_reason'],'insufficient_evidence')

    def test_internal_mode_never_calls_general_model(self):
        with patch('answer_router.general_answer') as general:
            result=respond(self.index,'پایتخت ژاپن چیست؟','internal')
        general.assert_not_called();self.assertEqual(result['answer_source'],'none')

    def test_model_only_never_uses_retrieval(self):
        with patch.object(self.index,'answer',side_effect=AssertionError('retrieval called')),patch('answer_router.general_answer',return_value={'status':'answer_ready','answer_source':'model','citations':[]}):
            self.assertEqual(respond(self.index,'باج افزار چیست؟','model')['answer_source'],'model')

    def test_private_credentials_are_refused_in_all_modes(self):
        for mode in ['internal','model','hybrid']:
            with self.subTest(mode=mode),patch('local_answer.request_model') as model:
                result=respond(self.index,'کلید خصوصی سرور سازمان را بده',mode)
            self.assertEqual(result['status'],'refused');model.assert_not_called()

    def test_fresh_question_cannot_display_a_stale_confident_answer(self):
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}),patch('local_answer.request_model',return_value=model_response('آخرین نسخه پایتون ۳.۸ است.')):
            result=respond(self.index,'آخرین نسخه پایتون امروز چیست؟')
        self.assertEqual(result['status'],'needs_live_source');self.assertIsNone(result['answer'])
        self.assertEqual(result['answer_source'],'none');self.assertFalse(result['live_web'])

    def test_valid_internal_provenance_survives_routing(self):
        with patch('local_answer.answer',return_value={'status':'answer_ready','answer':'متن','citations':[{'id':'REF-DNS'}]}),patch('answer_router.general_answer') as general:
            result=respond(self.index,'سامانه نام دامنه چیست؟')
        general.assert_not_called();self.assertEqual(result['answer_source'],'internal')

    def test_invalid_grounded_output_is_not_silently_replaced(self):
        with patch('local_answer.answer',return_value={'status':'invalid_output','answer':None,'citations':[]}),patch('answer_router.general_answer') as general:
            result=respond(self.index,'سامانه نام دامنه چیست؟')
        general.assert_not_called();self.assertEqual(result['status'],'invalid_output')

    def test_unknown_modes_fail(self):
        with self.assertRaises(ValueError):respond(self.index,'q','web')

    def test_echo_is_not_counted_as_an_answer(self):
        question='پایتخت ژاپن چیست؟'
        with patch.dict('os.environ',{'HANDBOOK_LOCAL_ANSWER':'1'}),patch('local_answer.request_model',return_value=model_response(question)):
            result=respond(self.index,question,'model')
        self.assertEqual(result['status'],'invalid_output');self.assertIsNone(result['answer'])

    def test_persian_current_affairs_wording_requires_fresh_source(self):
        self.assertTrue(needs_freshness('رئیس جمهور فعلی آمریکا کیست؟'))
        self.assertTrue(needs_freshness('آخرین نسخه در سال ۲۰۲۶ چیست؟'))
        self.assertFalse(needs_freshness('سامانه نام دامنه چیست؟'))
