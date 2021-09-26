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