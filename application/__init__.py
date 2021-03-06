# initial this flask application

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

app.config.from_object('config')
db = SQLAlchemy(app)
