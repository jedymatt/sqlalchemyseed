# pytest plugin — design

**Status:** approved design, pending implementation
**Roadmap item:** [#65](https://github.com/jedymatt/sqlalchemyseed/issues/65) Tier 1 — pytest plugin
**Target release:** 2.3.0

## Goal

Give SQLAlchemy test suites a first-class way to load known fixture data from
JSON/YAML/CSV files into a **transactionally isolated** session that is rolled
back after each test. This is the gap `factory_boy` does not fill: it owns
*generated* data; file-based *known* fixtures with automatic per-test rollback
is the open lane (the Django `loaddata` muscle-memory that Django refugees miss).

## Distribution

Bundled into the existing `sqlalchemyseed` package — **not** a separate
`pytest-sqlalchemyseed` distribution. Registered via a `pytest11` entry point:

```toml
[project.entry-points.pytest11]
sqlalchemyseed = "sqlalchemyseed.pytest_plugin"
```

Rationale: zero new distribution to version/release/OIDC-configure, and the
plugin version stays in lockstep with the seeder it wraps.

**Inertness contract:** the plugin module defines *only* fixtures — no hooks, no
`autouse`, no config, no marker. Merely having `sqlalchemyseed` + `pytest`
installed changes nothing until a test explicitly requests a fixture. `pytest`
is a **dev/test dependency only**; it is NOT added to `[project.dependencies]`.
`import pytest` lives at the top of `pytest_plugin.py` and nowhere else in the
package — `sqlalchemyseed/__init__.py` must NOT import `pytest_plugin`, so
importing `sqlalchemyseed` in production never imports pytest. pytest loads the
plugin module itself via the `pytest11` entry point, only when pytest runs.

## Fixtures

Three fixtures. Naming follows the rule **user-provided hooks may use
conventional names (override by the user is the intended seam); plugin-owned
fixtures are namespaced so they cannot be silently shadowed.**

| Fixture | Owner | Scope | Role |
|---|---|---|---|
| `engine` | **user** (conftest) | session | The single integration point. A SQLAlchemy `Engine` with the schema already created. |
| `sqlalchemyseed_session` | plugin | function | Transactional `Session` bound to an open connection-level transaction, rolled back after each test. |
| `seed` | plugin | function | Callable factory that loads a file and seeds it into `sqlalchemyseed_session`, returning the seeder. |

### `engine` (user-provided)

The plugin ships a **stub** `engine` fixture that raises a clear, actionable
error if the user has not defined their own:

```python
@pytest.fixture
def engine():
    raise RuntimeError(
        "sqlalchemyseed's pytest plugin requires an 'engine' fixture. "
        "Define one in your conftest.py that returns a SQLAlchemy Engine "
        "with your schema created, e.g.:\n\n"
        "    @pytest.fixture(scope='session')\n"
        "    def engine():\n"
        "        engine = create_engine('sqlite://')\n"
        "        Base.metadata.create_all(engine)\n"
        "        return engine\n"
    )
```

The user's conftest fixture overrides this stub by name. Expected shape is
session-scoped (created once); per-test isolation comes from rollback, not from
recreating the schema.

### `sqlalchemyseed_session` (plugin, overridable)

```python
@pytest.fixture
def sqlalchemyseed_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
```

`join_transaction_mode="create_savepoint"` (SQLAlchemy 2.0+, already required)
means any `commit()` the test or `seed()` issues lands on a SAVEPOINT inside the
outer transaction; the teardown `transaction.rollback()` erases everything. No
per-test `create_all`/`drop_all`, so it is fast and leaves the DB pristine. The
session reads its own uncommitted writes, so `HybridSeeder`'s mid-seed
`session.query(...).one()` works inside the open transaction.

### `seed` (plugin factory)

```python
@pytest.fixture
def seed(sqlalchemyseed_session):
    def _seed(path, *, model=None, seeder="basic", ref_prefix="!"):
        entities = load_path(path, model)
        cls = HybridSeeder if seeder == "hybrid" else Seeder
        inst = cls(sqlalchemyseed_session, ref_prefix)
        inst.seed(entities)
        sqlalchemyseed_session.flush()
        return inst
    return _seed
```

- Returns the seeder instance so tests can read `.instances`.
- `flush()` (not `commit()`) is sufficient to make rows queryable within the
  same session and keeps all writes inside the rolled-back transaction; the
  savepoint mode is belt-and-suspenders for tests that commit anyway.
- Composable: call `seed()` multiple times, seed then assert, seed conditionally.

## Shared file loading (refactor)

File-extension dispatch (`.json` / `.yaml` / `.yml` / `.csv`; CSV requires
`model`) already exists in `cli.load_file(path, model)`. The plugin needs the
identical logic — the third occurrence (loaders → CLI → plugin), so extract it
(Rule of Three) into a neutral shared helper `load_path(path, model)` in the
`loader` module. The CLI is refactored to call it; **no behavior change to the
CLI**. The plugin imports `load_path` from `loader`, not from `cli` (avoids
pulling argparse into the plugin and keeps the dependency direction clean).

Unlike the CLI, the plugin does **no** `sys.path` munging — under pytest the
user's models are already importable (conftest imported them; rootdir is on the
path). `sys.path.insert(0, cwd)` stays a CLI-only concern.

## Error handling

- **Missing `engine`**: the stub fixture raises the actionable message above —
  not an obscure "fixture 'engine' not found".
- **Bad file / unsupported extension / missing `model` for CSV**: the loader's
  existing exceptions propagate directly. In a test context, failing loudly is
  correct — no swallowing.

## Testing

Use pytest's own `pytester` fixture to run *sub*-pytest sessions against a
throwaway in-memory SQLite engine and `tests/models.py`. New file
`tests/test_pytest_plugin.py`. Enable via `pytest_plugins = ["pytester"]` in
`tests/conftest.py` (create if absent). Coverage:

- seed JSON, YAML, CSV (CSV with `model`)
- `seeder="hybrid"` path
- `seed()` returns a seeder whose `.instances` is populated
- **rollback isolation**: two tests; the second observes an empty DB
- missing-`engine` error surfaces the actionable message
- user override of `sqlalchemyseed_session` is honored
- unsupported file type / missing `model` for CSV fail loudly

## Packaging / docs / version

- `pyproject.toml`: add the `[project.entry-points.pytest11]` entry.
- `pytest` is already in `[dependency-groups].dev`; no new runtime dependency.
- `__version__` → `2.3.0`.
- README: add a "## Testing with pytest" section showing the `engine` conftest
  fixture and a `seed(...)` test.

## Out of scope (YAGNI for 2.3.0)

- `@pytest.mark.seed(...)` marker sugar (factory fixture ships first; add later
  only if demand appears).
- ini options (`ref_prefix`, base data dir) — paths resolve as given.
- Async / `AsyncSession` support (tracked separately in #43).
