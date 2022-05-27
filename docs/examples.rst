Examples
========

json
----

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

yaml
----

.. code-block:: yaml

    model: models.Person
    data:
        - name: John March
          age: 23
        - name: Juan Dela Cruz
          age: 21

csv
---

In line one, name and age,
are attributes of a model that will be specified when loading the file.

.. code-block:: none

    name, age
    John March, 23
    Juan Dela Cruz, 21

To load a csv file

.. code-block:: python

    # second argument, model, accepts class
    load_entities_from_csv("people.csv", models.Person)
    # or string
    load_entities_from_csv("people.csv", "models.Person")

.. note::
    csv does not support referencing relationships.


No Relationship
---------------

.. code-block:: json

    [
        {
            "model": "models.Person",
            "data": {
                "name": "You",
                "age": 18
            }
        },
        {
            "model": "models.Person",
            "data": [
                {
                    "name": "You",
                    "age": 18
                },
                {
                    "name": "Still You But Older",
                    "age": 40
                }
            ]
        }
    ]


One to One Relationship
-----------------------

.. code-block:: json

    [
        {
            "model": "models.Person",
            "data": {
                "name": "John",
                "age": 18,
                "!job": {
                    "model": "models.Job",
                    "data": {
                        "job_name": "Programmer",
                    }
                }
            }
        },
        {
            "model": "models.Person",
            "data": {
                "name": "Jeniffer",
                "age": 18,
                "!job": {
                    "model": "models.Job",
                    "filter": {
                        "job_name": "Programmer",
                    }
                }
            }
        }
    ]

One to Many Relationship
------------------------

.. code-block:: json
    
    [
        {
            "model": "models.Person",
            "data": {
                "name": "John",
                "age": 18,
                "!items": [
                    {
                        "model": "models.Item",
                        "data": {
                            "name": "Pencil"
                        }
                    },
                    {
                        "model": "models.Item",
                        "data": {
                            "name": "Eraser"
                        }
                    }
                ]
            }
        }
    ]

Nested Relationships

.. code-block:: json
    
    {
        "model": "models.Parent",
        "data": {
            "name": "John Smith",
            "!children": [
                {
                    "model": "models.Child",
                    "data": {
                        "name": "Mark Smith",
                        "!children": [
                            {
                                "model": "models.GrandChild",
                                "data": {
                                    "name": "Alice Smith"
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
