import re
from app import mongo
from app import config
from datetime import date
from datetime import datetime
from cryptography.fernet import Fernet
from validators import url
from bson.objectid import ObjectId

class Task:

    # Priorities
    HIGH_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    LOW_PRIORITY = 3
    TASK_PRIORITIES = {'high': HIGH_PRIORITY, 'medium': MEDIUM_PRIORITY, 'low': LOW_PRIORITY}

    # Statuses
    STATUS = {'PENDING': 'PENDING',
        'QUEUED': 'QUEUED',
        'IN-PROGRESS': 'PROGRESS',
        'COMPLETE': 'COMPLETE'}

    # DB parameters
    INDEX_ASCENDING = 1
    INDEX_DESCENDING = -1

    def __init__(self):
        today = date.today().isoformat()
        self.PRIORITIES = {v: k for k, v in self.TASK_PRIORITIES.items()}
        self.tasks_db = mongo.db.tasks
        self.tasks_db.tasks.create_index([('status', self.INDEX_ASCENDING),
            ('timestamp', self.INDEX_ASCENDING)],
            unique=False, background=True)
        self.tasks_db.tasks.create_index([('queue', self.INDEX_ASCENDING),
            ('notbefore', self.INDEX_ASCENDING),
            ('priority', self.INDEX_ASCENDING),
            ('timestamp', self.INDEX_ASCENDING)],
            unique=False, sparse=True, background=True)
        self.title = ''
        self.description = ''
        self.requester = ''
        self.tags = None
        self.notbefore = today
        self.status = self.STATUS['PENDING']
        self.statusdate = today
        self.priority = self.PRIORITIES[self.MEDIUM_PRIORITY]
        self.cryptokey = config['CRYPTO']['cryptoKey']

    def create(self):
        err = self.validate()
        if err:
            raise ModelException(err)
        crypto = Fernet(self.cryptokey)
        doc = {
            'title': crypto.encrypt(self.title.encode()).decode(),
            'description': crypto.encrypt(self.description.encode()).decode(),
            'requester': self.requester,
            'tags': self.tags,
            'notbefore': self.notbefore,
            'priority': self.TASK_PRIORITIES[self.priority],
            'status': self.status,
            'statusdate': self.statusdate,
            'timestamp': datetime.utcnow().timestamp()
        }
        if self.url:
            doc['url'] = self.url
        task_id = self.tasks_db.insert(doc)
        return str(task_id)

    def read(self, task_id):
        try:
            id = ObjectId(task_id)
        except Exception as err:
            return None
        doc = self.tasks_db.find_one({'_id': id})
        if doc:
            return self.decrypt_doc(doc)
        return doc

    def list(self, queueName, limit):
        today = date.today().isoformat()
        docs = self.tasks_db.find({'queue': queueName, 'status': self.STATUS['QUEUED'], 'notbefore': {'$lte': today}}).sort([
            ('priority', self.INDEX_ASCENDING),
            ('notbefore', self.INDEX_ASCENDING),
            ('timestamp', self.INDEX_ASCENDING)
        ]).limit(limit)
        clearDocs = []
        for doc in docs:
            clearDocs.append(self.decrypt_doc(doc))
        return {'tasks': clearDocs}

    def update(self, doc):
        update_pending = False
        today = date.today().isoformat()
        newtimestamp = datetime.utcnow().timestamp()
        if '_id' not in doc:
            raise ModelException('document _id missing')
        if 'timestamp' not in doc:
            raise ModelException('document timestamp missing')
        if 'notbefore' in doc:
            update_pending = True
            if doc['notbefore'] > today:
                try:
                    l = doc['notbefore'].split('-')
                    d = date(int(l[0]), int(l[1]), int(l[2]))
                except Exception as err:
                    raise ModelException('notbefore must be YYYY-MM-DD')
            else:
                raise ModelException('notbefore must be YYYY-MM-DD and in future')
        if 'priority' in doc:
            update_pending = True
            if doc['priority'] not in self.TASK_PRIORITIES:
                raise ModelException('invalid priority')
        if 'status' in doc:
            update_pending = True
            doc['statusdate'] = today
            if doc['status'] not in self.STATUS:
                raise ModelException('invalid status')
        if 'note' in doc:
            update_pending = True
            if 'text' not in doc['note'] or 'originator' not in doc['note'] \
            or not doc['note']['text'] or not doc['note']['originator']:
                raise ModelException('note must contain text and originator')
        if not update_pending:
            return 0
        updateclause = {}
        updateclause['$set'] = {'timestamp': newtimestamp}
        if 'updater' in doc:
            updateclause['$set']['updater'] = doc['updater']
        if 'notbefore' in doc:
            updateclause['$set']['notbefore'] = doc['notbefore']
        if 'priority' in doc:
            updateclause['$set']['priority'] = self.TASK_PRIORITIES[doc['priority']]
        if 'status' in doc:
            updateclause['$set']['status'] = self.STATUS[doc['status']]
            updateclause['$set']['statusdate'] = doc['statusdate']
        if 'note' in doc:
            updateclause['$push'] = {'notes': {'text': doc['note']['text'], 'originator': doc['note']['originator'], 'ondate': today}}
        # update document inc timestamp in query to ensure no change since read
        res = self.tasks_db.update_one(
            {'_id': ObjectId(doc['_id']), 'timestamp': doc['timestamp']},
            updateclause)
        if res.modified_count == 0:
            raise ConcurrencyException('task has been updated by another user')
        else:
            return res.modified_count

    def decrypt_doc(self, doc):
        crypto = Fernet(self.cryptokey)
        doc['_id'] = str(doc['_id'])
        if 'title' in doc:
            doc['title'] = crypto.decrypt(doc['title'].encode()).decode()
        if 'description' in doc:
            doc['description'] = crypto.decrypt(doc['description'].encode()).decode()
        if 'priority' in doc:
            doc['priority'] = self.PRIORITIES[doc['priority']]
        return doc

    def validate(self):
        if not self.title:
            return "title is mandatory"
        elif not self.description:
            return "description is mandatory"
        elif not self.tags:
            return "tags is mandatory"
        elif not self.requester:
            return "requester is mandatory"
        elif (self.priority not in self.TASK_PRIORITIES):
            return "priority must be high, medium or low"
        elif url and not url(self.url):
            return "invalid task url"
        else:
            for tag in self.tags:
                if not re.match('^#[A-Za-z]{1}[A-Za-z0-9-_]*[A-Za-z0-9]{1}$', tag):
                    return "invalid tag, should be #[A-Za-z]{1}[A-Za-z0-9_-]*[A-Za-z0-9]{1}"
            return False

class ModelException(Exception):
    pass

class ConcurrencyException(Exception):
    pass

class Rules:

    def __init__(self):
        self.rules_db = mongo.db.rules

    def list_queues(self):
        doc = self.rules_db.find_one()
        queues = set()
        for rule in doc['rules']:
            if 'then' in rule and 'queue' in rule['then']:
                queues.add(rule['then']['queue'])
        return {'queues': list(queues)}
