import unittest
import requests
import json
import random
from datetime import date

class TestAPI(unittest.TestCase):

    def setUp(self):
        pass

    def test_create(self):
        priorities = ['high', 'medium', 'low']
        # create a task
        today = date.today().isoformat()
        payload = {
            'title': 'news',
            'description': 'check the news',
            'url': 'http://bbc.co.uk/news',
            'origin': 'head office',
            'tags': '#news #uk',
            'notbefore': today,
            'priority': priorities[random.randint(0, 2)]
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post('http://localhost:5001/tasks', data=json.dumps(payload), headers=headers)
        data = r.json()
        self.assertIs(('_id' in data), True)
        # retrieve the task
        id = data['_id']
        r = requests.get('http://localhost:5001/tasks/' + id)
        data = r.json()
        self.assertEqual(data['title'], 'news')
        self.assertEqual(data['description'], 'check the news')
        self.assertEqual(data['url'], 'http://bbc.co.uk/news')
        self.assertEqual(data['origin'], 'head office')
        self.assertIn('#news', data['tags'])
        self.assertIn('#uk', data['tags'])
        self.assertEqual(data['notbefore'], today)
        self.assertIn(data['priority'], priorities)
        self.assertEqual(data['status'], 'PENDING')

if __name__ == '__main__':
    unittest.main()
