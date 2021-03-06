Introduction
============

`sqlalchemyseed`_ is a SQLAlchemy seeder that supports nested relationships
with an easy to read text files.

Supported file types :

- json
- yaml
- csv

.. _sqlalchemyseed: https://github.com/jedymatt/sqlalchemyseed

Installation
------------

Default installation

.. code-block:: shell

    pip install sqlalchemyseed

When using yaml to load entities from yaml files,
execute this command to install necessary dependencies

.. code-block:: shell

    pip install sqlalchemyseed[yaml]

Dependencies
------------

- Required dependencies:
    - SQAlchemy>=1.4.0
- Optional dependencies:
    - yaml: PyYAML>=5.4.0

Quickstart
----------

Here's a simple snippet to get started from ``main.py`` file.

.. code-block:: python

    from sqlalchemyseed import load_entities_from_json
    from sqlalchemyseed import Seeder
    from db import session

    # load entities
    entities = load_entities_from_json('data.json')

    # Initializing Seeder
    seeder = Seeder(session)

    # Seeding
    seeder.seed(entities)

    # Committing
    session.commit()  # or seeder.session.commit()


And the ``data.json`` file.

.. code-block:: json
    
    {
        "model": "models.Person",
        "data": [
            {
                "name": "John March",
                "age": 23
            },
            {
                "name": "Juan Dela Cruz",
                "age": 21
            }
        ]
    }
