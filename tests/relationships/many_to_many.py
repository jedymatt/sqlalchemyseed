from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String

Base = declarative_base()


association_table = Table(
    'association',
    Base.metadata,
    Column('left_id', ForeignKey('left.id'), primary_key=True),
    Column('right_id', ForeignKey('right.id'), primary_key=True),
)


class Parent(Base):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    children = relationship(
        "Child",
        secondary=association_table,
        back_populates="parents"
    )


class Child(Base):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))
    parents = relationship(
        "Parent",
        secondary=association_table,
        back_populates="children"
    )
