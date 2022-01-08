from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String

Base = declarative_base()


class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    child_id = Column(Integer, ForeignKey('child.id'))
    child = relationship("Child", back_populates="parents")


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    parents = relationship("Parent", back_populates="child")
