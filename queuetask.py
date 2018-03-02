import configparser
import pymongo
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.ruleset import RuleSet

def setup(db):
    INDEX_ASCENDING = 1
    INDEX_DESCENDING = -1
    db.tasks.create_index([('queue', INDEX_ASCENDING),
                ('notbefore', INDEX_ASCENDING),
                ('priority', INDEX_ASCENDING),
                ('timestamp', INDEX_ASCENDING)],
                unique=False, sparse=True, background=True)

if __name__ == '__main__':
    # allocate tasks to a queue
    config = configparser.ConfigParser()
    config.read('cam-api.cfg')
    client = MongoClient(config['DATABASE']['dbURI'])
    db = client[config['DATABASE']['dbName']]
    setup(db)
    rules = db.rules.find_one()
    rs = RuleSet(rules)
    tasks = db.tasks.find({'status': 'PENDING'}).sort('timestamp', pymongo.ASCENDING)
    processed = 0
    for task in tasks:
        task_id = str(task['_id'])
        del task['_id']
        rs.evaluate(task)
        task['status'] = 'QUEUED'
        res = db.tasks.replace_one({'_id': ObjectId(task_id)}, task)
        processed = processed + 1
    print('Number of tasks queued: ' + str(processed))
