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
    Get a list of tasks in a queue - use this with a limit = 1 if you want to
    pull one task at a time and update task status to "IN PROGRESS".

    if you're not happy with the default prioritisation and wish
    to manage queue concurrency within the client application then use limit = 0
    for all tasks or limit = n to get a number of tasks - in this case tasks
    will not be updated to "IN_PROGRESS".
    """
    try:
        task = Task()
        res = None
        while True:
            queuedocs = []
            res = task.list(qname, lim)
            if not res or len(res['tasks']) == 0:
                break
            if lim == 1:
                doc = res['tasks'][0]
                try:
                    # update the document so it isn't returned next time
                    upd = task.update({'_id': doc['_id'], 'timestamp': doc['timestamp'], 'status': 'IN-PROGRESS'})
                    if upd > 0:
                        doc['status'] = Task.STATUS['IN-PROGRESS']
                        queuedocs.append(doc)
                except ConcurrencyException as concurrrent_err:
                    pass
            else:
                for doc in res['tasks']:
                    queuedocs.append(doc)
            if len(queuedocs) > 0:
                break
        res['tasks'] = queuedocs
        return jsonify(res)
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

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
            task.tags = request.json['tags']
        if 'requester' in request.json:
            task.requester = escape(request.json['requester'])
        if 'priority' in request.json:
            task.priority = escape(request.json['priority'])
        if 'notbefore' in request.json:
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

@app.route('/tasks/requeue/<string:id>', methods=['PUT'])
def requeueTask(id):
    """
    Re-queue a task
    """
    try:
        task = Task()
        doc = task.read(id)
        if not doc:
            return "Not found", 404
        if doc['status'] == Task.STATUS['COMPLETE']:
            return jsonify({'updated' : 0})
        if 'notbefore' not in request.json:
            return "Bad request", 400
        if 'priority' in request.json and request.json['priority'] not in Task.TASK_PRIORITIES:
            return "Bad request", 400
        if 'updater' not in request.json:
            return "Bad request", 400
        updateclause = {
            '_id': id,
            'timestamp': doc['timestamp'],
            'status': 'QUEUED',
            'updater': request.json['updater']}
        if 'notbefore' in request.json:
            updateclause['notbefore'] = request.json['notbefore']
        if 'priority' in request.json:
            updateclause['priority'] = request.json['priority']
        if 'note' in request.json:
            updateclause['note'] = {'text': request.json['note'], 'originator': request.json['updater']}
        upd = task.update(updateclause)
        return jsonify({'updated' : upd})
    except ModelException as model_err:
        app.logger.error(str(model_err))
        return "Bad Request", 400
    except ConcurrencyException as concurrency_err:
        return "Concurrent update", 409
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/tasks/complete/<string:id>', methods=['PUT'])
def completeTask(id):
    """
    Complete a task
    """
    try:
        task = Task()
        doc = task.read(id)
        if not doc:
            return "Not found", 404
        requestjson = {}
        if request.data:
            requestjson = request.json
        if doc['status'] == Task.STATUS['COMPLETE']:
            return jsonify({'updated' : 0})
        if 'updater' not in request.json:
            return "Bad request", 400
        updateclause = {
            '_id': id,
            'timestamp': doc['timestamp'],
            'status': 'COMPLETE',
            'updater': request.json['updater']}
        if 'note' in requestjson:
            updateclause['note'] = {'text': requestjson['note'], 'originator': requestjson['updater']}
        upd = task.update(updateclause)
        return jsonify({'updated' : upd})
    except ModelException as model_err:
        app.logger.error(str(model_err))
        return "Bad Request", 400
    except ConcurrencyException as concurrency_err:
        return "Concurrent update", 409
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500
