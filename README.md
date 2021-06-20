# sqlalchemyseed

SQLAlchemy seeder. One-to-one, one-to-many, many-to-many relationship support.

## Installation

```commandline
pip install sqlalchemyseed
```

### Dependencies

* SQAlchemy>=1.4.0

## Getting Started

```python
# main.py
from db import session  # import where your session is located.
from sqlalchemyseed import create_objects
from sqlalchemyseed import load_entities_from_json

entities = load_entities_from_json("data.json")

# create_objects returns the objects created, while automatically added them to the session
objects = create_objects(session, entities)

# you can check the added objects by printing session.new
print(session.new)

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

One to Many
***********

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