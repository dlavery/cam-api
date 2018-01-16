from flask import Flask
from flask_pymongo import PyMongo
from logging import Formatter
from logging import FileHandler

# Create application
app = Flask(__name__)

# Read external config
app.config['MONGO_DBNAME'] = 'cam'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/cam'
logfile = '/usr/local/var/log/cam-api.log'

# Set up logging
fh = FileHandler(logfile, mode='a', encoding='utf8', delay=False)
fmt = Formatter('%(asctime)s %(levelname)s %(filename)s %(lineno)d %(message)s')
fh.setFormatter(fmt)
app.logger.addHandler(fh)

# Set up database
mongo = PyMongo(app)
