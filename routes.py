from app import app
from flask import request
from flask import jsonify

@app.route('/', methods=['GET'])
def hello():
  return jsonify({'greeting' : 'Hello, World'})

@app.route('/tasks', methods=['POST'])
def addTask():
    title = request.json['title']
    desrciption = request.json['description']
    url = request.json['url']
