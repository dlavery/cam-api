from app import mongo
from app import config
from datetime import date
from datetime import datetime
from cryptography.fernet import Fernet
from validators import url

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

    def __init__(self):
        today = date.today().isoformat()
        priorities = {v: k for k, v in self.TASK_PRIORITIES.items()}
        self.tasks_db = mongo.db.tasks
        self.title = ''
        self.description = ''
        self.url = ''
        self.tags = ''
        self.notbefore = today
        self.status = self.PENDING_STATUS
        self.statusdate = today
        self.priority = priorities[self.MEDIUM_PRIORITY]
        self.cryptokey = config['CRYPTO']['cryptoKey']

    def create(self):
        if not self.validate():
            raise ModelException("invalid task")
        crypto = Fernet(self.cryptokey)
        task_id = self.tasks_db.insert({'title': self.title, 'description': crypto.encrypt(self.description.encode()).decode(), 'url': self.url, 'tags': self.tags, 'notbefore': self.notbefore, 'priority': self.TASK_PRIORITIES[self.priority], 'status': self.status, 'statusdate': self.statusdate, 'timestamp': datetime.utcnow().timestamp() })
        return str(task_id)

    def validate(self):
        if (not self.title
        or not self.description
        or not self.url
        or not self.tags):
            return False
        elif (self.priority not in self.TASK_PRIORITIES):
            return False
        elif (url(self.url)):
            return True
        else:
            return False

    def read(self):
        None

class ModelException(Exception):
    pass
