import configparser
import pymongo
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.ruleset import RuleSet
from models import Task

def setup(db):
    INDEX_ASCENDING = 1
    INDEX_DESCENDING = -1
    db.tasks.create_index([('status', INDEX_ASCENDING),
                ('timestamp', INDEX_ASCENDING)],
                unique=False)
    db.tasks.create_index([('queue', INDEX_ASCENDING),
                ('notbefore', INDEX_ASCENDING),
                ('priority', INDEX_ASCENDING),
                ('timestamp', INDEX_ASCENDING)],
                unique=False, sparse=True)

if __name__ == '__main__':
    # allocate tasks to a queue
    config = configparser.ConfigParser()
    config.read('cam-api.cfg')
    client = MongoClient(config['DATABASE']['dbURI'])
    db = client[config['DATABASE']['dbName']]
    setup(db)
    rules = db.rules.find_one()
    rs = RuleSet(rules)
    today = date.today().isoformat()
    processed = 0
    tasks = db.tasks.find({'status': Task.STATUS['PENDING']}).sort('timestamp', pymongo.ASCENDING)
    for task in tasks:
        task_id = str(task['_id'])
        del task['_id']
        rs.evaluate(task)
        task['status'] = Task.STATUS['QUEUED']
        task['statusdate'] = today
        res = db.tasks.replace_one({'_id': ObjectId(task_id)}, task)
        processed = processed + 1
    print('Number of tasks queued: ' + str(processed))
