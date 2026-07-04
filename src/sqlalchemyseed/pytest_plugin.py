"""pytest plugin: file-based SQLAlchemy fixtures with per-test rollback.

Registered via the ``pytest11`` entry point. Defines fixtures only — importing
this module has no side effects, and it is never imported by the package's
``__init__`` so production imports never pull in pytest.
"""

import pytest
from sqlalchemy.orm import Session

from .loader import load_path
from .seeder import HybridSeeder, Seeder

_MISSING_ENGINE_MESSAGE = (
    "sqlalchemyseed's pytest plugin requires an 'engine' fixture. Define one in "
    "your conftest.py that returns a SQLAlchemy Engine with your schema created, "
    "e.g.:\n\n"
    "    @pytest.fixture(scope='session')\n"
    "    def engine():\n"
    "        engine = create_engine('sqlite://')\n"
    "        Base.metadata.create_all(engine)\n"
    "        return engine\n"
)


@pytest.fixture
def engine():
    """Placeholder the user overrides in their conftest with a real Engine."""
    raise RuntimeError(_MISSING_ENGINE_MESSAGE)


@pytest.fixture
def sqlalchemyseed_session(engine):
    """A Session in an open transaction that is rolled back after the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def seed(sqlalchemyseed_session):
    """Return a callable that seeds a data file into the test session."""
    def _seed(path, *, model=None, seeder="basic", ref_prefix="!"):
        entities = load_path(path, model)
        seeder_cls = HybridSeeder if seeder == "hybrid" else Seeder
        instance = seeder_cls(sqlalchemyseed_session, ref_prefix=ref_prefix)
        instance.seed(entities)
        sqlalchemyseed_session.flush()
        return instance

    return _seed
