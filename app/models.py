from datetime import datetime
from flask.ext.superadmin import model
from app import db


class News(db.Document):
    title = db.StringField(required=True, unique=True)
    author = db.StringField(required=True)
    category = db.ListField(db.StringField())
    text = db.StringField(required=True)
    small_text = db.StringField(required=True)
    pic = db.StringField(required=True)
    link = db.StringField(required=True)
    source = db.StringField(required=True)
    date = db.DateTimeField(required=True, default=datetime.now)
    popular = db.IntField()



class User(db.Document):
    login = db.StringField(required=True, max_length=50)
    password = db.StringField(required=True, max_length=255)
    email = db.EmailField(required=True, max_length=50)
    bitcoin_wallet = db.StringField(max_length=50)
    avatar = db.StringField()
    date = db.DateTimeField(default=datetime.now)
    balance = db.IntField(default=0)

class Free(db.Document):
    wallet = db.StringField(required=True, max_length=50)
    date = db.DateTimeField(default=datetime.now)
    ip = db.StringField(required=True, max_length=17)
    reward = db.IntField(required=True)
    reffer = db.StringField()

class Contact(db.Document):
    name = db.StringField(required=True, max_length=50)
    date = db.DateTimeField(default=datetime.now)
    email = db.EmailField(required=True, max_length=50)
    message = db.StringField(required=True, max_length=1030)

class NewsAdminModel(model.ModelAdmin):
    list_display = ('title', 'date')