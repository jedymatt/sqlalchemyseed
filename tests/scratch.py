"""
Scratch file
"""

import logging

import sqlalchemy
import sqlalchemy.orm.state
from models import Base, Parent, Single
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import generic_repr

import sqlalchemyseed
from sqlalchemyseed.util import generate_repr

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

print(sqlalchemyseed.__version__)


single = Single()
mapper: sqlalchemy.orm.state.InstanceState = inspect(
    Parent.children, raiseerr=False)

print(single)
print(generate_repr(single))
# var = inspect(single, raiseerr=False)
# print(vars(inspect(Single.id)))
# print("=============================")
# print(mapper.is_mapper)
