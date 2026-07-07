"""SQLModel compatibility tests.

A SQLModel ``table=True`` class is a real SQLAlchemy mapped class, so the
seeders are expected to work unchanged. These tests pin the paths where
SQLModel could genuinely diverge: instrumented-attribute inspection, the
``__tablename__``-based class lookup behind FK-column filters, and list
relationships. Skipped entirely when sqlmodel is not installed (the min-deps
CI job excludes the sqlmodel dependency group).
"""

import warnings

import pytest

pytest.importorskip("sqlmodel")

from sqlalchemy import select
from sqlmodel import Session, SQLModel, create_engine

from sqlalchemyseed import HybridSeeder, Seeder, errors
from sqlalchemyseed.loader import load_path
from tests.sqlmodel_models import Company, Employee


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_seeder_with_nested_reference(session):
    Seeder(session).seed(
        {
            "model": "tests.sqlmodel_models.Employee",
            "data": {
                "name": "John Smith",
                "!company": {
                    "model": "tests.sqlmodel_models.Company",
                    "data": {"name": "MyCompany"},
                },
            },
        }
    )
    session.commit()

    employee = session.scalars(select(Employee)).one()
    assert employee.name == "John Smith"
    assert employee.company.name == "MyCompany"


def test_seeder_one_to_many_list_relationship(session):
    Seeder(session).seed(
        {
            "model": "tests.sqlmodel_models.Company",
            "data": {
                "name": "ListCo",
                "!employees": [
                    {"data": {"name": "Alice"}},
                    {"data": {"name": "Bob"}},
                ],
            },
        }
    )
    session.commit()

    company = session.scalars(select(Company)).one()
    assert sorted(e.name for e in company.employees) == ["Alice", "Bob"]


def test_hybrid_seeder_filter_on_relationship(session):
    HybridSeeder(session).seed(
        {"model": "tests.sqlmodel_models.Company", "data": {"name": "Acme"}}
    )
    session.commit()

    HybridSeeder(session).seed(
        {
            "model": "tests.sqlmodel_models.Employee",
            "data": {"name": "Jane", "!company": {"filter": {"name": "Acme"}}},
        }
    )
    session.commit()

    employee = session.scalars(
        select(Employee).where(Employee.name == "Jane")
    ).one()
    assert employee.company.name == "Acme"


def test_hybrid_seeder_filter_on_fk_column(session):
    # Filtering on the FK *column* attribute exercises
    # attribute.referenced_class's __tablename__-based registry lookup —
    # SQLModel auto-generates __tablename__, so this is the likeliest
    # divergence point.
    HybridSeeder(session).seed(
        {"model": "tests.sqlmodel_models.Company", "data": {"name": "ColCo"}}
    )
    session.commit()

    HybridSeeder(session).seed(
        {
            "model": "tests.sqlmodel_models.Employee",
            "data": {"name": "Bob Ref", "!company_id": {"filter": {"name": "ColCo"}}},
        }
    )
    session.commit()

    employee = session.scalars(
        select(Employee).where(Employee.name == "Bob Ref")
    ).one()
    assert employee.company.name == "ColCo"


def test_non_table_sqlmodel_class_is_rejected(session):
    with pytest.raises(errors.UnsupportedClassError):
        Seeder(session).seed(
            {"model": "tests.sqlmodel_models.Plain", "data": {"name": "x"}}
        )


def test_csv_seeding_with_sqlmodel_model(tmp_path, session):
    csv_file = tmp_path / "company.csv"
    csv_file.write_text("name\nCsvCo\n", encoding="utf-8")

    entities = load_path(str(csv_file), "tests.sqlmodel_models.Company")
    Seeder(session).seed(entities)
    session.commit()

    assert session.scalars(select(Company)).one().name == "CsvCo"


def test_hybrid_filter_is_warning_free_on_sqlmodel_session(session):
    # sqlmodel.Session deprecates .query(); the seeder must not call it, or
    # every FastAPI user's test run fills with DeprecationWarnings from
    # inside this library.
    HybridSeeder(session).seed(
        {"model": "tests.sqlmodel_models.Company", "data": {"name": "WarnFree"}}
    )
    session.commit()

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        HybridSeeder(session).seed(
            {
                "model": "tests.sqlmodel_models.Employee",
                "data": {
                    "name": "Quiet",
                    "!company": {"filter": {"name": "WarnFree"}},
                },
            }
        )
