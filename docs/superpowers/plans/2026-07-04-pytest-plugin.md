# pytest Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a bundled pytest plugin that loads JSON/YAML/CSV fixture files into a transactionally-isolated SQLAlchemy session that rolls back after each test.

**Architecture:** A new module `src/sqlalchemyseed/pytest_plugin.py` exposes three fixtures (`engine` user-provided stub, `sqlalchemyseed_session` transactional, `seed` factory), registered via a `pytest11` entry point. The CLI's file-extension dispatch is first extracted into a shared `loader.load_path` (Rule of Three) that both the CLI and the plugin call.

**Tech Stack:** Python, pytest (`pytester` for testing the plugin), SQLAlchemy 2.0+ (`join_transaction_mode="create_savepoint"`), uv, setuptools.

## Global Constraints

- `requires-python = ">=3.9"`; `SQLAlchemy>=2.0` (the `join_transaction_mode` Session kwarg exists at the 2.0.0 floor).
- pytest is a **dev/test dependency only** — do NOT add it to `[project.dependencies]`. `import pytest` appears only in `pytest_plugin.py`; `sqlalchemyseed/__init__.py` must NOT import `pytest_plugin`.
- The plugin module is inert: fixtures only — no hooks, no `autouse`, no markers, no config.
- Fixture names are fixed: `engine` (user hook), `sqlalchemyseed_session` (plugin), `seed` (plugin factory).
- The CLI refactor in Task 1 must produce **zero CLI behavior change** — preserve the exact CSV error string `"CSV input requires --model to name the target class: {path}"` so `tests/test_cli.py::test_csv_without_model_fails` passes unchanged.
- `seed()` calls `flush()`, never `commit()`.
- Version target: `2.3.0`.
- After editing `pyproject.toml`'s entry points, run `uv sync` so the new `pytest11` entry point is registered before running the suite.

---

### Task 1: Extract shared `load_path` into the loader (refactor)

Moves the file-extension dispatch out of `cli.py` into `loader.py` so both the CLI and (in Task 2) the plugin call one implementation. No behavior change.

**Files:**
- Modify: `src/sqlalchemyseed/loader.py` (add dispatch)
- Modify: `src/sqlalchemyseed/cli.py:14-19,78-107,117-123` (delete moved code, call `loader.load_path`)
- Test: `tests/test_loader.py` (add `load_path` unit tests)

**Interfaces:**
- Produces: `loader.load_path(path, model=None) -> dict` — accepts a `str` or `pathlib.Path`; dispatches on lowercased suffix (`.json` → `load_entities_from_json`, `.yaml`/`.yml` → `load_entities_from_yaml`, `.csv` → `_load_csv`); raises `ValueError` on unknown extension; CSV without `model` raises `ValueError`.
- Produces: `loader.DISCOVERABLE_EXTENSIONS: set[str]` = `{".json", ".yaml", ".yml"}` — the CLI's directory-discovery whitelist.
- Consumes: existing `loader.load_entities_from_json/yaml/csv`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_loader.py`:

```python
import pytest

from sqlalchemyseed import loader


def test_load_path_reads_json(tmp_path):
    data_file = tmp_path / "d.json"
    data_file.write_text('{"model": "m.M", "data": []}', encoding="utf-8")
    assert loader.load_path(data_file) == {"model": "m.M", "data": []}


def test_load_path_rejects_unknown_extension(tmp_path):
    bad = tmp_path / "d.txt"
    bad.write_text("nope", encoding="utf-8")
    with pytest.raises(ValueError):
        loader.load_path(bad)


def test_load_path_csv_requires_model(tmp_path):
    csv_file = tmp_path / "d.csv"
    csv_file.write_text("name\nAlice\n", encoding="utf-8")
    with pytest.raises(ValueError):
        loader.load_path(csv_file)


def test_discoverable_extensions_are_json_and_yaml():
    assert loader.DISCOVERABLE_EXTENSIONS == {".json", ".yaml", ".yml"}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_loader.py -v`
Expected: FAIL — `AttributeError: module 'sqlalchemyseed.loader' has no attribute 'load_path'`.

- [ ] **Step 3: Add the dispatch to `loader.py`**

At the top of `src/sqlalchemyseed/loader.py`, add `from pathlib import Path` under the existing imports (after `import sys`). Then append to the end of the file:

```python
_JSON_EXTENSIONS = {".json"}
_YAML_EXTENSIONS = {".yaml", ".yml"}
_CSV_EXTENSIONS = {".csv"}
# Formats that are self-describing (carry their own model) and so can be
# auto-discovered inside a directory. CSV needs an explicit model.
DISCOVERABLE_EXTENSIONS = _JSON_EXTENSIONS | _YAML_EXTENSIONS


def load_path(path, model=None) -> dict:
    """Load entities from a single data file, dispatching on its extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in _JSON_EXTENSIONS:
        return load_entities_from_json(str(path))
    if suffix in _YAML_EXTENSIONS:
        return load_entities_from_yaml(str(path))
    if suffix in _CSV_EXTENSIONS:
        return _load_csv(path, model)
    raise ValueError(f"unsupported file type: {path}")


def _load_csv(path, model) -> dict:
    """Load entities from a CSV file, which requires an explicit model."""
    if model is None:
        raise ValueError(f"CSV input requires --model to name the target class: {path}")
    return load_entities_from_csv(str(path), model)
```

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `uv run pytest tests/test_loader.py -v`
Expected: PASS (all four new tests plus existing ones).

- [ ] **Step 5: Point the CLI at the shared dispatch**

In `src/sqlalchemyseed/cli.py`:

1. Delete the extension constants block (lines 14-19):

```python
_JSON_EXTENSIONS = {".json"}
_YAML_EXTENSIONS = {".yaml", ".yml"}
_CSV_EXTENSIONS = {".csv"}
# Only self-describing formats are auto-discovered inside a directory. CSV
# needs an explicit --model, so a CSV must be named as an individual file.
_DISCOVERABLE_EXTENSIONS = _JSON_EXTENSIONS | _YAML_EXTENSIONS
```

2. In `_discover_directory`, change the whitelist reference:

```python
    discovered = sorted(
        child for child in directory.iterdir()
        if child.suffix.lower() in loader.DISCOVERABLE_EXTENSIONS
    )
```

3. Delete the `load_file` and `_load_csv` functions entirely (old lines 91-107).

4. In `_seed_all`, call the shared loader:

```python
def _seed_all(seeder, files, model) -> int:
    """Seed every file through the seeder and return the entity count."""
    seeded = 0
    for path in files:
        seeder.seed(loader.load_path(path, model))
        seeded += len(seeder.instances)
    return seeded
```

- [ ] **Step 6: Run the full suite to verify no behavior change**

Run: `uv run pytest tests/test_cli.py tests/test_loader.py -v`
Expected: PASS — every existing CLI test (including `test_csv_without_model_fails` asserting `"requires --model"`) still passes.

- [ ] **Step 7: Commit**

```bash
git add src/sqlalchemyseed/loader.py src/sqlalchemyseed/cli.py tests/test_loader.py
git commit -m "refactor: extract shared load_path dispatch into loader

Rule of Three (loaders -> CLI -> upcoming plugin). No CLI behavior change.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: The pytest plugin module, entry point, and tests

Creates the plugin and wires it in via the `pytest11` entry point, tested with pytest's own `pytester` fixture.

**Files:**
- Create: `src/sqlalchemyseed/pytest_plugin.py`
- Modify: `pyproject.toml` (add `[project.entry-points.pytest11]`)
- Create: `tests/conftest.py` (enable `pytester`)
- Test: `tests/test_pytest_plugin.py`

**Interfaces:**
- Consumes: `loader.load_path` (Task 1); `Seeder`, `HybridSeeder` from `.seeder`.
- Produces fixtures: `engine` (stub, session must override), `sqlalchemyseed_session(engine) -> Session`, `seed(sqlalchemyseed_session) -> callable`. The `seed` callable signature is `_seed(path, *, model=None, seeder="basic", ref_prefix="!") -> Seeder | HybridSeeder`, returning the seeder instance (so `.instances` is readable).

- [ ] **Step 1: Enable `pytester` and write the first failing test**

Create `tests/conftest.py`:

```python
pytest_plugins = ["pytester"]
```

Create `tests/test_pytest_plugin.py`:

```python
"""Tests for the bundled pytest plugin, exercised via the pytester fixture."""

# A self-contained conftest for the inner pytest runs. StaticPool keeps a
# single in-memory SQLite connection alive so create_all and the session share
# one database.
CONFTEST = '''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from models import Base


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    return eng
'''

MODELS = '''
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
'''


def _scaffold(pytester):
    """Write the shared conftest + models module into the inner project."""
    pytester.makeconftest(CONFTEST)
    pytester.makepyfile(models=MODELS)


def test_seed_json(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}, {"name": "Bob"}]}',
    )
    pytester.makepyfile(
        test_seed_json='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seeder = seed("people.json")
            assert sqlalchemyseed_session.query(Person).count() == 2
            assert seeder.instances[0].name == "Alice"
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_pytest_plugin.py -v`
Expected: FAIL — the inner test errors with `fixture 'seed' not found` (the plugin does not exist yet), so `assert_outcomes(passed=1)` fails.

- [ ] **Step 3: Create the plugin module**

Create `src/sqlalchemyseed/pytest_plugin.py`:

```python
"""pytest plugin: file-based SQLAlchemy fixtures with per-test rollback.

Registered via the ``pytest11`` entry point. Defines fixtures only — importing
this module has no side effects, and it is never imported by the package's
``__init__`` so production imports never pull in pytest.
"""

import pytest
from sqlalchemy.orm import Session

from .loader import load_path
from .seeder import HybridSeeder, Seeder

_MISSING_ENGINE_MESSAGE = (
    "sqlalchemyseed's pytest plugin requires an 'engine' fixture. Define one in "
    "your conftest.py that returns a SQLAlchemy Engine with your schema created, "
    "e.g.:\n\n"
    "    @pytest.fixture(scope='session')\n"
    "    def engine():\n"
    "        engine = create_engine('sqlite://')\n"
    "        Base.metadata.create_all(engine)\n"
    "        return engine\n"
)


@pytest.fixture
def engine():
    """Placeholder the user overrides in their conftest with a real Engine."""
    raise RuntimeError(_MISSING_ENGINE_MESSAGE)


@pytest.fixture
def sqlalchemyseed_session(engine):
    """A Session in an open transaction that is rolled back after the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def seed(sqlalchemyseed_session):
    """Return a callable that seeds a data file into the test session."""
    def _seed(path, *, model=None, seeder="basic", ref_prefix="!"):
        entities = load_path(path, model)
        seeder_cls = HybridSeeder if seeder == "hybrid" else Seeder
        instance = seeder_cls(sqlalchemyseed_session, ref_prefix=ref_prefix)
        instance.seed(entities)
        sqlalchemyseed_session.flush()
        return instance

    return _seed
```

- [ ] **Step 4: Register the entry point and sync**

In `pyproject.toml`, add directly after the `[project.scripts]` block:

```toml
[project.entry-points.pytest11]
sqlalchemyseed = "sqlalchemyseed.pytest_plugin"
```

Then re-register it in the environment:

Run: `uv sync`
Expected: resolves and reinstalls the project (editable) with the new entry point.

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_pytest_plugin.py -v`
Expected: PASS — the inner `test_seed_json` now finds the `seed` fixture.

- [ ] **Step 6: Add the remaining plugin tests**

Append to `tests/test_pytest_plugin.py`:

```python
def test_seed_yaml(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".yaml",
        people="model: models.Person\ndata:\n  - name: Carol\n",
    )
    pytester.makepyfile(
        test_seed_yaml='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seed("people.yaml")
            assert sqlalchemyseed_session.query(Person).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_seed_csv_with_model(pytester):
    _scaffold(pytester)
    pytester.makefile(".csv", people="name\nDave\nErin\n")
    pytester.makepyfile(
        test_seed_csv='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seed("people.csv", model="models.Person")
            assert sqlalchemyseed_session.query(Person).count() == 2
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_hybrid_seeder(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}]}',
    )
    pytester.makepyfile(
        test_hybrid='''
        from models import Person

        def test_it(seed, sqlalchemyseed_session):
            seeder = seed("people.json", seeder="hybrid")
            assert sqlalchemyseed_session.query(Person).count() == 1
            assert seeder.instances[0].name == "Alice"
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_rollback_isolation(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Alice"}, {"name": "Bob"}]}',
    )
    pytester.makepyfile(
        test_isolation='''
        from models import Person

        def test_first_seeds(seed, sqlalchemyseed_session):
            seed("people.json")
            assert sqlalchemyseed_session.query(Person).count() == 2

        def test_second_sees_empty_db(sqlalchemyseed_session):
            # The prior test's rows were rolled back with its transaction.
            assert sqlalchemyseed_session.query(Person).count() == 0
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_missing_engine_gives_actionable_error(pytester):
    # Deliberately no conftest / engine fixture.
    pytester.makepyfile(
        test_no_engine='''
        def test_it(seed):
            pass
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*requires an 'engine' fixture*"])


def test_user_can_override_session(pytester):
    _scaffold(pytester)
    pytester.makefile(
        ".json",
        people='{"model": "models.Person", "data": [{"name": "Zoe"}]}',
    )
    # Override the plugin's session fixture; seed must use the override.
    pytester.makepyfile(
        test_override='''
        import pytest
        from sqlalchemy.orm import Session
        from models import Person

        @pytest.fixture
        def sqlalchemyseed_session(engine):
            connection = engine.connect()
            transaction = connection.begin()
            session = Session(bind=connection, join_transaction_mode="create_savepoint")
            session.info["overridden"] = True
            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
                connection.close()

        def test_it(seed, sqlalchemyseed_session):
            seed("people.json")
            assert sqlalchemyseed_session.info.get("overridden") is True
            assert sqlalchemyseed_session.query(Person).count() == 1
        '''
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
```

- [ ] **Step 7: Run the plugin tests**

Run: `uv run pytest tests/test_pytest_plugin.py -v`
Expected: PASS — all seven tests (json, yaml, csv, hybrid, rollback isolation, missing-engine error, session override).

- [ ] **Step 8: Run the whole suite to confirm no collision**

Run: `uv run pytest -q`
Expected: PASS — the auto-registered plugin adds `engine`/`seed`/`sqlalchemyseed_session` fixtures globally; confirm no existing test breaks (none request those names).

- [ ] **Step 9: Commit**

```bash
git add src/sqlalchemyseed/pytest_plugin.py pyproject.toml tests/conftest.py tests/test_pytest_plugin.py uv.lock
git commit -m "feat: add bundled pytest plugin with per-test rollback

seed/sqlalchemyseed_session/engine fixtures via a pytest11 entry point.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Version bump, README, and full verification

Releases the feature at the docs + version level and verifies the whole matrix locally.

**Files:**
- Modify: `src/sqlalchemyseed/__init__.py:14`
- Modify: `README.md` (add "## Testing with pytest" section)

**Interfaces:**
- Consumes: the fixtures shipped in Task 2. No new code.

- [ ] **Step 1: Bump the version**

In `src/sqlalchemyseed/__init__.py`, change:

```python
__version__ = "2.2.0"
```

to:

```python
__version__ = "2.3.0"
```

- [ ] **Step 2: Document the plugin in the README**

In `README.md`, insert a new section immediately after the "## Command-line usage" section (before "## Documentation"):

````markdown
## Testing with pytest

Installing `sqlalchemyseed` alongside `pytest` registers a plugin that loads
fixture files into a transactionally-isolated session. Provide one `engine`
fixture in your `conftest.py`; the plugin supplies `sqlalchemyseed_session`
(rolled back after every test) and a `seed` factory.

```python
# conftest.py
import pytest
from sqlalchemy import create_engine

from myapp.models import Base


@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine
```

```python
# test_people.py
from myapp.models import Person


def test_people_are_seeded(seed, sqlalchemyseed_session):
    seeder = seed("tests/data/people.yaml")
    assert sqlalchemyseed_session.query(Person).count() == 2
    assert seeder.instances[0].name == "Alice"
```

`seed()` accepts the same inputs as the library: `.json`, `.yaml`/`.yml`, and
`.csv` files. CSV is not self-describing, so pass the model:
`seed("people.csv", model="myapp.models.Person")`. Use `seeder="hybrid"` for the
`HybridSeeder`, and `ref_prefix=...` to override the relationship reference
prefix. Every test runs inside a transaction that is rolled back afterward, so
tests never see each other's rows.
````

- [ ] **Step 3: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS — all tests including the new plugin tests.

- [ ] **Step 4: Run against the lowest supported dependencies**

Run: `uv run --resolution lowest-direct --python 3.9 pytest -q`
Expected: PASS — confirms `join_transaction_mode="create_savepoint"` works at the SQLAlchemy 2.0.0 floor.

- [ ] **Step 5: Commit**

```bash
git add src/sqlalchemyseed/__init__.py README.md
git commit -m "docs: document pytest plugin and bump to 2.3.0

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Notes for the release (out of plan scope, do after merge)

Follow the established release flow used for 2.1.0/2.2.0: open a PR from `feat/pytest-plugin`, merge, then create a GitHub Release tagged `v2.3.0` — the OIDC Trusted-Publishing workflow publishes to PyPI. Then check off the pytest-plugin item on roadmap issue #65. Do not perform these steps as part of implementation; they are the user-gated release.
