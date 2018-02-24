import unittest
import json
from ruleset import RuleSet

class TestRuleSet(unittest.TestCase):

    def setUp(self):
        pass

    def test_ruleset(self):
        with open('people.json') as f1:
            people_data = json.load(f1)
        results = list()
        for person in people_data['people']:
            with open('rules.json') as f2:
                rules_data = json.load(f2)
            rs = RuleSet(rules_data)
            results.append(rs.evaluate(person))
        for result in results:
            if result['name'] == 'FRED':
                self.assertEqual(result['status'], 'COOL')
            elif result['name'] == 'GINGER':
                self.assertEqual(result['status'], 'OLD')
            elif result['name'] == 'SID':
                self.assertEqual(result['status'], 'ANCIENT')
            elif result['name'] == 'NANCY':
                self.assertEqual(result['status'], 'VERY OLD')
            elif result['name'] == 'JOE':
                self.assertEqual(result['status'], 'YOUNG')
            elif result['name'] == 'FLO':
                self.assertEqual(result['status'], 'VERY OLD')

if __name__ == '__main__':
    unittest.main()
