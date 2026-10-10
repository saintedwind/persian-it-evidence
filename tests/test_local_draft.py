import json, os, unittest
from unittest.mock import patch
from evidence import Index
import local_draft as ld

class LocalDraftTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ, {'HANDBOOK_LOCAL_MODEL':'1'});self.env.start()
        self.addCleanup(self.env.stop);self.index=Index.load()
    def response(self, **updates):
        value={'steps':[1], 'source_id':'IT-004', 'supported':True};value.update(updates)
        return {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(value)}}], 'usage':{'completion_tokens':30}}
    def test_exact_source_selection(self):
        with patch.object(ld,'request_model',return_value=self.response()) as call:
            result=ld.draft(self.index,'صف چاپ پرینتر')
        self.assertEqual(result['status'],'draft_ready')
        self.assertIn(result['draft'],result['citations'][0]['excerpt'])
        self.assertEqual(call.call_args.args[1]['id'],'IT-004')
    def test_unknown_never_calls_model(self):
        with patch.object(ld,'request_model') as call:
            self.assertEqual(ld.draft(self.index,'quasar astronomy')['status'],'insufficient_evidence')
            call.assert_not_called()
    def test_staff_never_calls_model(self):
        with patch.object(ld,'request_model') as call:
            self.assertEqual(ld.draft(self.index,'اطلس DR42')['status'],'insufficient_evidence')
            call.assert_not_called()
    def test_invalid_selections_rejected(self):
        for updates in [{'steps':[999]},{'steps':[True]},{'steps':[1,1]},{'steps':[]},{'source_id':'STAFF-001'},{'steps':'1'}]:
            with self.subTest(updates=updates),patch.object(ld,'request_model',return_value=self.response(**updates)):
                self.assertEqual(ld.draft(self.index,'صف چاپ پرینتر')['status'],'invalid_output')
    def test_failure_returns_no_draft(self):
        with patch.object(ld,'request_model',side_effect=TimeoutError()):
            self.assertIsNone(ld.draft(self.index,'صف چاپ پرینتر')['draft'])
    def test_disabled_never_calls_model(self):
        with patch.dict(os.environ,{'HANDBOOK_LOCAL_MODEL':'0'}),patch.object(ld,'request_model') as call:
            self.assertEqual(ld.draft(self.index,'صف چاپ پرینتر')['status'],'unavailable');call.assert_not_called()
    def test_output_budget_truncation_rejected(self):
        r=self.response();r['choices'][0]['finish_reason']='length'
        with patch.object(ld,'request_model',return_value=r):
            self.assertEqual(ld.draft(self.index,'صف چاپ پرینتر')['status'],'incomplete')
    def test_bounded_question(self):
        for q in ['',None,'x'*401]:
            with self.assertRaises(ValueError):ld.draft(self.index,q)
    def test_busy_skips_call(self):
        ld.LOCK.acquire()
        try:
            with patch.object(ld,'request_model') as call:
                self.assertEqual(ld.draft(self.index,'صف چاپ پرینتر')['status'],'busy');call.assert_not_called()
        finally:ld.LOCK.release()
