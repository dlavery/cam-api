from app import mongo
from datetime import date

class Task:

    def __init__(self):
        today = date.today().isoformat()
        self.tasks_db = mongo.db.tasks
        self.title = ''
        self.description = ''
        self.url = ''
        self.tags = ''
        self.notbefore = today
        self.status = 'NEW'
        self.statusdate = today

    def create(self):
        if not self.validate():
            raise ModelException("invalid task")
        task_id = self.tasks_db.insert({'title': self.title, 'description': self.description, 'url': self.url, 'tags': self.tags, 'notbefore': self.notbefore, 'status': self.status, 'statusdate': self.statusdate })
        return str(task_id)

    def validate(self):
        if (not self.title
        or not self.description
        or not self.url
        or not self.tags):
            return False
        else:
            return True

class ModelException(Exception):
    pass
