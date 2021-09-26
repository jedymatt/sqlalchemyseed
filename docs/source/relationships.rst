Referencing Relationships
==========================

To add reference attribute,
add prefix to the attribute to differentiate reference attribute from normal ones.

.. code-block:: json

    {
        "model": "models.Employee",
        "data": {
            "name": "John Smith",
            "!company": {
                "model": "models.Company",
                "data": {
                    "name": "MyCompany"
                }
            }
        }
    }

Base on the example above, **name** is a normal attribute and **!company** is a reference attribute
which translates to ``Employee.name`` and ``Employee.company``, respectively.

.. note:: 
    The default reference prefix is ``!`` and can be customized.

Customizing reference prefix
----------------------------

If you want ``@`` as prefix,
you can just specify it to what seeder you use by
assigning value of ``Seeder.ref_prefix`` or ``HybridSeeeder.ref_prefix``.
Default value is ``!``

.. code-block:: python

    seeder = Seeder(session, ref_prefix='@')
    # or
    seeder = Seeder(session)
    seeder.ref_prefix = '@'
    

Seeder vs. HybridSeeder
-----------------------

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Features & Options
      - Seeder
      - HybridSeeder
    
    * - Support ``model`` and ``data`` keys
      - ✔️
      - ✔️
    
    * - Support ``model`` and ``filter`` keys
      - ❌
      - ✔️
    
    * - Optional argument ``add_to_session=False`` in the ``seed`` method
      - ✔️
      - ❌

When to use HybridSeeder and 'filter' key field?
------------------------------------------------

Assuming that ``Child(age=5)`` exists in the database or session,
then we should use ``filter`` instead of ``data`` key.

The values from ``filter`` will query from the database or session,
and get the result then assign it to the ``Parent.child``

.. code-block:: python

    from sqlalchemyseed import HybridSeeder
    from db import session

    data = {
        "model": "models.Parent",
        "data": {
            "!child": { # '!' is the reference prefix
                "model": "models.Child",
                "filter": {
                    "age": 5
                }
            }
        }
    }

    # When seeding instances that has 'filter' key,
    # then use HybridSeeder, otherwise use Seeder.
    seeder = HybridSeeder(session, ref_prefix='!') 
    seeder.seed(data)

    session.commit()  # or seeder.sesssion.commit()

.. note::
    ``filter`` key is dependent to HybridSeeder in order to perform correctly.

Types of reference attributes
-----------------------------

Reference attribute types:

- foreign key attribute
- relationship attribute

You can reference a foreign key and relationship attribute in the same way.
For example:

.. code-block:: python

    from sqlalchemyseed import HybridSeeder
    from db import session

    instance = {
            'model': 'tests.models.Employee',
            'data': [
                {
                    'name': 'John Smith',
                    '!company_id': {  # this is the foreign key attribute
                        'model': 'tests.models.Company',
                        'filter': {
                            'name': 'MyCompany'
                        }
                    }
                },
                {
                    'name': 'Juan Dela Cruz',
                    '!company': { # this is the relationship attribute
                        'model': 'tests.models.Company', 
                        'filter': {
                            'name': 'MyCompany'
                        }
                    }
            ]
        }

    seeder = HybridSeeder(session)
    seeder.seed(instance)
    seeder.session.commit()

.. note::
    ``model`` can be removed if the attribute is a reference attribute like this:

    .. code-block:: json

        {
            "model": "models.Employee",
            "data": {
                "name": "Juan Dela Cruz",
                "!company": {
                    "data": {
                        "name": "Juan's Company"
                    }
                }
            }
        }
    
    Notice above that ``model`` is removed in ``!company``.
