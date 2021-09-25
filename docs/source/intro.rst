Introduction
============

sqlalchemyseed is a SQLAlchemy seeder that supports nested relationships
with an easy to read text files.

Supported file types.

- json
- yaml
- csv

Example of json file

.. code-block :: json

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


Installation
------------

Default installation ::

    pip install sqlalchemyseed

When using yaml to load entities from yaml files,
execute this command to install necessary dependencies ::

    pip install sqlalchemyseed[yaml]