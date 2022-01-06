"""
Scratch file
"""

import logging

import sqlalchemy
from sqlalchemy.orm.attributes import set_attribute
from sqlalchemy.orm.base import class_mapper, object_mapper, object_state
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.orm.relationships import foreign
import sqlalchemy.orm.state
from sqlalchemy import Column, create_engine, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import ColumnProperty, relationship, sessionmaker
from sqlalchemy.sql.base import ColumnCollection, Immutable, ImmutableColumnCollection
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.util._collections import ImmutableProperties
from sqlalchemy_utils import generic_repr

import sqlalchemyseed
from sqlalchemyseed.key_value import *
from sqlalchemyseed.seeder import Entity, EntityTuple
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

# print(single)
# print(generate_repr(single))

wrapped = AttributeValue(Child.name, 1)
attr: InstrumentedAttribute = wrapped.attr
parent: orm.Mapper = attr.parent
comp: ColumnProperty.Comparator = attr.comparator
prop: ColumnProperty = attr.property

print(parent.tables[0].name)
print(wrapped.referenced_class)


# entity = Entity(instance=Parent(name="John Doe"), attr_name='name')

# print(entity.referenced_class)


for col in wrapped.parent.columns:
    print(col)
    foreign_keys = tuple(col.foreign_keys)
    if len(foreign_keys) > 0:
        foreign_keys = foreign_keys[0]
        col_: Column = foreign_keys.column
        print(col_.table.name)
        class_ = next(filter(
            lambda mapper: mapper.class_.__tablename__ == col_.table.name,
            wrapped.parent.registry.mappers
        )).class_
        print(f"referenced class: {class_}")
        # print(foreign_keys.column.key)
        # print(foreign_keys.column.name)
    print()
