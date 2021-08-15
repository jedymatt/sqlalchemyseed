from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    employees = relationship('Employee', back_populates='company')

    def __repr__(self) -> str:
        return f"<Company(name='{self.name}')>"


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship(
        'Company', back_populates='employees', uselist=False)

    def __repr__(self) -> str:
        return f"<Employee(name='{self.name}', company='{self.company}')>"


class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    children = relationship('Child')

    def __repr__(self) -> str:
        return f"<Parent(name='{self.name}', children='{[child.name if child.name is not None else child for child in self.children]}')>"


class Child(Base):
    __tablename__ = 'children'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    parent_id = Column(Integer, ForeignKey('parents.id'))

    children = relationship('GrandChild')


class GrandChild(Base):
    __tablename__ = 'grand_children'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    parent_id = Column(Integer, ForeignKey('children.id'))


class Character(Base):
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'character',
        'polymorphic_on': type
    }


class Player(Character):
    # __tablename__ = 'players'
    #
    # id = Column(Integer, ForeignKey('characters.id'), primary_key=True)
    #
    # player_id = Column(Integer, ForeignKey('players.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'player'
    }
