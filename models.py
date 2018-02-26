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
    PENDING_STATUS = "PENDING"
    IN_PROGRESS_STATUS = "IN_PROGRESS"
    COMPLETE_STATUS = "COMPLETE"

    # DB parameters
    INDEX_ASCENDING = 1
    INDEX_DESCENDING = -1

    def __init__(self):
        today = date.today().isoformat()
        self.PRIORITIES = {v: k for k, v in self.TASK_PRIORITIES.items()}
        self.tasks_db = mongo.db.tasks
        self.tasks_db.create_index([('status', self.INDEX_ASCENDING),
            ('notbefore', self.INDEX_ASCENDING),
            ('priority', self.INDEX_ASCENDING),
            ('timestamp', self.INDEX_ASCENDING)],
            unique=False, background=True)
        self.title = ''
        self.description = ''
        self.url = ''
        self.origin = ''
        self.tags = ''
        self.notbefore = today
        self.status = self.PENDING_STATUS
        self.statusdate = today
        self.priority = self.PRIORITIES[self.MEDIUM_PRIORITY]
        self.cryptokey = config['CRYPTO']['cryptoKey']

    def create(self):
        err = self.validate()
        if err:
            raise ModelException(err)
        crypto = Fernet(self.cryptokey)
        task_id = self.tasks_db.insert({
            'title': crypto.encrypt(self.title.encode()).decode(),
            'description': crypto.encrypt(self.description.encode()).decode(),
            'url': self.url,
            'origin': self.origin,
            'tags': self.tags,
            'notbefore': self.notbefore,
            'priority': self.TASK_PRIORITIES[self.priority],
            'status': self.status,
            'statusdate': self.statusdate,
            'timestamp': datetime.utcnow().timestamp()
            })
        return str(task_id)

    def validate(self):
        if not self.title:
            return "title is mandatory"
        elif not self.description:
            return "description is mandatory"
        elif not self.url:
            return "url is mandatory"
        elif not self.tags:
            return "tags is mandatory"
        elif not self.origin:
            return "origin is mandatory"
        elif (self.priority not in self.TASK_PRIORITIES):
            return "priority must be high, medium or low"
        elif not url(self.url):
            return "invalid task url"
        else:
            return False

    def read(self, task_id):
        doc = self.tasks_db.find_one({'_id': ObjectId(task_id)})
        if doc:
            return self.decrypt_doc(doc)
        return doc

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

class ModelException(Exception):
    pass
