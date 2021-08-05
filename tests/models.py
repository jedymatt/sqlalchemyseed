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
