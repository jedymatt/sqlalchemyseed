"""Tests for the bundled pytest plugin, exercised via the pytester fixture."""

# A self-contained conftest for the inner pytest runs. StaticPool keeps a
# single in-memory SQLite connection alive so create_all and the session share
# one database.
CONFTEST = '''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from models import Base


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    return eng
'''

MODELS = '''
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
'''


def _scaffold(pytester):
    """Write the shared conftest + models module into the inner project."""
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(models=MODELS)


def test_seed_json(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}, {"name": "Bob"}]}',
    )
    pytester.makepyfile(
        test_seed_json='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seeder = seed("people.json")
            assert sqlalchemyseed_session.query(Person).count() == 2
            assert seeder.instances[0].name == "Alice"
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_seed_yaml(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".yaml",
        people="model: models.Person\ndata:\n  - name: Carol\n",
    )
    pytester.makepyfile(
        test_seed_yaml='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seed("people.yaml")
            assert sqlalchemyseed_session.query(Person).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_seed_csv_with_model(pytester):
    _scaffold(pytester)
    pytester.makefile(".csv", people="name\nDave\nErin\n")
    pytester.makepyfile(
        test_seed_csv='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seed("people.csv", model="models.Person")
            assert sqlalchemyseed_session.query(Person).count() == 2
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_hybrid_seeder(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}]}',
    )
    pytester.makepyfile(
        test_hybrid='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seeder = seed("people.json", seeder="hybrid")
            assert sqlalchemyseed_session.query(Person).count() == 1
            assert seeder.instances[0].name == "Alice"
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_rollback_isolation(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}, {"name": "Bob"}]}',
    )
    pytester.makepyfile(
        test_isolation='''
        from models import Person

        def test_first_seeds(seed, sqlalchemyseed_session):
            seed("people.json")
            assert sqlalchemyseed_session.query(Person).count() == 2

        def test_second_sees_empty_db(sqlalchemyseed_session):
            # The prior test's rows were rolled back with its transaction.
            assert sqlalchemyseed_session.query(Person).count() == 0
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_missing_engine_gives_actionable_error(pytester):
    # Deliberately no conftest / engine fixture.
    pytester.makepyfile(
        test_no_engine='''
        def test_it(seed):
            pass
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*requires an 'engine' fixture*"])


def test_user_can_override_session(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Zoe"}]}',
    )
    # Override the plugin's session fixture; seed must use the override.
    pytester.makepyfile(
        test_override='''
        import pytest
        from sqlalchemy.orm import Session
        from models import Person

        @pytest.fixture
        def sqlalchemyseed_session(engine):
            connection = engine.connect()
            transaction = connection.begin()
            session = Session(bind=connection, join_transaction_mode="create_savepoint")
            session.info["overridden"] = True
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
                connection.close()

        def test_it(seed, sqlalchemyseed_session):
            seed("people.json")
            assert sqlalchemyseed_session.info.get("overridden") is True
            assert sqlalchemyseed_session.query(Person).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
