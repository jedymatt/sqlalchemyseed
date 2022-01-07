"""
Scratch file
"""


import dataclasses
from typing import Generic, NewType, Type, TypeVar, Union
from sqlalchemy import Column, Integer, String, create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import ColumnProperty, relationship, sessionmaker
from sqlalchemy.sql.schema import ForeignKey

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


T = TypeVar('T')


# class Stack(Generic[T]):
#     def __init__(self) -> None:
#         # Create an empty list with items of type T
#         self.items: list[T] = []

#     def push(self, item: T) -> None:
#         self.items.append(item)

#     def pop(self) -> T:
#         return self.items.pop()

#     def empty(self) -> bool:
#         return not self.items


# stack = Stack[int]()
# stack.push(2)
# stack.pop()
# stack.push('x')        # Type error
