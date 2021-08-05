# sqlalchemyseed

[![PyPI](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)

Sqlalchemy seeder. Supports nested relationships.

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
from tests.db import session

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

- Seeder supports model and data key fields.
- Seeder does not support model and filter key fields.
- HybridSeeder supports model and data, and model and filter key fields.
- HybridSeeder enables to query existing objects from the session and assigns it with the relationship.

## When to use HybridSeeder and 'filter' key field?

```python

from sqlalchemyseed import HybridSeeder
from tests.db import session

data = {
    "model": "models.Parent",
    "obj": {
        "child": {
            "model": "models.Child",
            "filter": {
                "age": 5
            }
        }
    }
}

# Assuming that Child(age=5) exists in the database or session,
#  then we should use 'filter' instead of 'obj'

# When seeding instances that has 'filter' key, then use HybridSeeder, otherwise use Seeder.
seeder = HybridSeeder(session)
seeder.seed(data)

```

## No Relationship

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

## Relationships

In adding a relationship attribute, add prefix '!' to the key in order to identify it.

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

## Example of Nested Relationships

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
