"""
Scratch file
"""


import dataclasses
from typing import Generic, NewType, Type, TypeVar, Union
from sqlalchemy import Column, Integer, String, create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import ColumnProperty, relationship, sessionmaker
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper, class_mapper
from sqlalchemy.orm import object_mapper

import sqlalchemyseed
from sqlalchemyseed import *
from sqlalchemyseed.key_value import *
from sqlalchemyseed.util import generate_repr
from dataclasses import dataclass

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


mapper: Mapper = object_mapper(single)

print(mapper.identity_key_from_instance(single))
