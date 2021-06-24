from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# one-to-one, done
# nested relationship, done
# filter and data, done
# one to many, done
#  many to many, done

class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    child = relationship('Child', back_populates='parent', uselist=False)


class Child(Base):
    __tablename__ = 'children'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    age = Column(Integer)
    parent_id = Column(Integer, ForeignKey('parents.id'))

    parent = relationship('Parent', back_populates='child', uselist=False)
