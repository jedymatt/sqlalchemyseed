Command-line usage
==================

Seed a database directly from data files without writing any Python, using the
``sqlalchemyseed`` command that ships with the package.

.. code-block:: shell

    sqlalchemyseed data.json --url sqlite:///app.db

The command accepts one or more files and/or directories. A directory seeds
every ``.json``/``.yaml``/``.yml`` file inside it, in sorted order:

.. code-block:: shell

    sqlalchemyseed seeds/ --url "$DATABASE_URL"
    sqlalchemyseed a.json b.yaml --url sqlite:///app.db

The database URL may be passed with ``--url`` or the ``DATABASE_URL``
environment variable. Model paths in the data files (for example
``models.Person``) are resolved against the current working directory, so run
the command from your project root.

Options
-------

- ``--url`` — SQLAlchemy database URL (defaults to the ``DATABASE_URL`` environment variable).
- ``--seeder hybrid`` — use ``HybridSeeder`` instead of the default ``Seeder``.
- ``--model models.Person`` — required for CSV inputs, which are not self-describing.
- ``--ref-prefix`` — override the relationship reference prefix (default ``!``).
- ``--dry-run`` — seed inside a transaction, then roll back (validate without writing).

The same command is available as a module:

.. code-block:: shell

    python -m sqlalchemyseed data.json --url sqlite:///app.db
