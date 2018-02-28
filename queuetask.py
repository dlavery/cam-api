import configparser
import pymongo
from pymongo import MongoClient
from utils import ruleset

def setup(db):
    INDEX_ASCENDING = 1
    INDEX_DESCENDING = -1
    db.taskqueue.create_index([('queueName', INDEX_ASCENDING)], unique=False)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('addressutils.cfg')
    client = MongoClient(config['DATABASE']['dbURI'])
    db = client[config['DATABASE']['dbName']]
    setup(db)

    with open('queuerules.json') as f2:
        rules_data = json.load(f2)
        rs = RuleSet(rules_data)
        results.append(rs.evaluate(person))

    # bucket pattern, push to queue but upsert on full bucket
    #db.taskqueue.update(
    #    {'queueId': '1', '$where': 'this.items.length<4'},
    #    {'$push': {'items': {'taskId': '5', 'status': '0'}}},
    #    True)

    # get list of queues
    #db.getCollection('test').distinct('queueId')

    # find a task in a queues
    #db.taskqueue.find({'queue.taskId': {$eq: '1'}})
    #db.taskqueue.update({'queue.taskId': {$eq: '1'}}, {$set: {'queue.$.status': '1'}})

    # find queue names
    #db.getCollection('test').distinct('queueName')
