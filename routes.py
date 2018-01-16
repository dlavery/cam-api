from app import app
from flask import request
from flask import jsonify
from models import Task
from models import ModelException

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
        task.title = request.json['title']
        task.description = request.json['description']
        task.url = request.json['url']
        task.tags = request.json['tags']
        if ('notbefore' in request.json):
            task.notbefore = request.json['notbefore']
        task_id = task.create()
        app.logger.error("success: " + task_id)
        return jsonify({'_id' : task_id})
    except ModelException as model_err:
        app.logger.error(str(model_err))
        return "Bad Request", 400
    except Exception as system_err:
        app.logger.error(str(system_err))
        return "Unexpected error", 500

@app.route('/tasks/{<string:id>', methods=['GET'])
def getTask(id):
    """
    Retrieve a task from the tasks collection
    """
