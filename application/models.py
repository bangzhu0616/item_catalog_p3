from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKeyConstraint, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

from werkzeug.security import generate_password_hash, check_password_hash
from application import app, db

import os

class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
        }

class Items(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String)
    create_at = db.Column(db.DateTime, default=func.now())
    cat = db.Column(db.Integer, nullable=False)
    category = relationship(Categories)

    __table_args__ = (
        ForeignKeyConstraint(
            ['cat'], 
            ['categories.id']
        ),
    )

    def get_cat_name(self):
        session = object_session(self)
        category = session.query(Categories).filter_by(id=self.cat).one()
        return category.name

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
            'description'   : self.description,
            'categroy'  : {
                'id'    : self.cat,
                'name'  : self.get_cat_name,
            }
        }

class Accounts(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable = False)
    password_hash = db.Column(db.String(250))
    email = db.Column(db.String(100))
    create_at = db.Column(db.DateTime, default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

