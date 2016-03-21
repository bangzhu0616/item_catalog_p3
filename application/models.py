'''
This file defines the classes of all database tables.
'''

from sqlalchemy import Column, Integer, String, DateTime, ForeignKeyConstraint
from sqlalchemy import func, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

from werkzeug.security import generate_password_hash, check_password_hash
from application import app

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False, unique=True)
    account = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ['account'],
            ['accounts.id']
        ),
    )

    def get_items(self):
        session = object_session(self)
        items = session.query(Items).filter_by(cat=self.id).all()
        return items

    @property
    def serialize(self):
        items = self.get_items()
        return {
            'id'    : self.id,
            'account_id': self.account,
            'name'  : self.name,
            'item_count': len(items),
            'Item'  : [i.serialize_cat for i in items],
        }

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    description = Column(String)
    create_at = Column(DateTime, default=func.now())
    cat = Column(Integer, nullable=False)
    category = relationship(Categories)
    account = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ['cat'],
            ['categories.id']
        ),
        ForeignKeyConstraint(
            ['account'],
            ['accounts.id']
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
            'account_id': self.account,
            'categroy'  : {
                'id'    : self.cat,
                'name'  : self.get_cat_name(),
            }
        }

    @property
    def serialize_cat(self):
        return {
            'id': self.id,
            'title': self.name,
            'description': self.description,
            'cat_id': self.cat,
            'account': self.account,
        }

class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable = False)
    # password_hash = Column(String(250))
    email = Column(String(100))
    create_at = Column(DateTime, default=func.now())

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
