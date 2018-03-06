from app import app
from flask import request, escape
from flask import jsonify
from models import Task
from models import Rules
from models import ModelException
from models import ConcurrencyException

@app.route('/', methods=['GET'])
def hello():
  return jsonify({'greeting' : 'Hello, World'})

@app.route('/tasks', methods=['POST'])
def addTask():
    """
    Add a task to the tasks collection
    """
    try:
        task = Task()
        if 'title' in request.json:
            task.title = escape(request.json['title'])
        if 'description' in request.json:
            task.description = escape(request.json['description'])
        if 'url' in request.json:
            task.url = request.json['url']
        if 'tags' in request.json:
            task.tags = escape(request.json['tags'])
        if 'requester' in request.json:
            task.requester = escape(request.json['requester'])
        if ('priority' in request.json):
            task.priority = escape(request.json['priority'])
        if ('notbefore' in request.json):
            task.notbefore = escape(request.json['notbefore'])
        task_id = task.create()
        return jsonify({'_id' : task_id})
    except ModelException as model_err:
        app.logger.error(str(model_err))
        return "Bad Request", 400
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/tasks/<string:id>', methods=['GET'])
def getTask(id):
    """
    Retrieve a task from the tasks collection
    """
    try:
        task = Task()
        res = task.read(id)
        if not res:
            return "Not found", 404
        return jsonify(res)
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/queues', methods=['GET'])
def getQueues():
    """
    Get a list of active queues
    """
    try:
        rules = Rules()
        res = rules.list_queues()
        if not res:
            return "Not found", 404
        return jsonify(res)
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/queues/<string:qname>/<int:lim>', methods=['GET'])
def getQueueTasks(qname, lim):
    """
    Get a list of tasks in a queue - use this if with a limit > 0
    if you're not happy with the default prioritisation and wish
    to manage queue concurrency within the client application
    """
    try:
        task = Task()
        res = None
        while True:
            queuedocs = []
            res = task.list(qname, lim)
            if not res or len(res['tasks']) == 0:
                break
            for doc in res['tasks']:
                try:
                    # update the documents so they don't get returned next time
                    upd = task.update({'_id': doc['_id'], 'timestamp': doc['timestamp'], 'status': 'IN-PROGRESS'})
                    if upd > 0:
                        queuedocs.append(doc)
                except ConcurrencyException as concurrrent_err:
                    pass
            if len(queuedocs) > 0:
                break
        res['tasks'] = queuedocs
        return jsonify(res)
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/tasks/<string:id>', methods=['PUT'])
def updateTask():
    """
    Update a task
    """
    try:
        task = Task()
        if 'title' in request.json:
            task.title = escape(request.json['title'])
        if 'description' in request.json:
            task.description = escape(request.json['description'])
        if 'url' in request.json:
            task.url = request.json['url']
        if 'tags' in request.json:
            task.tags = escape(request.json['tags'])
        if 'requester' in request.json:
            task.requester = escape(request.json['requester'])
        if ('priority' in request.json):
            task.priority = escape(request.json['priority'])
        if ('notbefore' in request.json):
            task.notbefore = escape(request.json['notbefore'])
        task_id = task.create()
        return jsonify({'_id' : task_id})
    except ModelException as model_err:
        app.logger.error(str(model_err))
        return "Bad Request", 400
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500
