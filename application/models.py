from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKeyConstraint, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session

from werkzeug.security import generate_password_hash, check_password_hash
from application import app

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        return {
            'id'    : self.id,
            'name'  : self.name,
        }

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    description = Column(String)
    create_at = Column(DateTime, default=func.now())
    cat = Column(Integer, nullable=False)
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

class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable = False)
    password_hash = Column(String(250))
    email = Column(String(100))
    create_at = Column(DateTime, default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
