from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Association(Base):
    __tablename__ = 'association'
    left_id = Column(ForeignKey('left.id'), primary_key=True)
    right_id = Column(ForeignKey('right.id'), primary_key=True)
    extra_value = Column(String(45))
    child = relationship("Child", back_populates="parents")
    parent = relationship("Parent", back_populates="children")


class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    children = relationship("Association", back_populates="parent")


class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    parents = relationship("Association", back_populates="child")
