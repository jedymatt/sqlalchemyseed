# sqlalchemyseed

[![PyPI](https://img.shields.io/pypi/v/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemyseed)](https://pypi.org/project/sqlalchemyseed)
[![PyPI - License](https://img.shields.io/pypi/l/sqlalchemyseed)](https://github.com/jedymatt/sqlalchemyseed/blob/main/LICENSE)
[![Build Status](https://app.travis-ci.com/jedymatt/sqlalchemyseed.svg?branch=main)](https://app.travis-ci.com/jedymatt/sqlalchemyseed)
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

## Documentation

<https://sqlalchemyseed.readthedocs.io/>
