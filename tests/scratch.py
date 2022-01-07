"""
Scratch file
"""


from typing import Generic, NewType, Type, TypeVar
from sqlalchemy import Column, Integer, String, create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import ColumnProperty, relationship, sessionmaker
from sqlalchemy.sql.schema import ForeignKey

import sqlalchemyseed
from sqlalchemyseed import *
from sqlalchemyseed.key_value import *
from sqlalchemyseed.util import generate_repr

Base = declarative_base()


class Single(Base):
    """
    A class with no child
    """
    __tablename__ = 'single'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))

    def __repr__(self) -> str:
        return generate_repr(self)


class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    children = relationship('Child')

    def __repr__(self) -> str:
        return generate_repr(self)


class Child(Base):
    __tablename__ = 'children'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    parent_id = Column(Integer, ForeignKey('parents.id'))

    def __repr__(self) -> str:
        return generate_repr(self)


engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

print(sqlalchemyseed.__version__)

single = Single(value='343')


MANY_SINGLE = [
    {
        'model': 'scratch.Single',
        'data': {
            'value': 'Single Value',
        },
    },
    {
        'model': 'scratch.Single',
        'data': {
            'value': 'Single Value',
        },
    },
]

seeder = Seeder()
seeder.seed(MANY_SINGLE, add_to_session=False)

# js = JsonWalker([2, [1, {'yaha': 'lost', 'hello': 'world'}, 4]])
# val = js.find([1, 1])
# js.forward([1, 1])
# print(js.path)
# js.forward(['yaha'])
# print(js.path)
# print(js.current)
