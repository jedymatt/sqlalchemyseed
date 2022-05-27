# sqlalchemyseed

[![PyPI](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)
[![Python package](https://github.com/jedymatt/sqlalchemyseed/actions/workflows/python-package.yml/badge.svg)](https://github.com/jedymatt/sqlalchemyseed/actions/workflows/python-package.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/2ca97c98929b614658ea/maintainability)](https://codeclimate.com/github/jedymatt/sqlalchemyseed/maintainability)
[![codecov](https://codecov.io/gh/jedymatt/sqlalchemyseed/branch/main/graph/badge.svg?token=W03MFZ2FAG)](https://codecov.io/gh/jedymatt/sqlalchemyseed)
[![Documentation Status](https://readthedocs.org/projects/sqlalchemyseed/badge/?version=latest)](https://sqlalchemyseed.readthedocs.io/en/latest/?badge=latest)

Sqlalchemy seeder that supports nested relationships.

Supported file types

- json
- yaml
- csv

## Installation

Default installation

```shell
pip install sqlalchemyseed
```

## Quickstart

main.py

```python
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

data.json

```json
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

## Documentation

<https://sqlalchemyseed.readthedocs.io/>

## Found Bug?

Report here in this link:
<https://github.com/jedymatt/sqlalchemyseed/issues>

## Want to contribute?

First, Clone this [repository](https://github.com/jedymatt/sqlalchemyseed).

### Install dev dependencies

Inside the folder, paste this in the terminal to install necessary dependencies:

```shell
pip install -r requirements.txt -r docs/requirements.txt
```

Note: make sure you have the virtual environment and enabled, or if you are using vs code and docker then you can simply re-open this as container.

### Run tests

Before running tests, make sure that the package is installed as editable:

```shell
python setup.py develop --user
```

Then run the test:

```shell
pytest tests
```

Run test with coverage

```shell
coverage run -m pytest
```

Autobuild documentation

```shell
sphinx-autobuild docs docs/_build/html
```
