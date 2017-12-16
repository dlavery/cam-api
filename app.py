from flask import Flask
from flask_pymongo import PyMongo
from logging.handlers import TimedRotatingFileHandler

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'cam'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cam'

fh = TimedRotatingFileHandler('cam-api.log', when='midnight', encoding='utf8', delay=False, utc=True)
app.logger.addHandler(fh)

mongo = PyMongo(app)
