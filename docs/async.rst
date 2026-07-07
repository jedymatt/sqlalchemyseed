Async usage
===========

If your application uses an :class:`~sqlalchemy.ext.asyncio.AsyncSession`
instead of a synchronous ``Session``, use the async seeders. ``AsyncSeeder``
and ``AsyncHybridSeeder`` mirror :class:`~sqlalchemyseed.seeder.Seeder` and
:class:`~sqlalchemyseed.seeder.HybridSeeder`: they accept the same entities and
expose the same ``instances`` property, but their ``seed`` method is awaitable.

Under the hood they run the existing synchronous seeding logic through
:meth:`~sqlalchemy.ext.asyncio.AsyncSession.run_sync`, so a ``filter`` key still
issues a real query --
executed against your async driver -- during the seed traversal.

Installation
------------

Install the ``async`` extra (which pulls in greenlet, required by SQLAlchemy's
asyncio support) together with an async driver such as ``aiosqlite`` or
``asyncpg``:

.. code-block:: shell

    pip install "sqlalchemyseed[async]" aiosqlite

AsyncSeeder
-----------

.. code-block:: python

    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemyseed import AsyncSeeder

    engine = create_async_engine("sqlite+aiosqlite:///app.db")

    data = {
        "model": "models.Company",
        "data": {
            "name": "MyCompany",
            "!employees": [
                {"data": {"name": "Alice"}},
                {"data": {"name": "Bob"}},
            ],
        },
    }

    async with AsyncSession(engine) as session:
        seeder = AsyncSeeder(session, ref_prefix="!")
        await seeder.seed(data)
        await session.commit()

AsyncHybridSeeder
-----------------

Use ``AsyncHybridSeeder`` when the entities contain a ``filter`` key, just as
you would reach for :class:`~sqlalchemyseed.seeder.HybridSeeder` in synchronous
code.

.. code-block:: python

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemyseed import AsyncHybridSeeder

    data = {
        "model": "models.Employee",
        "data": {
            "name": "Carol",
            "!company": {  # references an existing row
                "model": "models.Company",
                "filter": {"name": "Acme"},
            },
        },
    }

    async with AsyncSession(engine) as session:
        seeder = AsyncHybridSeeder(session)
        await seeder.seed(data)
        await session.commit()

.. note::
    The async seeders are only importable when SQLAlchemy's asyncio support
    (greenlet) is installed. Without it, the rest of ``sqlalchemyseed`` still
    imports normally -- only ``AsyncSeeder`` and ``AsyncHybridSeeder`` are
    unavailable.
