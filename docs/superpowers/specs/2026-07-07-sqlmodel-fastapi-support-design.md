# SQLModel & FastAPI support — design

**Status:** approved design, pending implementation
**Roadmap item:** [#65](https://github.com/jedymatt/sqlalchemyseed/issues/65) Tier 1 — first-class FastAPI + SQLModel support
**Target release:** 2.6.0

## Goal

Turn "SQLModel probably works" into "proven and documented". SQLModel is the
FastAPI ecosystem's ORM layer, and a `table=True` SQLModel class *is* a
SQLAlchemy mapped class — so the deliverable is compatibility **verified in CI
on every push**, a warning-free `HybridSeeder` under `sqlmodel.Session`, and
docs/README positioning that makes FastAPI users see themselves supported.

No new runtime API. The seed-file format, seeders, CLI, and pytest plugin all
stay exactly as they are.

## Empirical baseline (smoke-tested 2026-07-07, sqlmodel 0.0.39 / pydantic 2.13.4)

All core paths already pass with zero code changes:

| Scenario | Result | Why it works |
|---|---|---|
| `Seeder` with nested `!ref` child | ✅ | `inspect(class_).is_mapper` is true for `table=True` models |
| `HybridSeeder` `filter` on relationship attr | ✅ | SQLModel `Relationship()` produces real `RelationshipProperty` |
| `HybridSeeder` `filter` on FK **column** attr | ✅ | auto-generated `__tablename__` satisfies the registry lookup in `attribute.referenced_class` |
| one-to-many list relationship | ✅ | instrumented attributes; `set_attribute`/`get_attribute` work |
| non-`table=True` SQLModel class as `model` | ✅ correct error | not a mapper → existing `UnsupportedClassError` |

Two rough edges found:

1. **`DeprecationWarning` noise.** `HybridSeeder._setup_filter_instance` uses
   legacy `session.query(...)`. `sqlmodel.Session` overrides `.query()` to emit
   a `DeprecationWarning` per call. Python's default filter hides it in plain
   runs, but **pytest surfaces it** — users running our pytest plugin with a
   SQLModel session get warning noise from inside this library. Fixed by this
   design (see below).
2. **Unknown attribute error shape.** A bad attribute name in a seed file
   raises a raw `AttributeError: <name>` on SQLModel models (plain declarative
   models raise a clearer `TypeError`). Cosmetic; documented, not changed.

## Runtime change: modernize `HybridSeeder` filter queries

The only production-code change. In `seeder.py`,
`HybridSeeder._setup_filter_instance` migrates its three
`session.query(...).filter_by(...).one()` branches to 2.0-style
`select()` + `session.execute(...)`:

- relationship branch and top-level branch: `select(entity).filter_by(**kw)`
  → `.scalar_one()`
- FK-column branch (`session.query(column)`): the selected object is a raw
  `Column`, not a mapped entity, so `Select.filter_by` may not resolve
  attribute names against it the way legacy `Query.filter_by` did. If it
  doesn't, build explicit criteria from the column's table:
  `select(column).where(*(column.table.c[k] == v ...))` → `.one()[0]`.
  Verify against the existing FK-column tests.

**Semantics contract:** zero/multiple matches must still raise
`NoResultFound`/`MultipleResultsFound` exactly as before (`.one()` →
`.scalar_one()` preserves both). Existing tests cover these paths; the new
no-warning test (below) guards the migration.

`AsyncHybridSeeder` needs no change — it bridges through
`AsyncSession.run_sync` and inherits the fix.

Sweep the rest of the package and docs for other legacy `session.query` call
sites and migrate/update them in the same pass (docs examples included, where
they demonstrate this library rather than generic SQLAlchemy).

## Tests: dedicated compat module

New `tests/sqlmodel_models.py`: `Company`/`Employee` with a bidirectional
relationship and FK, mirroring the shape of `tests/models.py`. New
`tests/test_sqlmodel.py` covering the divergence-prone paths and integration
seams:

- basic `Seeder` with nested `!ref` child
- `HybridSeeder` `filter` on a relationship attribute
- `HybridSeeder` `filter` on an FK column attribute
- one-to-many list relationship (children appended, not overwritten)
- `AsyncSeeder` against SQLModel's async session (`sqlmodel.ext.asyncio`)
- pytest plugin: `seed` fixture with a SQLModel-built `engine`
  (pytester-style, matching `test_pytest_plugin.py`)
- CSV loading with `model` pointing at a SQLModel class
- **no `DeprecationWarning` from library internals** when `HybridSeeder` runs
  a `filter` seed on a `sqlmodel.Session` (guards the query modernization)
- non-`table=True` SQLModel class raises `UnsupportedClassError`

The existing 99 tests are untouched. Rationale for a dedicated module over
parametrizing the whole suite: the seeder only touches models through the
mapper API, which the smoke test confirmed is identical for SQLModel — the
mirrored high-risk scenarios cover the actual divergence surface, without a
test-suite refactor or 2× runtime.

## Packaging / CI

- `sqlmodel` joins `[dependency-groups].dev` (a test dependency only — NOT a
  runtime dependency, NOT an extra; users who want SQLModel already have it).
  Verified installable on Python 3.10 and 3.14 with pydantic v2.
- Both CI jobs pick it up automatically. The `lowest-direct` min-deps job
  resolves `sqlmodel` at its floor, so choose the floor empirically: start at
  the oldest SQLAlchemy-2.x-compatible release (`>=0.0.14`) and raise until
  the compat tests pass in that job. The floor must co-resolve with
  `SQLAlchemy>=2.0` (the resolver may lift SQLAlchemy above 2.0.0 if
  sqlmodel's own pin requires it; that is acceptable — the SQLAlchemy floor is
  still exercised by the resolver's constraint, not a hard pin).
- `pyproject.toml` keywords gain `sqlmodel`, `fastapi` for PyPI search.
- `__version__` → `2.6.0`.

## Docs & positioning

New Sphinx page `docs/fastapi.rst` — “FastAPI & SQLModel” — added to the
`index.rst` toctree (after the pytest page). Content:

1. **Models:** a `table=True` SQLModel class is a SQLAlchemy model; seed files
   and `model` paths work unchanged. Side-by-side model + seed file example.
2. **Sessions:** `sqlmodel.Session` subclasses `sqlalchemy.orm.Session` and
   works directly with `Seeder`/`HybridSeeder`; same for the async variants.
3. **Seeding at startup:** FastAPI `lifespan` snippet that loads a seed file
   on boot (docs snippet only — no shipped helper).
4. **Testing FastAPI apps:** the bundled pytest plugin with a SQLModel
   `engine` fixture (`SQLModel.metadata.create_all`), per-test rollback.
5. **CLI:** model paths pointing at SQLModel classes work as-is; one example.
6. **Troubleshooting:** unknown attribute → raw `AttributeError` (SQLModel
   quirk); forgetting `table=True` → `UnsupportedClassError`.

README gets a compact “Works with SQLModel & FastAPI” section — a minimal
copy-paste example (SQLModel model + seed file + three lines of seeding) —
linking to the docs page. Keep it short; the storefront job is “FastAPI users
are supported here”, not a tutorial.

## Out of scope (YAGNI for 2.6.0)

- Shipped FastAPI helper code (startup-seeding dependency/lifespan utility) —
  the docs snippet covers it; add code only if demand appears.
- A `[sqlmodel]` optional-dependency extra — it would only add a pin.
- Changing the unknown-attribute `AttributeError` behavior — documented
  instead; revisit with the validator work if it recurs.
- Pydantic-v1-era SQLModel versions (< 0.0.14).
- Dump/export, Alembic helper (next roadmap items).

## Release / follow-through

Ship as **v2.6.0**. On release: check off the SQLModel/FastAPI item in #65
(the last Tier 1 item) and point "next up" at the Alembic data-migration
helper (Tier 2).
