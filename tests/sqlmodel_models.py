"""SQLModel counterparts of tests/models.py for the compatibility tests.

Kept separate from tests/models.py: these register in SQLModel's global
``SQLModel.metadata``, not the declarative ``Base`` metadata.
"""

from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    employees: list["Employee"] = Relationship(back_populates="company")


class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")

    company: Optional[Company] = Relationship(back_populates="employees")


class Plain(SQLModel):
    """Not table=True — not a mapped class; the seeder must reject it."""

    name: str
