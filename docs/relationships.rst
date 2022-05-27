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
