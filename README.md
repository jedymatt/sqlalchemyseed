# sqlalchemyseed

[![PyPI](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)
[![Python package](https://github.com/jedymatt/sqlalchemyseed/actions/workflows/python-package.yml/badge.svg)](https://github.com/jedymatt/sqlalchemyseed/actions/workflows/python-package.yml)

Sqlalchemy seeder that supports nested relationships.

## Installation

```commandline
pip install sqlalchemyseed
```

### Dependencies

- SQAlchemy>=1.4.0

## Getting Started

```python
# main.py
from sqlalchemyseed import load_entities_from_json, Seeder
from db import session

# load entities
entities = load_entities_from_json('tests/test_data.json')

# Initializing Seeder
seeder = Seeder()  # or Seeder(session)

# Seeding
seeder.session = session  # assign session if no session assigned before seeding
seeder.seed(entities)

# Committing
session.commit()  # or seeder.session.commit()
```

## Seeder vs. HybridSeeder

| Features & Options                                                     | Seeder             | HybridSeeder       |
| :--------------------------------------------------------------------- | :----------------- | :----------------- |
| Support `model` and `data` keys                                        | :heavy_check_mark: | :heavy_check_mark: |
| Support `model` and `filter` keys                                      | :x:                | :heavy_check_mark: |
| Optional argument `add_to_session=False` in the `seed` method          | :heavy_check_mark: | :x:                |
| Assign existing objects from session or db to a relationship attribute | :x:                | :heavy_check_mark: |

## When to use HybridSeeder and 'filter' key field?

Assuming that `Child(age=5)` exists in the database or session,
then we should use *filter* instead of *data*,
the values of *filter* will query from the database or session,
and assign it to the `Parent.child`

```python
from sqlalchemyseed import HybridSeeder
from db import session

data = {
    "model": "models.Parent",
    "data": {
        "!child": {
            "model": "models.Child",
            "filter": {
                "age": 5
            }
        }
    }
}


# When seeding instances that has 'filter' key, then use HybridSeeder, otherwise use Seeder.
seeder = HybridSeeder(session)
seeder.seed(data)

session.commit() # or seeder.sesssion.commit()
```

## Relationships

In adding a relationship attribute, add prefix **!** to the key in order to identify it.

### Referencing relationship object or a foreign key

If your class don't have a relationship attribute but instead a foreign key attribute you can use it the same as how you did it on a relationship attribute

```python
from sqlalchemyseed import HybridSeeder
from db import session

instance = [
    {
        'model': 'tests.models.Company',
        'data': {'name': 'MyCompany'}
    },
    {
        'model': 'tests.models.Employee',
        'data':[  
            {
                'name': 'John Smith',
                # foreign key attribute
                '!company_id': {
                    'model': 'tests.models.Company',
                    'filter': {
                        'name': 'MyCompany'
                    }
                }
            },
            {
                'name': 'Juan Dela Cruz',
                # relationship attribute
                '!company': {
                    'model': 'tests.models.Company',
                    'filter': {
                        'name': 'MyCompany'
                    }
            }
        ]
    }
]

seeder = HybridSeeder(session)
seeder.seed(instance)
```

### No Relationship

```json5
// test_data.json
[
    {
        "model": "models.Person",
        "data": {
            "name": "You",
            "age": 18
        }
    },
    // when you have two or more objects of the same model, you can
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
```

### One to One

```json5
// test_data.json
[
    {
        "model": "models.Person",
        "data": {
            "name": "John",
            "age": 18,
            // creates a job object
            "!job": {
                "model": "models.Job",
                "data": {
                    "job_name": "Programmer",
                }
            }
        }
    },
    // or this, if you want to add relationship that exists
    // in your database use 'filter' instead of 'obj'
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
```

### One to Many

```json5
//test_data.json
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
```

### Example of Nested Relationships

```json
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
```
