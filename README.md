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

## Command-line usage

Seed a database directly from data files without writing Python:

```shell
sqlalchemyseed data.json --url sqlite:///app.db
```

The command accepts one or more files and/or directories (a directory seeds
every `.json`/`.yaml`/`.yml` file inside it, in sorted order):

```shell
sqlalchemyseed seeds/ --url "$DATABASE_URL"
sqlalchemyseed a.json b.yaml --url sqlite:///app.db
```

The database URL may be passed with `--url` or the `DATABASE_URL` environment
variable. Model paths in the data files (e.g. `models.Person`) are resolved
against the current working directory, so run the command from your project
root.

Options:

- `--dry-run` — seed inside a transaction, then roll back (validate without writing)
- `--seeder hybrid` — use `HybridSeeder` instead of the default `Seeder`
- `--model models.Person` — required for CSV inputs, which are not self-describing
- `--ref-prefix` — override the relationship reference prefix (default `!`)

The same command is available as a module:

```shell
python -m sqlalchemyseed data.json --url sqlite:///app.db
```

## Documentation

<https://sqlalchemyseed.readthedocs.io/>

## Found Bug?

Report here in this link:
<https://github.com/jedymatt/sqlalchemyseed/issues>

## Want to contribute?

First, Clone this [repository](https://github.com/jedymatt/sqlalchemyseed).

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and running tasks.

### Install dev dependencies

Inside the folder, sync the environment (uv creates the virtualenv and installs the project plus dev dependencies):

```shell
uv sync
```

### Run tests

```shell
uv run pytest
```

Run the tests against a specific Python version (uv downloads it if needed):

```shell
uv run --python 3.14 pytest
```

Run the tests against the lowest supported dependencies (e.g. SQLAlchemy 2.0):

```shell
uv run --resolution lowest-direct pytest
```

Run tests with coverage:

```shell
uv run coverage run -m pytest
```

Autobuild documentation

```shell
sphinx-autobuild docs docs/_build/html
```
