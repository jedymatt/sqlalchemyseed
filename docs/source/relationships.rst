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
    
    Reference attribute can either be foreign key or relationship attribute.

Customizing prefix
------------------
If you want ``@`` as prefix,
you can just specify it to what seeder you use by
adding ``ref_prefix='@'`` in the argument when initializing a seeder class.

.. code-block:: python

    seeder = Seeder(session, ref_prefix='@')
    