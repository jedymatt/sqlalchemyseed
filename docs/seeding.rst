Seeding
=======

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