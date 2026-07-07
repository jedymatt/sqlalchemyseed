Testing with pytest
===================

Installing ``sqlalchemyseed`` alongside `pytest`_ registers a plugin that loads
fixture files into a transactionally-isolated session. You provide a single
``engine`` fixture; the plugin supplies ``sqlalchemyseed_session`` (rolled back
after every test) and a ``seed`` factory.

.. _pytest: https://docs.pytest.org/

The plugin is registered automatically through a ``pytest11`` entry point — no
configuration is required. ``pytest`` is only needed for testing; it is not a
runtime dependency of the library.

Setup
-----

Define one ``engine`` fixture in your ``conftest.py`` that returns a SQLAlchemy
``Engine`` with your schema created.

.. code-block:: python

    # conftest.py
    import pytest
    from sqlalchemy import create_engine, event
    from sqlalchemy.pool import StaticPool

    from myapp.models import Base


    @pytest.fixture(scope="session")
    def engine():
        # StaticPool keeps a single in-memory connection alive so the schema
        # you create is visible to the test session. A file-based or server
        # database needs no such tweak -- just return your usual engine.
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # SQLite only: hand transaction control to SQLAlchemy so an explicit
        # commit() inside a test lands on a savepoint and is rolled back with
        # the outer transaction. Left to itself the pysqlite driver commits
        # straight to the database and the per-test rollback cannot undo it.
        # Other databases (PostgreSQL, MySQL) need neither listener.
        @event.listens_for(engine, "connect")
        def _sqlite_no_driver_begin(dbapi_connection, connection_record):
            dbapi_connection.isolation_level = None

        @event.listens_for(engine, "begin")
        def _sqlite_emit_begin(connection):
            connection.exec_driver_sql("BEGIN")

        Base.metadata.create_all(engine)
        return engine

Writing a test
--------------

Request the ``seed`` factory and seed a data file. Every test runs inside a
transaction that is rolled back afterward, so tests never see each other's rows.

.. code-block:: python

    # test_people.py
    from sqlalchemy import select

    from myapp.models import Person


    def test_people_are_seeded(seed, sqlalchemyseed_session):
        seeder = seed("tests/data/people.yaml")
        people = sqlalchemyseed_session.scalars(select(Person)).all()
        assert len(people) == 2
        assert seeder.instances[0].name == "Alice"

Fixtures
--------

The plugin adds three fixtures.

``engine``
    You provide this in your ``conftest.py``. It is the single integration
    point: an ``Engine`` with the schema already
    created. If you forget to define it, the plugin raises an error explaining
    exactly what to add.

``sqlalchemyseed_session``
    A ``Session`` bound to an open transaction that is
    rolled back after each test. Request it whenever a test needs to query the
    database. You can override it in your own ``conftest.py`` if you manage
    sessions yourself.

``seed``
    A callable that loads a data file and seeds it into
    ``sqlalchemyseed_session``, returning the seeder so ``.instances`` is
    available:

    .. code-block:: python

        seed(path, *, model=None, seeder="basic", ref_prefix="!")

    - ``path`` — a ``.json``, ``.yaml``/``.yml``, or ``.csv`` file.
    - ``model`` — required for CSV inputs, which are not self-describing,
      for example ``seed("people.csv", model="myapp.models.Person")``.
    - ``seeder`` — ``"hybrid"`` to use ``HybridSeeder`` instead of the
      default ``Seeder``.
    - ``ref_prefix`` — override the relationship reference prefix (default ``!``).

How isolation works
-------------------

The ``sqlalchemyseed_session`` fixture opens a connection-level transaction and
binds a session to it with ``join_transaction_mode="create_savepoint"``. Any
commit issued during the test lands on a savepoint inside that transaction, and
the transaction is rolled back when the test finishes. Nothing is written to the
database permanently, and there is no per-test schema teardown, so the tests
stay fast and leave the database pristine.

For an explicit ``commit()`` to be caught by the savepoint, SQLAlchemy must
control the transaction boundaries. On SQLite the ``pysqlite`` driver manages
``BEGIN`` itself by default, so the ``connect``/``begin`` event listeners in the
``engine`` fixture above are required — without them a committed row escapes the
rollback. Seeded data (which is flushed, never committed) rolls back regardless.
Other databases such as PostgreSQL and MySQL need no such listeners.

.. note::

    The plugin registers fixtures named ``engine``, ``sqlalchemyseed_session``,
    and ``seed``. Defining your own ``engine`` fixture is how you plug in your
    database; if you already use those names for something else, your
    definitions take precedence (pytest resolves ``conftest`` fixtures over
    plugin fixtures).
