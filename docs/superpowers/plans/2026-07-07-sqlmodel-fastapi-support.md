# SQLModel & FastAPI Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove and document first-class SQLModel/FastAPI compatibility: compat tests in CI, a warning-free `HybridSeeder` under `sqlmodel.Session`, a FastAPI docs page, and README positioning — shipped as v2.6.0.

**Architecture:** SQLModel `table=True` classes are genuine SQLAlchemy mapped classes, so no shim is needed — the work is a dedicated compat test module (`tests/test_sqlmodel.py`), one behavior-preserving runtime change (legacy `session.query()` → 2.0-style `select()` in `HybridSeeder._setup_filter_instance`), packaging/CI wiring, and docs.

**Tech Stack:** Python ≥3.10, SQLAlchemy ≥2.0, sqlmodel ≥0.0.22 (test-only dependency), uv, pytest 9 (pytester for plugin tests), Sphinx/furo docs.

**Spec:** `docs/superpowers/specs/2026-07-07-sqlmodel-fastapi-support-design.md`. One deviation, discovered empirically during planning: sqlmodel goes in its **own dependency group** (not `dev`), excluded from the min-deps CI job via `--no-group sqlmodel`. Reason: including sqlmodel in the `lowest-direct` resolution silently lifts SQLAlchemy from 2.0.0 to ≥2.0.51 (sqlmodel 0.0.14's own floor is broken — it imports `TryCast`, absent from SQLAlchemy 2.0.0), which would gut the min-deps job's core guarantee of testing the SQLAlchemy 2.0.0 floor.

## Global Constraints

- Python floor: `>=3.10`. SQLAlchemy floor: `>=2.0`, and the min-deps CI job MUST keep resolving SQLAlchemy to 2.0.0 (verify in Task 1).
- `sqlmodel>=0.0.22`, **test dependency only** — never in `[project.dependencies]`, never as an extra.
- No new runtime API; seed-file format, CLI, and pytest plugin behavior unchanged.
- `HybridSeeder` filter semantics contract: zero matches → `NoResultFound`, multiple → `MultipleResultsFound` (`.one()`/`.scalar_one()` both satisfy this — verified empirically).
- `select(column).filter_by(**kw)` resolves attribute names against the column's table — verified empirically on SQLAlchemy 2.0.x; no `.where()` fallback needed.
- Existing 99 tests must stay green after every task.
- All work on branch `worktree-sqlmodel-fastapi-support` in this worktree; run everything with `uv run`.

---

### Task 1: sqlmodel dependency group + min-deps CI exclusion

**Files:**
- Modify: `pyproject.toml` (dependency-groups at lines 46-57, `[tool.uv]` at lines 72-73)
- Modify: `.github/workflows/python-package.yml` (min-deps job's run step)

**Interfaces:**
- Produces: importable `sqlmodel` in the default dev environment; later tasks assume `uv run pytest` has sqlmodel available and the min-deps job runs `--no-group sqlmodel`.

- [ ] **Step 1: Add the sqlmodel dependency group**

In `pyproject.toml`, after the `dev` group inside `[dependency-groups]`, add a `sqlmodel` group, and add it to `default-groups`:

```toml
[dependency-groups]
dev = [
    # 9.0.3 fixes GHSA-6w46-j5rx-g56g (tmpdir handling); it needs Python >=3.10,
    # which is now the floor.
    "pytest>=9.0.3",
    "coverage>=6.2",
    "PyYAML>=6.0",
    # Async seeder tests: aiosqlite provides an async SQLite driver, greenlet
    # backs SQLAlchemy's AsyncSession.run_sync bridge.
    "aiosqlite>=0.19",
    "greenlet>=3.0",
]
# Kept out of `dev` so the min-deps CI job can exclude it: resolving sqlmodel
# under --resolution lowest-direct drags SQLAlchemy above 2.0.0 and the job
# would silently stop testing the declared floor. 0.0.22 is the oldest release
# that works at all against SQLAlchemy 2.0.x (0.0.14 imports TryCast, which
# SQLAlchemy 2.0.0 lacks).
sqlmodel = [
    "sqlmodel>=0.0.22",
]
```

```toml
[tool.uv]
default-groups = ["dev", "sqlmodel"]
```

- [ ] **Step 2: Sync and verify sqlmodel imports**

Run: `uv sync && uv run python -c "import sqlmodel; print(sqlmodel.__version__)"`
Expected: prints a version ≥0.0.22 (0.0.39 at plan time).

- [ ] **Step 3: Exclude the group from the min-deps CI job**

In `.github/workflows/python-package.yml`, the `test-min-deps` job's last step currently reads:

```yaml
      # --resolution lowest-direct pins every direct dependency to its lowest
      # allowed version, which exercises the SQLAlchemy>=2.0 floor.
      - name: Run tests (lowest supported dependencies)
        run: uv run --resolution lowest-direct pytest
```

Change the run line (keep the comment, extend it):

```yaml
      # --resolution lowest-direct pins every direct dependency to its lowest
      # allowed version, which exercises the SQLAlchemy>=2.0 floor. The
      # sqlmodel group is excluded because sqlmodel's own SQLAlchemy pin would
      # lift the resolved SQLAlchemy above 2.0.0, defeating the floor check;
      # the sqlmodel compat tests skip themselves when sqlmodel is absent.
      - name: Run tests (lowest supported dependencies)
        run: uv run --resolution lowest-direct --no-group sqlmodel pytest
```

- [ ] **Step 4: Verify both resolutions locally**

Run: `uv run pytest -q`
Expected: `99 passed` (sqlmodel present, no compat tests yet).

Run: `uv run --python 3.10 --resolution lowest-direct --no-group sqlmodel python -c "import sqlalchemy; print(sqlalchemy.__version__)"`
Expected: `2.0.0` — the floor guarantee is intact.

Run: `uv run --python 3.10 --resolution lowest-direct --no-group sqlmodel pytest -q`
Expected: `99 passed`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .github/workflows/python-package.yml uv.lock
git commit -m "chore: add sqlmodel test dependency group, keep min-deps job on the SQLAlchemy floor"
```

---

### Task 2: SQLModel test models + core seeder compat tests

**Files:**
- Create: `tests/sqlmodel_models.py`
- Create: `tests/test_sqlmodel.py`

**Interfaces:**
- Consumes: `sqlmodel` group from Task 1; `Seeder`, `HybridSeeder`, `errors` from `sqlalchemyseed`; `load_path(path, model)` from `sqlalchemyseed.loader`.
- Produces: `tests/sqlmodel_models.py` exporting `Company`, `Employee` (table models, bidirectional relationship) and `Plain` (non-table); `tests/test_sqlmodel.py` with a function-scoped `session` fixture (`sqlmodel.Session`). Tasks 3–4 append tests to this module and reuse the fixture and models.

These are characterization tests — the smoke test during scoping showed they pass today. If any fails, STOP: that is a real compatibility bug; investigate before proceeding (do not massage the test to green).

- [ ] **Step 1: Create the SQLModel test models**

Create `tests/sqlmodel_models.py`:

```python
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
```

- [ ] **Step 2: Create the compat test module with the core tests**

Create `tests/test_sqlmodel.py`:

```python
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
```

(The `warnings` import is used by Task 3's test; leaving it now avoids churn.)

- [ ] **Step 3: Run the new tests**

Run: `uv run pytest tests/test_sqlmodel.py -v`
Expected: 6 passed. **If any test fails, STOP and investigate — that is a genuine compatibility bug, not a test to adjust.**

- [ ] **Step 4: Run the full suite**

Run: `uv run pytest -q`
Expected: `105 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/sqlmodel_models.py tests/test_sqlmodel.py
git commit -m "test: prove SQLModel compatibility for core seeding paths"
```

---

### Task 3: Migrate HybridSeeder filter queries to 2.0-style select()

**Files:**
- Modify: `src/sqlalchemyseed/seeder.py:259-307` (`_setup_instance` stale comment + `_setup_filter_instance`)
- Test: `tests/test_sqlmodel.py` (append one test)

**Interfaces:**
- Consumes: `session` fixture and models from Task 2.
- Produces: `HybridSeeder._setup_filter_instance` free of legacy `Query`; `sqlmodel.Session` no longer triggers `DeprecationWarning` from library internals. No signature changes anywhere.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_sqlmodel.py`:

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_sqlmodel.py::test_hybrid_filter_is_warning_free_on_sqlmodel_session -v`
Expected: FAIL with `DeprecationWarning: ... session.exec() instead of session.query()` raised as an error.

- [ ] **Step 3: Migrate the three query branches**

In `src/sqlalchemyseed/seeder.py`, `_setup_filter_instance` currently reads:

```python
    def _setup_filter_instance(self, class_, filtered_kwargs, parent: InstanceAttributeTuple):
        if parent is not None:
            instr_attr = instrumented_attribute(
                parent.instance, parent.attr_name)
        else:
            instr_attr = None

        if instr_attr is not None and attr_is_column(instr_attr):
            column = foreign_key_column(instr_attr)
            return self.session.query(column).filter_by(**filtered_kwargs).one()[0]

        if instr_attr is not None and attr_is_relationship(instr_attr):
            return self.session.query(referenced_class(instr_attr)).filter_by(
                **filtered_kwargs
            ).one()

        return self.session.query(class_).filter_by(**filtered_kwargs).one()
```

Replace the three query lines with 2.0-style equivalents (the module already has `import sqlalchemy` at the top; `select(column).filter_by(...)` resolves names against the column's table — verified during planning):

```python
    def _setup_filter_instance(self, class_, filtered_kwargs, parent: InstanceAttributeTuple):
        if parent is not None:
            instr_attr = instrumented_attribute(
                parent.instance, parent.attr_name)
        else:
            instr_attr = None

        if instr_attr is not None and attr_is_column(instr_attr):
            column = foreign_key_column(instr_attr)
            return self.session.execute(
                sqlalchemy.select(column).filter_by(**filtered_kwargs)
            ).one()[0]

        if instr_attr is not None and attr_is_relationship(instr_attr):
            return self.session.execute(
                sqlalchemy.select(referenced_class(instr_attr)).filter_by(**filtered_kwargs)
            ).scalar_one()

        return self.session.execute(
            sqlalchemy.select(class_).filter_by(**filtered_kwargs)
        ).scalar_one()
```

Also delete the stale commented-out line in `_setup_instance` (`seeder.py:266`):

```python
        else:  # key == key.filter()
            # instance = self.session.query(class_).filter_by(**filtered_kwargs)
            instance = self._setup_filter_instance(
```

becomes

```python
        else:  # key == key.filter()
            instance = self._setup_filter_instance(
```

- [ ] **Step 4: Run the new test, then the full suite**

Run: `uv run pytest tests/test_sqlmodel.py::test_hybrid_filter_is_warning_free_on_sqlmodel_session -v`
Expected: PASS.

Run: `uv run pytest -q`
Expected: `106 passed` — the existing hybrid-seeder tests (including the ones asserting `NoResultFound`/`MultipleResultsFound` behavior) confirm the migration is behavior-preserving.

Run: `grep -rn "session.query" src/sqlalchemyseed/`
Expected: no matches — no legacy query calls remain in the package.

- [ ] **Step 5: Commit**

```bash
git add src/sqlalchemyseed/seeder.py tests/test_sqlmodel.py
git commit -m "fix: migrate HybridSeeder filter queries to 2.0-style select()"
```

---

### Task 4: Async seeder + pytest plugin compat tests

**Files:**
- Modify: `tests/test_sqlmodel.py` (append an async test class and a pytester test)

**Interfaces:**
- Consumes: models from Task 2; `AsyncSeeder` from `sqlalchemyseed.aio`; the bundled pytest plugin's `seed`/`sqlalchemyseed_session` fixtures (registered via the `pytest11` entry point); `pytester` (enabled by `pytest_plugins = ["pytester"]` in `tests/conftest.py`, already present).
- Produces: nothing consumed later; final shape of `tests/test_sqlmodel.py` (9 tests).

- [ ] **Step 1: Append the async compat test**

Append to `tests/test_sqlmodel.py`. Style note: `unittest.IsolatedAsyncioTestCase` matches `tests/test_async_seeder.py` — the repo has no pytest-asyncio dependency, so async tests run through unittest.

```python
import unittest


class AsyncSQLModelTestCase(unittest.IsolatedAsyncioTestCase):
    """AsyncSeeder against SQLModel's own AsyncSession subclass."""

    async def test_async_seeder_with_sqlmodel_models(self):
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlmodel.ext.asyncio.session import AsyncSession

        from sqlalchemyseed.aio import AsyncSeeder

        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        session = AsyncSession(engine)
        try:
            seeder = AsyncSeeder(session)
            await seeder.seed(
                {
                    "model": "tests.sqlmodel_models.Company",
                    "data": {
                        "name": "AsyncCo",
                        "!employees": [{"data": {"name": "Async Alice"}}],
                    },
                }
            )
            await session.commit()

            company = (await session.execute(select(Company))).scalar_one()
            employee = (await session.execute(select(Employee))).scalar_one()
            self.assertEqual(company.name, "AsyncCo")
            self.assertEqual(employee.name, "Async Alice")
        finally:
            await session.close()
            await engine.dispose()
```

- [ ] **Step 2: Run the async test**

Run: `uv run pytest "tests/test_sqlmodel.py::AsyncSQLModelTestCase" -v`
Expected: 1 passed.

- [ ] **Step 3: Append the pytest-plugin-with-SQLModel test**

Append to `tests/test_sqlmodel.py`. Two deliberate choices: the inner run uses `runpytest_subprocess()` (NOT in-process `runpytest()`) because the inner `models.py` registers tables in SQLModel's process-global `SQLModel.metadata`, and an in-process re-import across tests would raise "Table already defined"; and the inner engine setup mirrors the documented SQLModel conftest from the docs page (Task 5).

```python
SQLMODEL_PLUGIN_CONFTEST = '''
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import models  # registers the tables on SQLModel.metadata


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(eng)
    return eng
'''

SQLMODEL_PLUGIN_MODELS = '''
from typing import Optional

from sqlmodel import Field, SQLModel


class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
'''


def test_pytest_plugin_with_sqlmodel_engine(pytester):
    pytester.makeconftest(SQLMODEL_PLUGIN_CONFTEST)
    pytester.makepyfile(models=SQLMODEL_PLUGIN_MODELS)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}]}',
    )
    pytester.makepyfile(
        test_inner='''
        from sqlalchemy import select
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seeder = seed("people.json")
            people = sqlalchemyseed_session.scalars(select(Person)).all()
            assert [p.name for p in people] == ["Alice"]
            assert seeder.instances[0].name == "Alice"
        '''
    )
    # Subprocess: keeps the inner models module and SQLModel's global
    # metadata out of this process.
    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
```

- [ ] **Step 4: Run the plugin test, then the full suite**

Run: `uv run pytest tests/test_sqlmodel.py::test_pytest_plugin_with_sqlmodel_engine -v`
Expected: 1 passed.

Run: `uv run pytest -q`
Expected: `108 passed`.

- [ ] **Step 5: Commit**

```bash
git add tests/test_sqlmodel.py
git commit -m "test: cover AsyncSeeder and the pytest plugin with SQLModel"
```

---

### Task 5: FastAPI & SQLModel docs page + legacy-query docs sweep

**Files:**
- Create: `docs/fastapi.rst`
- Modify: `docs/index.rst:16-26` (toctree)
- Modify: `docs/pytest.rst:64-73` (test example)
- Modify: `README.md:185-192` (same example)

**Interfaces:**
- Consumes: fixture/CLI/plugin behavior as shipped (no code changes in this task).
- Produces: `docs/fastapi.rst` referenced from `index.rst`; Task 6's README section links to the built page at `https://sqlalchemyseed.readthedocs.io/en/latest/fastapi.html`.

- [ ] **Step 1: Create `docs/fastapi.rst`**

```rst
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
attribute the model does not have raises SQLModel's raw
``AttributeError: <name>`` (plain declarative models raise ``TypeError``).
Either way the fix is the same: correct the attribute name in the seed file.

**Forgot** ``table=True`` — a SQLModel class without ``table=True`` is not a
mapped class; using it as a ``model`` raises ``UnsupportedClassError``. Add
``table=True`` to the class definition.
```

- [ ] **Step 2: Add the page to the toctree**

In `docs/index.rst`, the toctree currently ends with:

```rst
    examples
    cli
    pytest
```

Append `fastapi`:

```rst
    examples
    cli
    pytest
    fastapi
```

- [ ] **Step 3: Modernize the legacy-query examples in existing docs**

In `docs/pytest.rst` (the "Writing a test" code block, ~line 64):

```rst
.. code-block:: python

    # test_people.py
    from myapp.models import Person


    def test_people_are_seeded(seed, sqlalchemyseed_session):
        seeder = seed("tests/data/people.yaml")
        assert sqlalchemyseed_session.query(Person).count() == 2
        assert seeder.instances[0].name == "Alice"
```

becomes

```rst
.. code-block:: python

    # test_people.py
    from sqlalchemy import select

    from myapp.models import Person


    def test_people_are_seeded(seed, sqlalchemyseed_session):
        seeder = seed("tests/data/people.yaml")
        people = sqlalchemyseed_session.scalars(select(Person)).all()
        assert len(people) == 2
        assert seeder.instances[0].name == "Alice"
```

In `README.md` (~line 185), the identical `# test_people.py` example gets the identical rewrite (same code, markdown fencing).

- [ ] **Step 4: Build the docs and verify**

Run: `uv run --with-requirements docs/requirements.txt python -m sphinx -b html docs docs/_build/html 2>&1 | tail -5`
Expected: `build succeeded` (warnings about pre-existing pages are tolerable; no errors, and no warnings mentioning `fastapi.rst`).

Run: `grep -rn "session.query\|\.query(" docs/*.rst README.md`
Expected: no matches.

- [ ] **Step 5: Commit**

```bash
git add docs/fastapi.rst docs/index.rst docs/pytest.rst README.md
git commit -m "docs: add FastAPI & SQLModel page, modernize query examples"
```

---

### Task 6: README section, keywords, version 2.6.0

**Files:**
- Modify: `README.md` (new section after "## Quickstart", before "## Editor validation (JSON Schema)")
- Modify: `pyproject.toml:11` (keywords)
- Modify: `src/sqlalchemyseed/__init__.py:21` (`__version__`)

**Interfaces:**
- Consumes: docs page URL from Task 5.
- Produces: released surface for v2.6.0.

- [ ] **Step 1: Add the README section**

In `README.md`, immediately after the Quickstart section's closing code fence and before `## Editor validation (JSON Schema)`, insert:

````markdown
## Works with SQLModel & FastAPI

A [SQLModel](https://sqlmodel.tiangolo.com/) `table=True` class **is** a
SQLAlchemy model, so sqlalchemyseed works with SQLModel and FastAPI out of the
box — same seed files, same seeders, verified in CI:

```python
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine

from sqlalchemyseed import Seeder


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    seeder = Seeder(session)
    seeder.seed({"model": "app.models.Hero", "data": [{"name": "Deadpond"}]})
    session.commit()
```

Seed at app startup, in tests via the bundled pytest plugin, or from the CLI —
see the [FastAPI & SQLModel docs](https://sqlalchemyseed.readthedocs.io/en/latest/fastapi.html).
````

- [ ] **Step 2: Add PyPI keywords**

In `pyproject.toml`:

```toml
keywords = ["sqlalchemy", "orm", "seed", "seeder", "json", "yaml"]
```

becomes

```toml
keywords = ["sqlalchemy", "sqlmodel", "fastapi", "orm", "seed", "seeder", "json", "yaml"]
```

- [ ] **Step 3: Commit the README/keywords**

```bash
git add README.md pyproject.toml
git commit -m "docs: position SQLModel/FastAPI support in README and PyPI keywords"
```

- [ ] **Step 4: Bump the version**

In `src/sqlalchemyseed/__init__.py`:

```python
__version__ = "2.5.0"
```

becomes

```python
__version__ = "2.6.0"
```

- [ ] **Step 5: Final full verification**

Run: `uv sync && uv run pytest -q`
Expected: `108 passed`.

Run: `uv run --python 3.10 --resolution lowest-direct --no-group sqlmodel pytest -q`
Expected: `99 passed, 1 skipped` — `pytest.importorskip` skips `tests/test_sqlmodel.py` at collection (one skip for the whole module). The requirement is 0 failed, 0 errors, with the sqlmodel tests skipping rather than failing.

- [ ] **Step 6: Commit the bump**

```bash
git add src/sqlalchemyseed/__init__.py uv.lock
git commit -m "chore: bump version to 2.6.0"
```

---

## Post-merge follow-through (not plan tasks)

After the PR merges and v2.6.0 is released (release workflow publishes on GitHub release): check off the SQLModel/FastAPI item in issue #65 — the last Tier 1 item — and update its "Next up" to the Alembic data-migration helper.
