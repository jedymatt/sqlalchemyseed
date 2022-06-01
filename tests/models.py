from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemyseed.util import generate_repr

Base = declarative_base()
AnotherBase = declarative_base()


class Person(Base):
    """
    Person class
    """
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    age = Column(Integer)

    location_id = Column(Integer, ForeignKey('locations.id'))

    spouse = relationship('Spouse', uselist=False, back_populates='person')
    location = relationship('Location', back_populates='persons')
    cars = relationship('Car', back_populates='owner')

    def __repr__(self):
        return generate_repr(self)


class Car(Base):
    """
    Car class.
    """
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner_id = Column(Integer, ForeignKey('persons.id'))

    owner = relationship('Person', back_populates='cars')

    def __repr__(self) -> str:
        return generate_repr(self)


class Spouse(Base):
    """
    Spouse class.
    """
    __tablename__ = 'spouses'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)
    person_id = Column(Integer, ForeignKey('persons.id'))

    person = relationship('Person', back_populates='spouse')

    def __repr__(self) -> str:
        return generate_repr(self)


class Location(Base):
    """
    Location class.
    """
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    persons = relationship('Person', back_populates='location')

    def __repr__(self) -> str:
        return generate_repr(self)


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    address = Column(String(50))

    def __repr__(self) -> str:
        return generate_repr(self)
