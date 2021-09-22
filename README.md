# sqlalchemyseed

[![PyPI](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)
[![Build Status](https://app.travis-ci.com/jedymatt/sqlalchemyseed.svg?branch=main)](https://app.travis-ci.com/jedymatt/sqlalchemyseed)
[![Maintainability](https://api.codeclimate.com/v1/badges/2ca97c98929b614658ea/maintainability)](https://codeclimate.com/github/jedymatt/sqlalchemyseed/maintainability)
[![codecov](https://codecov.io/gh/jedymatt/sqlalchemyseed/branch/main/graph/badge.svg?token=W03MFZ2FAG)](https://codecov.io/gh/jedymatt/sqlalchemyseed)

Sqlalchemy seeder that supports nested relationships.

Supported file types

- [json](#json)
- [yaml](#yaml)
- [csv](#csv)

## Installation

Default installation

```shell
pip install sqlalchemyseed
```

When using yaml to load entities from yaml files, execute this command to install necessary dependencies

```shell
pip install sqlalchemyseed[yaml]
```

## Dependencies

Required dependencies

- SQAlchemy>=1.4.0

Optional dependencies

- yaml
  - PyYAML>=5.4.0

## Getting Started

```python
# main.py
from sqlalchemyseed import load_entities_from_json
from sqlalchemyseed import Seeder
from db import session

# load entities
entities = load_entities_from_json('data.json')

# Initializing Seeder
seeder = Seeder(session)

# Seeding
seeder.seed(entities)

# Committing
session.commit()  # or seeder.session.commit()
```

## Seeder vs. HybridSeeder

| Features & Options                                            | Seeder | HybridSeeder |
| :------------------------------------------------------------ | :----- | :----------- |
| Support `model` and `data` keys                               | ✔️      | ✔️            |
| Support `model` and `filter` keys                             | ❌      | ✔️            |
| Optional argument `add_to_session=False` in the `seed` method | ✔️      | ❌            |

## When to use HybridSeeder and 'filter' key field?

Assuming that `Child(age=5)` exists in the database or session, then we should use `filter` instead of `data`, the
values of `filter` will query from the database or session, and assign it to the `Parent.child`

```python
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
# ref_prefix can be changed according to your needs,
# defaults  to '!'
seeder = HybridSeeder(session, ref_prefix='!') 
seeder.seed(data)

session.commit()  # or seeder.sesssion.commit()
```

## Relationships

In adding a reference attribute, add prefix to the key in order to identify it. Default prefix is `!`.

Reference attribute can either be foreign key or relationship attribute. See examples below.

### Customizing prefix

If you want '@' as prefix, you can just specify it to what seeder you use by adding ref_prefix='@' in the argument like this `seeder = Seeder(session, ref_prefix='@')`, in order for the seeder to identify the referencing attributes

### Referencing relationship object or a foreign key

If your class don't have a relationship attribute but instead a foreign key attribute you can use it the same as how you
did it on a relationship attribute

**Note**: `model` can be removed if it is a reference attribute.  

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
        'data': [
            {
                'name': 'John Smith',
                # foreign key attribute
                '!company_id': {
                    'model': 'tests.models.Company', # models can be removed if it is a referencing attribute
                    'filter': {
                        'name': 'MyCompany'
                    }
                }
            },
            {
                'name': 'Juan Dela Cruz',
                # relationship attribute
                '!company': {
                    'model': 'tests.models.Company', # models can be removed if it is a referencing attribute
                    'filter': {
                        'name': 'MyCompany'
                    }
                }
        ]
    }
]

seeder = HybridSeeder(session)
seeder.seed(instance)
seeder.session.commit() # or session.commit()
```

### No Relationship

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
    // in your database use 'filter' instead of 'data'
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

## File Input Examples

### JSON

data.json

```json5
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
```

### YAML

data.yml

```yaml
model: models.Person
data:
    - name: John March
      age: 23
    - name: Juan Dela Cruz
      age: 21
```

### CSV

In line one, name and age, are attributes of a model that will be specified when loading the file.

`people.csv`

```text
name, age
John March, 23
Juan Dela Cruz, 21
```

To load a csv file

`main.py`

```python
# second argument, model, accepts class
load_entities_from_csv("people.csv", models.Person)
# or string
load_entities_from_csv("people.csv", "models.Person")
```

**Note**: Does not support relationships
