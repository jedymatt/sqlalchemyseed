"""
Scratch file
"""

import dataclasses
from typing import Generic, NewType, Type, TypeVar, Union
from sqlalchemy import Column, Integer, String, create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import ColumnProperty, relationship, sessionmaker
from sqlalchemy.orm import MapperProperty
from sqlalchemy.orm import attributes
from sqlalchemy.orm.attributes import ScalarAttributeImpl, get_attribute, set_committed_value
from sqlalchemy.orm.base import state_attribute_str
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import inspect
from sqlalchemy.orm.mapper import Mapper, class_mapper
from sqlalchemy.orm import object_mapper

import sqlalchemyseed
from sqlalchemyseed import *
from sqlalchemyseed.key_value import *
from sqlalchemyseed.util import generate_repr
from dataclasses import dataclass
from sqlalchemy.orm.instrumentation import ClassManager

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

single = Single(value='str')

wrapper = AttributeWrapper(getattr(single, 'value'))
print(wrapper.is_column)
mapper: Mapper = object_mapper(single)
class_manager: ClassManager = mapper.class_manager

attr = get_attribute(single, 'value')
for c in list(mapper.attrs):
    c: ColumnProperty = c
    print(c.key)
    parent: Mapper = c.parent
    print(parent.class_.__name__)
    var: InstrumentedAttribute = c.class_attribute

InstrumentedList