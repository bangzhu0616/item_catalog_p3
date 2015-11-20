from application import db, app
from application.models import *
from application.forms import *

from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import json, os

engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))

if not os.path.exists('./database.db'):
    Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def say_hello():
    return 'Hello'

if __name__ == '__main__':

    app.debug = True
    app.run()