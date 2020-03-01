from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.superadmin import Admin
from flask.ext.pymongo import PyMongo
from flask.ext.recaptcha import ReCaptcha
from flask_analytics import Analytics
from redis import Redis

app = Flask(__name__)
app.config.from_object('config')
Analytics(app)
db = MongoEngine(app)
mongo = PyMongo(app)
recaptcha = ReCaptcha(app)
redis = Redis()

from app import views
