from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from pymongo import MongoClient
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

from flask_login import LoginManager
import json
from bson import ObjectId
import os 

app = Flask(__name__)
bcrypt=Bcrypt(app)
# uri = "mongodb+srv://asha:eXDgKIQUKvDIupLI@clusterflask.de3liz7.mongodb.net/?retryWrites=true&w=majority"
# client = MongoClient(uri, server_api=ServerApi('1'))
app.config['SECRET_KEY']='secret'
app.config["MONGO_URI"] = "mongodb+srv://asha:eXDgKIQUKvDIupLI@clusterflask.de3liz7.mongodb.net/CMSapp?retryWrites=true&w=majority"
# "mongodb+srv://asha:password01@cluster0-llbmc.mongodb.net/CMSapp?retryWrites=true&w=majority"
mongo = PyMongo(app)
login_manager= LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

from cms import routes