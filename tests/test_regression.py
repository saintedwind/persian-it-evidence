import copy
import unittest
from evaluate import evaluate, regressions


class RegressionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evaluate()

    def test_existing_results_pass(self):
        self.assertEqual(regressions(self.report), [])

    def test_single_answer_regression_is_blocked(self):
        report = copy.deepcopy(self.report)
        report['cases'][0]['returned'] = None
        self.assertTrue(regressions(report))

    def test_missing_case_is_blocked(self):
        report = copy.deepcopy(self.report)
        report['cases'].pop(0)
        self.assertTrue(regressions(report))

    def test_unanswerable_false_positive_is_blocked(self):
        report = copy.deepcopy(self.report)
        next(r for r in report['cases'] if r['id'] == 'q19')['returned'] = 'IT-001'
        self.assertTrue(regressions(report))

    def test_known_failure_can_improve(self):
        report = copy.deepcopy(self.report)
        next(r for r in report['cases'] if r['id'] == 'q17')['returned'] = 'IT-004'
        self.assertEqual(regressions(report), [])

    def test_restricted_retrieval_is_blocked(self):
        report = copy.deepcopy(self.report)
        report['metrics']['restricted_document_leaks'] = 1
        self.assertTrue(regressions(report))
