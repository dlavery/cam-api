from app import app
from app import mongo
from app import runPort
import routes

if __name__ == '__main__':
    app.run(port=int(runPort), debug=False)
