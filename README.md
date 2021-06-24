# sqlalchemyseed

[![https://pypi.org/project/sqlalchemyseed/](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed/)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)

## Installation

```commandline
pip install sqlalchemyseed
```

### Dependencies

* SQAlchemy>=1.4.0
* jsonschema>=3.2.0

## Getting Started

```python
# main.py
from tests.db import session  # import where your session is located.
from sqlalchemyseed import Seeder, load_entities_from_json, HybridSeeder

# load entities
entities = load_entities_from_json("data.json")

# use seeder if you are limited to using 'data' field or you do not query relationship from database
seeder = Seeder()
seeder.seed(entities, session)  # session, optional, automatically add entities to session
# HybridSeeder to use 'filter' field, querying and assigning relationship that exist in the database
seeder = HybridSeeder(session)
seeder.seed(entities)

# for confirmation,
# you can check the added objects by printing session.new and session.dirty
print(session.new)
print(session.dirty)

```

## No Relationship

```json5
// data.json
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

## One to One

```json5
// data.json
[
    {
        "model": "models.Person",
        "data": {
            "name": "John",
            "age": 18,
            // creates a job object
            "job": {
                "model": "models.Job",
                "data": {
                    "job_name": "Programmer",
                }
            }
        }
    },
    // or this, if you want to add relationship that exist
    // in your database use 'filter' instead of 'data'
    {
        "model": "models.Person",
        "data": {
            "name": "Jeniffer",
            "age": 18,
            "job": {
                "model": "models.Job",
                "filter": {
                    "job_name": "Programmer",
                }
            }
        }
    }
]
```

## One to Many

```json5
//data.json
[
    {
        "model": "models.Person",
        "data": {
            "name": "John",
            "age": 18,
            "items": [
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