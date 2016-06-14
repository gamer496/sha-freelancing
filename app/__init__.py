from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

app=Flask(__name__)
manager=Manager(app)
app.secret_key="reality is broken"
app.config.from_object("config")
db=SQLAlchemy(app)
cors=CORS(app)
migrate=Migrate(app,db)
auth=HTTPBasicAuth()
from app import models,views
