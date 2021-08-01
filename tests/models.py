from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# one-to-one, done
# nested relationship, done
# filter and data, done
# one to many, done
#  many to many, done

class Person(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)

    name = Column(String(255))

    child_id = Column(Integer, ForeignKey('people.id'))
    child = relationship('Person')

    def __repr__(self):
        return "<Person(child='%s')>" % self.child


class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

    children = relationship('Child', back_populates='parent')

    def __repr__(self):
        return "<Parent(name='{}', age='{}', children='{}')>".format(self.name, self.age, self.children)


class Child(Base):
    __tablename__ = 'children'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    age = Column(Integer)
    parent_id = Column(Integer, ForeignKey('parents.id'))

    parent = relationship('Parent', back_populates='children', uselist=False)

    def __repr__(self):
        return "<Child(name='{}', age='{}')>".format(self.name, self.age)
