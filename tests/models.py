from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemyseed.util import generate_repr

Base = declarative_base()
AnotherBase = declarative_base()


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


class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))


not_class = 'this is not a class'


class UnsupportedClass:
    """This is an example of an unsupported class"""
    pass


class AnotherCompany(AnotherBase):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    employees = relationship('Employee', back_populates='company')

    def __repr__(self) -> str:
        return f"<AnotherEmployee(name='{self.name}')>"


class AnotherEmployee(AnotherBase):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    company_id = Column(Integer, ForeignKey('companies.id'))

    company = relationship(
        'Company', back_populates='employees', uselist=False)

    def __repr__(self) -> str:
        return f"<AnotherEmployee(name='{self.name}', company='{self.company}')>"


class Single(Base):
    """
    Single class with no child
    """
    __tablename__ = 'single'
    id = Column(Integer, primary_key=True)
    value = Column(String(45))

    def __repr__(self) -> str:
        return generate_repr(self)


class One(Base):
    """
    One class with no other Parent that relates to its child.
    """
    __tablename__ = 'single_parent'

    id = Column(Integer, primary_key=True)
    value = Column(String(45))

    def __repr__(self) -> str:
        return generate_repr(self)


class OneToOne(Base):
    """
    OneToOne class
    """
    __tablename__ = 'one_to_one'

    id = Column(Integer, primary_key=True)
    value = Column(String(45))

    def __repr__(self) -> str:
        return generate_repr(self)

class OneToMany(Base):
    """
    OneToMany class
    """
    __tablename__ = 'one_to_many'

    id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return generate_repr(self)


class ManyToOne(Base):
    """
    ManyToOne class
    """
    __tablename__ = 'many_to_one'

    id = Column(Integer, primary_key=True)


class ManyToMany(Base):
    """
    ManyToMany class
    """
    __tablename__ = 'many_to_many'

    id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return generate_repr(self,)


val = Single(value='str value')
print(repr(val))
