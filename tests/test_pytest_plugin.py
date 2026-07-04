"""Tests for the bundled pytest plugin, exercised via the pytester fixture."""

# A self-contained conftest for the inner pytest runs. StaticPool keeps a
# single in-memory SQLite connection alive so create_all and the session share
# one database.
CONFTEST = '''
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from models import Base


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Hand transaction control to SQLAlchemy so an explicit commit() inside a
    # test lands on a savepoint and is rolled back with the outer transaction.
    # Left to itself the pysqlite driver commits straight to the database and
    # the per-test rollback cannot undo it.
    @event.listens_for(eng, "connect")
    def _sqlite_no_driver_begin(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(eng, "begin")
    def _sqlite_emit_begin(connection):
        connection.exec_driver_sql("BEGIN")

    Base.metadata.create_all(eng)
    return eng
'''

MODELS = '''
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    employees = relationship("Employee", back_populates="company")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="employees")
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


def test_committed_writes_still_roll_back(pytester):
    # The point of join_transaction_mode="create_savepoint": even an explicit
    # commit() lands on a savepoint inside the outer transaction and is unwound
    # by the teardown rollback. This pins the documented contract that the
    # flush-only seed path (test_rollback_isolation) does not exercise.
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}]}',
    )
    pytester.makepyfile(
        test_commit_isolation='''
        from models import Person

        def test_first_commits(seed, sqlalchemyseed_session):
            seed("people.json")
            sqlalchemyseed_session.commit()
            assert sqlalchemyseed_session.query(Person).count() == 1

        def test_second_sees_empty_db(sqlalchemyseed_session):
            # The committed row was still rolled back with the outer transaction.
            assert sqlalchemyseed_session.query(Person).count() == 0
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_reference_resolution_default_prefix(pytester):
    # A "!"-prefixed key is a relationship reference; the seeder wires the
    # nested Company onto the Employee. Guards the default ref_prefix.
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        employee=(
            '{"model": "models.Employee", "data": {"name": "Juan", '
            '"!company": {"model": "models.Company", "data": {"name": "Acme"}}}}'
        ),
    )
    pytester.makepyfile(
        test_reference='''
        from models import Company, Employee

        def test_it(seed, sqlalchemyseed_session):
            seed("employee.json")
            employee = sqlalchemyseed_session.query(Employee).one()
            assert employee.company.name == "Acme"
            assert sqlalchemyseed_session.query(Company).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_custom_ref_prefix(pytester):
    # A non-default prefix ("@") must be threaded through to the seeder so the
    # "@company" key is treated as a reference rather than a column.
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        employee=(
            '{"model": "models.Employee", "data": {"name": "Mia", '
            '"@company": {"model": "models.Company", "data": {"name": "Globex"}}}}'
        ),
    )
    pytester.makepyfile(
        test_prefix='''
        from models import Employee

        def test_it(seed, sqlalchemyseed_session):
            seed("employee.json", ref_prefix="@")
            employee = sqlalchemyseed_session.query(Employee).one()
            assert employee.company.name == "Globex"
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_multiple_seed_calls_accumulate(pytester):
    # Seeding several files in one test is a first-class use case; each call
    # builds a fresh seeder on the shared session and flushes.
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        alice='{"model": "models.Person", "data": [{"name": "Alice"}]}',
        others='{"model": "models.Person", "data": [{"name": "Bob"}, {"name": "Carol"}]}',
    )
    pytester.makepyfile(
        test_multi='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seed("alice.json")
            seed("others.json")
            assert sqlalchemyseed_session.query(Person).count() == 3
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


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
    # A minimal session suffices here — this test proves override precedence,
    # not the production fixture's transaction handling.
    pytester.makepyfile(
        test_override='''
        import pytest
        from sqlalchemy.orm import Session
        from models import Person

        @pytest.fixture
        def sqlalchemyseed_session(engine):
            session = Session(bind=engine)
            session.info["overridden"] = True
            yield session
            session.close()

        def test_it(seed, sqlalchemyseed_session):
            seed("people.json")
            assert sqlalchemyseed_session.info.get("overridden") is True
            assert sqlalchemyseed_session.query(Person).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_unsupported_file_type_fails_loudly(pytester):
    _scaffold(pytester)
    pytester.makefile(".txt", data="nope")
    pytester.makepyfile(
        test_unsupported='''
        import pytest

        def test_it(seed):
            with pytest.raises(ValueError):
                seed("data.txt")
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
