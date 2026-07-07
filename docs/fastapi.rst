FastAPI & SQLModel
==================

`SQLModel <https://sqlmodel.tiangolo.com/>`_ table models **are** SQLAlchemy
models — a class declared with ``table=True`` is a regular SQLAlchemy mapped
class underneath. sqlalchemyseed therefore works with SQLModel and FastAPI
out of the box: the same seed files, the same seeders, the same CLI and
pytest plugin. This page shows the FastAPI-shaped entry points.

Requires ``sqlmodel>=0.0.22`` (older releases pin a SQLAlchemy version this
library does not support).

Models and seed files
---------------------

Point the ``model`` key at your SQLModel class, exactly as you would for a
declarative model. ``sqlmodel.Session`` subclasses
``sqlalchemy.orm.Session``, so seeders accept it directly.

.. code-block:: python

    # app/models.py
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

.. code-block:: yaml

    # seeds/employees.yaml
    model: app.models.Employee
    data:
      - name: John Smith
        '!company':
          model: app.models.Company
          data:
            name: MyCompany

.. code-block:: python

    from sqlmodel import Session, create_engine

    from sqlalchemyseed import Seeder, load_entities_from_yaml

    engine = create_engine("sqlite:///database.db")

    with Session(engine) as session:
        seeder = Seeder(session)
        seeder.seed(load_entities_from_yaml("seeds/employees.yaml"))
        session.commit()

Seeding on application startup
------------------------------

For demo or development data, seed inside FastAPI's lifespan hook:

.. code-block:: python

    from contextlib import asynccontextmanager

    from fastapi import FastAPI
    from sqlmodel import Session, SQLModel, create_engine

    from sqlalchemyseed import Seeder, load_entities_from_yaml

    engine = create_engine("sqlite:///database.db")


    @asynccontextmanager
    async def lifespan(app: FastAPI):
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            seeder = Seeder(session)
            seeder.seed(load_entities_from_yaml("seeds/employees.yaml"))
            session.commit()
        yield


    app = FastAPI(lifespan=lifespan)

For production reference data, prefer running the :doc:`CLI <cli>` in your
deploy or container entrypoint instead of the application process.

Testing FastAPI apps
--------------------

The bundled :doc:`pytest plugin <pytest>` works unchanged; only the
``engine`` fixture differs — build the schema from ``SQLModel.metadata``:

.. code-block:: python

    # conftest.py
    import pytest
    from sqlalchemy.pool import StaticPool
    from sqlmodel import SQLModel, create_engine

    import app.models  # noqa: F401 — registers tables on SQLModel.metadata


    @pytest.fixture(scope="session")
    def engine():
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        return engine

.. code-block:: python

    # test_people.py
    from sqlalchemy import select

    from app.models import Employee


    def test_employees_are_seeded(seed, sqlalchemyseed_session):
        seed("seeds/employees.yaml")
        employee = sqlalchemyseed_session.scalars(select(Employee)).one()
        assert employee.company.name == "MyCompany"

Every test runs in a transaction that is rolled back afterward — see
:doc:`pytest` for the full fixture reference.

Command line
------------

Model paths in seed files (and ``--model`` for CSV) resolve SQLModel classes
like any other:

.. code-block:: console

    $ sqlalchemyseed seeds/ --url sqlite:///database.db
    $ sqlalchemyseed people.csv --model app.models.Employee --url sqlite:///database.db

Async
-----

``AsyncSeeder`` and ``AsyncHybridSeeder`` accept SQLModel's async session —
see :doc:`async`:

.. code-block:: python

    from sqlmodel.ext.asyncio.session import AsyncSession

    from sqlalchemyseed import AsyncSeeder

    async def seed_db(engine):
        async with AsyncSession(engine) as session:
            seeder = AsyncSeeder(session)
            await seeder.seed(load_entities_from_yaml("seeds/employees.yaml"))
            await session.commit()

Troubleshooting
---------------

**Unknown attribute raises** ``AttributeError`` — a seed file naming an
attribute the model does not have raises ``AttributeError`` for SQLModel
and plain declarative models alike. The fix is the same either way:
correct the attribute name in the seed file.

**Forgot** ``table=True`` — a SQLModel class without ``table=True`` is not a
mapped class; using it as a ``model`` raises ``UnsupportedClassError``. Add
``table=True`` to the class definition.
