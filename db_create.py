'''
This file create database.
'''

from application import db, app
from application.models import *

from sqlalchemy import create_engine

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

Base.metadata.create_all(engine)

print("DB created.")
