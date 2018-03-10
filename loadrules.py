import configparser
import pymongo
import json
from pymongo import MongoClient

def loadrules():
    # load rules into the DB
    config = configparser.ConfigParser()
    config.read('cam-api.cfg')
    client = MongoClient(config['DATABASE']['dbURI'])
    db = client[config['DATABASE']['dbName']]
    db.rules.delete_many({})
    with open('queuerules.json') as f:
        rules_data = json.load(f)
    db.rules.insert_one(rules_data)

if __name__ == '__main__':
    loadrules()
    print('Rules updated')
