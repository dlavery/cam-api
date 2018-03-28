import unittest
import requests
import json
import random
import configparser
import pymongo
from models import Task
from pymongo import MongoClient
from datetime import date
from datetime import timedelta
from loadrules import loadrules
from queuetask import queue

class TestAPI(unittest.TestCase):

    def setUp(self):
        loadrules()
        config = configparser.ConfigParser()
        config.read('cam-api.cfg')
        client = MongoClient(config['DATABASE']['dbURI'])
        self.db = client[config['DATABASE']['dbName']]
        self.db.tasks.delete_many({})
        self.priorities = ['high', 'medium', 'low']

    def tearDown(self):
        self.db.tasks.delete_many({})

    def _create_task(self, payload):
        r = requests.post('http://localhost:5001/tasks', data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        return r.json()

    def test_queues(self):
        r = requests.get('http://localhost:5001/queues')
        data = r.json()
        r = data['queues']
        self.assertEqual(True, all([e in r for e in ['General', 'NewsTeam', 'SportsTeam']]))

    def test_create(self):
        # create a task
        today = date.today().isoformat()
        payload = {
            'title': 'news',
            'description': 'check the news',
            'url': 'http://bbc.co.uk/news',
            'requester': 'head office',
            'tags': ['#news', '#uk'],
            'notbefore': today,
            'priority': self.priorities[random.randint(0, 2)]
        }
        data = self._create_task(payload)
        self.assertIs(('_id' in data), True)
        # retrieve the task
        id = data['_id']
        r = requests.get('http://localhost:5001/tasks/' + id)
        data = r.json()
        self.assertEqual(data['title'], 'news')
        self.assertEqual(data['description'], 'check the news')
        self.assertEqual(data['url'], 'http://bbc.co.uk/news')
        self.assertEqual(data['requester'], 'head office')
        self.assertIn('#news', data['tags'])
        self.assertIn('#uk', data['tags'])
        self.assertEqual(data['notbefore'], today)
        self.assertIn(data['priority'], self.priorities)
        self.assertEqual(data['status'], 'PENDING')

    def test_queue(self):
        # create a task
        today = date.today().isoformat()
        payload = {
            'title': 'news',
            'description': 'check the news',
            'url': 'http://bbc.co.uk/news',
            'requester': 'head office',
            'tags': ['#news', '#uk'],
            'notbefore': today,
            'priority': self.priorities[random.randint(0, 2)]
        }
        data = self._create_task(payload)
        # run queueing to set up the test
        r = queue(self.db)
        # do test
        r = requests.get('http://localhost:5001/queues/NewsTeam/1')
        data = r.json()
        t = ('tasks' in data)
        self.assertEqual(t, True)
        docs = data['tasks']
        self.assertEqual(len(docs), 1)
        data = docs[0]
        self.assertEqual(data['title'], 'news')
        self.assertEqual(data['description'], 'check the news')
        self.assertEqual(data['url'], 'http://bbc.co.uk/news')
        self.assertEqual(data['requester'], 'head office')
        self.assertIn('#news', data['tags'])
        self.assertIn('#uk', data['tags'])
        self.assertEqual(data['status'], 'PROGRESS')

    def test_requeue(self):
        # create a task
        today = date.today().isoformat()
        payload = {
            'title': 'news',
            'description': 'check the news',
            'url': 'http://bbc.co.uk/news',
            'requester': 'head office',
            'tags': ['#news', '#uk'],
            'notbefore': today,
            'priority': self.priorities[random.randint(0, 2)]
        }
        data = self._create_task(payload)
        # run queueing to set up the test
        r = queue(self.db)
        # do test
        doc = self.db.tasks.find_one({})
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        payload = {
            'updater': 'jane smith',
            'notbefore': tomorrow,
            'note': 'Never do today what you can put off until tomorrow'
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.put('http://localhost:5001/tasks/requeue/' + str(doc['_id']), data=json.dumps(payload), headers=headers)
        data = r.json()
        self.assertEqual(data['updated'], 1)
        doc = self.db.tasks.find_one({})
        self.assertEqual(doc['notbefore'], tomorrow)
        self.assertEqual(doc['updater'], 'jane smith')
        self.assertEqual(doc['notes'][0]['originator'], 'jane smith')
        self.assertEqual(doc['notes'][0]['text'], 'Never do today what you can put off until tomorrow')
        self.assertEqual(doc['notes'][0]['ondate'], today)

    def test_complete(self):
        # create a task
        today = date.today().isoformat()
        payload = {
            'title': 'news',
            'description': 'check the news',
            'url': 'http://bbc.co.uk/news',
            'requester': 'head office',
            'tags': ['#news', '#uk'],
            'notbefore': today,
            'priority': self.priorities[random.randint(0, 2)]
        }
        data = self._create_task(payload)
        # run queueing to set up the test
        r = queue(self.db)
        # do test
        doc = self.db.tasks.find_one({})
        payload = {
            'updater': 'jane smith'
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.put('http://localhost:5001/tasks/complete/' + str(doc['_id']), data=json.dumps(payload), headers=headers)
        data = r.json()
        self.assertEqual(data['updated'], 1)
        today = date.today().isoformat()
        doc = self.db.tasks.find_one({})
        self.assertEqual(doc['status'], Task.STATUS['COMPLETE'])
        self.assertEqual(doc['statusdate'], today)

if __name__ == '__main__':
    unittest.main()
