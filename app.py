from flask import Flask
from flask_pymongo import PyMongo
from logging import FileHandler

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'cam'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cam'

fh = FileHandler('cam-api.log', mode='a', encoding='utf8', delay=False)
app.logger.addHandler(fh)

mongo = PyMongo(app)
