# Validator/Seeder Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close three schema/validator/seeder gaps in one PR — realign the JSON schema with the validator's empty-parent carve-out (#1), and surface two silent seed-time failures (forgotten `!` #3, array→scalar relationship #4) as warnings by default and hard errors under an opt-in `strict` flag.

**Architecture:** (a) is a one-branch addition to `res/schema.json`'s root `anyOf`, verified by a test asserting schema and validator agree on `{}`. (b) adds `strict: bool = False` to all four seeders; the forgotten-`!` guard lives in the shared `filter_kwargs` helper, and the scalar-cardinality guard lives in a new shared `attribute.check_scalar_cardinality` helper called from both seeders' `_seed_children`. The async seeders wrap the sync ones via `run_sync`, so they only forward the flag.

**Tech Stack:** Python ≥3.10, SQLAlchemy ≥2.0, `unittest` + `pytest` runner (via `uv run pytest`), `jsonschema` (new dev-only dependency for the alignment test), in-memory SQLite.

## Global Constraints

- Python floor: `requires-python = ">=3.10"` — no newer-only syntax.
- Runtime dependencies unchanged (`SQLAlchemy>=2.0` only). `jsonschema` is added to the **dev** dependency group only, never to `[project].dependencies`.
- Reuse existing exception classes from `src/sqlalchemyseed/errors.py`: `InvalidKeyError` for #3, `InvalidTypeError` for #4. Do **not** add new exception classes.
- Default behavior is non-breaking: `strict=False` warns (via `warnings.warn`, default `UserWarning`) and preserves today's runtime behavior; `strict=True` raises.
- Tests are `unittest.TestCase` / `unittest.IsolatedAsyncioTestCase` style, matching the existing suite. Models come from `tests/models.py` (`Company.employees` is a collection; `Employee.company` is `uselist=False`).
- Run tests with `uv run pytest`.
- Commit messages end with the repo's trailer:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

### Task 1: Empty-dict schema fix + alignment test (#1)

**Files:**
- Modify: `src/sqlalchemyseed/res/schema.json` (root `anyOf`, lines 86-96)
- Modify: `pyproject.toml` (`[dependency-groups] dev`, add `jsonschema`)
- Create: `tests/test_schema_alignment.py`

**Interfaces:**
- Consumes: `sqlalchemyseed.validator.validate` (existing).
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Add `jsonschema` to the dev dependency group**

Run:
```bash
uv add --dev jsonschema
```
Expected: `pyproject.toml` gains `jsonschema` under `[dependency-groups] dev`; `uv.lock` updates; the package installs into the project env.

- [ ] **Step 2: Write the failing alignment test**

Create `tests/test_schema_alignment.py`:
```python
import json
import unittest
from importlib.resources import files

import jsonschema

from sqlalchemyseed import validator
from sqlalchemyseed import errors


def _load_schema():
    text = files("sqlalchemyseed").joinpath("res/schema.json").read_text()
    return json.loads(text)


class TestSchemaValidatorAlignment(unittest.TestCase):
    """The shipped schema.json must accept/reject the same top-level shapes
    the runtime validator does. See gap #1: the validator treats an empty
    top-level dict as 'seed nothing', but the schema rejected it."""

    def setUp(self):
        self.schema = _load_schema()

    def test_empty_top_level_dict_accepted_by_both(self):
        # schema side: must not raise
        jsonschema.validate({}, self.schema)
        # validator side: already accepts (backward-compat carve-out)
        self.assertIsNone(validator.validate({}))

    def test_empty_top_level_list_accepted_by_both(self):
        jsonschema.validate([], self.schema)
        self.assertIsNone(validator.validate([]))

    def test_empty_child_dict_rejected_by_both(self):
        # The carve-out is parent-only: an empty CHILD dict is still invalid.
        entity = {"model": "m.User", "data": {"!addr": {}}}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(entity, self.schema)
        with self.assertRaises(errors.MissingKeyError):
            validator.validate(entity)
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `uv run pytest tests/test_schema_alignment.py -v`
Expected: `test_empty_top_level_dict_accepted_by_both` FAILS with a `jsonschema.exceptions.ValidationError` ({} does not match the schema, because the root `anyOf` routes a dict to `parent_entity`, which requires `model`). The other two tests PASS.

- [ ] **Step 4: Add the empty-object branch to the schema root**

In `src/sqlalchemyseed/res/schema.json`, replace the root `anyOf` (currently the last block, lines 86-96):
```json
    "anyOf": [
        {
            "$ref": "#/definitions/parent_entity"
        },
        {
            "type": "array",
            "items": {
                "$ref": "#/definitions/parent_entity"
            }
        }
    ]
```
with:
```json
    "anyOf": [
        {
            "$ref": "#/definitions/parent_entity"
        },
        {
            "type": "array",
            "items": {
                "$ref": "#/definitions/parent_entity"
            }
        },
        {
            "type": "object",
            "maxProperties": 0,
            "$comment": "Empty object = seed nothing (backward compat, parent level only)."
        }
    ]
```
Note: the empty-object branch is added only at the root. Child entities still reference `#/definitions/entity` (which requires one of `data`/`filter`), so a nested empty `{}` still fails — matching the validator's parent-only carve-out.

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_schema_alignment.py -v`
Expected: all three tests PASS.

- [ ] **Step 6: Run the full suite to confirm no regressions**

Run: `uv run pytest -q`
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/sqlalchemyseed/res/schema.json pyproject.toml uv.lock tests/test_schema_alignment.py
git commit -m "fix(schema): accept empty top-level object, aligning with validator

Closes gap #1: the validator treats an empty top-level dict as 'seed
nothing', but schema.json rejected it. Adds an empty-object branch to the
root anyOf (parent level only). Adds jsonschema as a dev dep for the
schema/validator alignment test.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Forgotten-`!` guard + `strict` flag on sync seeders (#3)

**Files:**
- Modify: `src/sqlalchemyseed/seeder.py` (imports; `filter_kwargs` lines 63-70; `Seeder.__init__` line 78; `Seeder._seed` line 151; `HybridSeeder.__init__` line 192; `HybridSeeder._setup_instance` line 260)
- Create: `tests/test_seeder_strict.py`

**Interfaces:**
- Consumes: `attribute.attr_is_relationship`, `attribute.instrumented_attribute`, `util.iter_non_ref_kwargs`, `errors.InvalidKeyError` (all existing).
- Produces:
  - `Seeder(session=None, ref_prefix="!", strict=False)` — new `self.strict` attribute.
  - `HybridSeeder(session, ref_prefix="!", strict=False)` — new `self.strict` attribute.
  - `filter_kwargs(kwargs, class_, ref_prefix, strict=False)` — new trailing param.

- [ ] **Step 1: Write the failing test**

Create `tests/test_seeder_strict.py`:
```python
import unittest
import warnings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import Seeder, errors
from tests.models import Base


class TestForgottenPrefixGuard(unittest.TestCase):
    """Gap #3: a relationship attribute written WITHOUT the '!' prefix is
    silently dropped at seed time. It must warn by default and raise when
    strict=True."""

    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _entity(self):
        # 'employees' IS a relationship on Company, but written without '!'.
        return {
            "model": "tests.models.Company",
            "data": {
                "name": "Acme",
                "employees": [
                    {"model": "tests.models.Employee", "data": {"name": "Bob"}}
                ],
            },
        }

    def test_strict_false_warns_and_drops(self):
        seeder = Seeder(self.Session(), strict=False)
        with self.assertWarns(UserWarning):
            seeder.seed(self._entity())
        company = seeder.instances[0]
        self.assertEqual(list(company.employees), [])  # relationship dropped

    def test_strict_true_raises(self):
        seeder = Seeder(self.Session(), strict=True)
        with self.assertRaises(errors.InvalidKeyError):
            seeder.seed(self._entity())

    def test_correct_prefix_seeds_and_does_not_warn_under_strict(self):
        entity = {
            "model": "tests.models.Company",
            "data": {
                "name": "Acme",
                "!employees": [
                    {"model": "tests.models.Employee", "data": {"name": "Bob"}}
                ],
            },
        }
        seeder = Seeder(self.Session(), strict=True)
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning would fail the test
            seeder.seed(entity)
        company = seeder.instances[0]
        self.assertEqual({e.name for e in company.employees}, {"Bob"})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_seeder_strict.py::TestForgottenPrefixGuard -v`
Expected: `test_strict_false_warns_and_drops` FAILS (no warning emitted — currently silent) and `test_strict_true_raises` FAILS with `TypeError` (`Seeder.__init__` has no `strict` argument yet).

- [ ] **Step 3: Add `import warnings` to seeder.py**

At the top of `src/sqlalchemyseed/seeder.py`, change:
```python
import abc
from typing import NamedTuple, Union
```
to:
```python
import abc
import warnings
from typing import NamedTuple, Union
```

- [ ] **Step 4: Rewrite `filter_kwargs` to guard forgotten `!`**

Replace `filter_kwargs` (lines 63-70):
```python
def filter_kwargs(kwargs: dict, class_, ref_prefix):
    """
    Filters kwargs
    """
    return {
        k: v for k, v in util.iter_non_ref_kwargs(kwargs, ref_prefix)
        if not attr_is_relationship(instrumented_attribute(class_, str(k)))
    }
```
with:
```python
def filter_kwargs(kwargs: dict, class_, ref_prefix, strict=False):
    """
    Filters kwargs, dropping keys that name a relationship attribute.

    A non-prefixed key that resolves to a relationship is a forgotten
    ``ref_prefix`` (gap #3): such a key is silently ignored by the model
    constructor. When ``strict`` is True this raises; otherwise it warns and
    drops the key (preserving historical behavior).
    """
    result = {}
    for k, v in util.iter_non_ref_kwargs(kwargs, ref_prefix):
        if attr_is_relationship(instrumented_attribute(class_, str(k))):
            message = (
                f"{str(k)!r} is a relationship attribute; "
                f"did you mean {ref_prefix}{k}?"
            )
            if strict:
                raise errors.InvalidKeyError(message)
            warnings.warn(message)
            continue
        result[k] = v
    return result
```

- [ ] **Step 5: Thread `strict` through `Seeder`**

In `Seeder.__init__` (line 78), change:
```python
    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!"):
        self.session = session
        self.ref_prefix = ref_prefix
```
to:
```python
    def __init__(self, session: sqlalchemy.orm.Session = None, ref_prefix="!", strict=False):
        self.session = session
        self.ref_prefix = ref_prefix
        self.strict = strict
```
In `Seeder._seed`'s `init_item` (line 151), change:
```python
            filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)
```
to:
```python
            filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix, self.strict)
```

- [ ] **Step 6: Thread `strict` through `HybridSeeder`**

In `HybridSeeder.__init__` (line 192), change:
```python
    def __init__(self, session: sqlalchemy.orm.Session, ref_prefix: str = '!'):
        self.session = session
        self._instances = []
        self.ref_prefix = ref_prefix
        self._walker = JsonWalker()
        self._parent = None
```
to:
```python
    def __init__(self, session: sqlalchemy.orm.Session, ref_prefix: str = '!', strict: bool = False):
        self.session = session
        self._instances = []
        self.ref_prefix = ref_prefix
        self.strict = strict
        self._walker = JsonWalker()
        self._parent = None
```
In `HybridSeeder._setup_instance` (line 260), change:
```python
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix)
```
to:
```python
        filtered_kwargs = filter_kwargs(kwargs, class_, self.ref_prefix, self.strict)
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `uv run pytest tests/test_seeder_strict.py::TestForgottenPrefixGuard -v`
Expected: all three tests PASS.

- [ ] **Step 8: Run the full suite to confirm no regressions**

Run: `uv run pytest -q`
Expected: all tests pass (existing seed data uses `!`-prefixed relationships, so no false positives).

- [ ] **Step 9: Commit**

```bash
git add src/sqlalchemyseed/seeder.py tests/test_seeder_strict.py
git commit -m "fix(seeder): surface forgotten '!' relationship prefix (gap #3)

A non-prefixed key naming a relationship was silently dropped by the model
constructor. filter_kwargs now warns (default) or raises InvalidKeyError
(strict=True). Adds a strict flag to Seeder and HybridSeeder.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Array→scalar relationship guard (#4)

**Files:**
- Modify: `src/sqlalchemyseed/attribute.py` (add `import warnings`, `from . import errors`, new `check_scalar_cardinality` function)
- Modify: `src/sqlalchemyseed/seeder.py` (import `check_scalar_cardinality`; call in `Seeder._seed_children` line 173-184 and `HybridSeeder._seed_children` line 254-257)
- Modify: `tests/test_seeder_strict.py` (add a second test class)

**Interfaces:**
- Consumes: `Seeder`/`HybridSeeder` `self.strict` (from Task 2); `attribute.attr_is_relationship`, `attribute.instrumented_attribute`; `errors.InvalidTypeError`.
- Produces: `attribute.check_scalar_cardinality(instance, attr_name, value, strict=False)` — no-op unless `attr_name` is a scalar (`uselist=False`) relationship and `value` is a list of length > 1.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_seeder_strict.py`:
```python
class TestScalarCardinalityGuard(unittest.TestCase):
    """Gap #4: a list bound to a scalar (uselist=False) relationship silently
    keeps only the last element. A list of >1 must warn by default and raise
    when strict=True; a list of exactly 1 is fine (no false positive)."""

    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _entity(self, n):
        # Employee.company is uselist=False (scalar); feed it a list of n.
        companies = [
            {"model": "tests.models.Company", "data": {"name": f"C{i}"}}
            for i in range(n)
        ]
        return {
            "model": "tests.models.Employee",
            "data": {"name": "Bob", "!company": companies},
        }

    def test_list_gt_1_strict_false_warns(self):
        seeder = Seeder(self.Session(), strict=False)
        with self.assertWarns(UserWarning):
            seeder.seed(self._entity(2))

    def test_list_gt_1_strict_true_raises(self):
        seeder = Seeder(self.Session(), strict=True)
        with self.assertRaises(errors.InvalidTypeError):
            seeder.seed(self._entity(2))

    def test_list_eq_1_no_warning_even_strict(self):
        seeder = Seeder(self.Session(), strict=True)
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning would fail the test
            seeder.seed(self._entity(1))
        employee = seeder.instances[0]
        self.assertEqual(employee.company.name, "C0")
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_seeder_strict.py::TestScalarCardinalityGuard -v`
Expected: `test_list_gt_1_strict_false_warns` FAILS (no warning — currently silent) and `test_list_gt_1_strict_true_raises` FAILS (no exception raised). `test_list_eq_1_no_warning_even_strict` PASSES.

- [ ] **Step 3: Add the guard helper to attribute.py**

At the top of `src/sqlalchemyseed/attribute.py`, change:
```python
from functools import lru_cache
from inspect import isclass

from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute, get_attribute, set_attribute
```
to:
```python
import warnings
from functools import lru_cache
from inspect import isclass

from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute, get_attribute, set_attribute

from . import errors
```
Then add this function (place it after `set_instance_attribute`, i.e. after line 47):
```python
def check_scalar_cardinality(instance, attr_name, value, strict=False):
    """
    Guard against binding a list to a scalar relationship (gap #4).

    A scalar relationship (``uselist=False``) given a list keeps only the last
    element via repeated assignment — silent data loss. When ``value`` is a
    list of more than one item, this raises if ``strict`` else warns. A
    single-element list is left alone (assigning one element is correct).
    """
    instr_attr = instrumented_attribute(instance, attr_name)
    if not attr_is_relationship(instr_attr):
        return
    if instr_attr.property.uselist:
        return
    if not isinstance(value, list) or len(value) <= 1:
        return
    message = (
        f"relationship {attr_name!r} is scalar (uselist=False) but received "
        f"a list of {len(value)} items"
    )
    if strict:
        raise errors.InvalidTypeError(message)
    warnings.warn(message)
```

- [ ] **Step 4: Import the helper in seeder.py**

In `src/sqlalchemyseed/seeder.py`, change the import (lines 12-13):
```python
from .attribute import (attr_is_column, attr_is_relationship, foreign_key_column, instrumented_attribute,
                        referenced_class, set_instance_attribute)
```
to:
```python
from .attribute import (attr_is_column, attr_is_relationship, check_scalar_cardinality,
                        foreign_key_column, instrumented_attribute, referenced_class,
                        set_instance_attribute)
```

- [ ] **Step 5: Call the guard in `Seeder._seed_children`**

Replace `Seeder._seed_children` (lines 173-184):
```python
    def _seed_children(self, instance):
        # expected json is dict:
        # {'model': ...}
        def seed_child():
            key = self._walker.current_key
            if key.startswith(self.ref_prefix):
                attr_name = key[len(self.ref_prefix):]
                self._current_parent = InstanceAttributeTuple(
                    instance, attr_name)
                self._pre_seed()

        self._walker.exec_func_iter(seed_child)
```
with:
```python
    def _seed_children(self, instance):
        # expected json is dict:
        # {'model': ...}
        def seed_child():
            key = self._walker.current_key
            if key.startswith(self.ref_prefix):
                attr_name = key[len(self.ref_prefix):]
                check_scalar_cardinality(
                    instance, attr_name, self._walker.json, self.strict)
                self._current_parent = InstanceAttributeTuple(
                    instance, attr_name)
                self._pre_seed()

        self._walker.exec_func_iter(seed_child)
```
(Here `self._walker.json` is the value at the current `!`-prefixed key — a dict or list.)

- [ ] **Step 6: Call the guard in `HybridSeeder._seed_children`**

Replace `HybridSeeder._seed_children` (lines 254-257):
```python
    def _seed_children(self, instance, kwargs):
        for attr_name, value in util.iter_ref_kwargs(kwargs, self.ref_prefix):
            self._pre_seed(
                entity=value, parent=InstanceAttributeTuple(instance, attr_name))
```
with:
```python
    def _seed_children(self, instance, kwargs):
        for attr_name, value in util.iter_ref_kwargs(kwargs, self.ref_prefix):
            check_scalar_cardinality(instance, attr_name, value, self.strict)
            self._pre_seed(
                entity=value, parent=InstanceAttributeTuple(instance, attr_name))
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `uv run pytest tests/test_seeder_strict.py::TestScalarCardinalityGuard -v`
Expected: all three tests PASS.

- [ ] **Step 8: Run the full suite to confirm no regressions**

Run: `uv run pytest -q`
Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add src/sqlalchemyseed/attribute.py src/sqlalchemyseed/seeder.py tests/test_seeder_strict.py
git commit -m "fix(seeder): guard list bound to scalar relationship (gap #4)

A list of >1 given to a uselist=False relationship silently kept only the
last element. check_scalar_cardinality now warns (default) or raises
InvalidTypeError (strict=True). A single-element list is unaffected.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Forward `strict` through the async seeders

**Files:**
- Modify: `src/sqlalchemyseed/aio.py` (`AsyncSeeder.__init__`/`.seed`; `AsyncHybridSeeder.__init__`/`.seed`)
- Modify: `tests/test_async_seeder.py` (add a test)

**Interfaces:**
- Consumes: `Seeder`/`HybridSeeder` `strict` kwarg (from Task 2); `errors.InvalidTypeError`.
- Produces:
  - `AsyncSeeder(session, ref_prefix="!", strict=False)`
  - `AsyncHybridSeeder(session, ref_prefix="!", strict=False)`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_async_seeder.py` (inside `AsyncSeederTestCase`, before the `if __name__` block — add these methods to the class):
```python
    async def test_async_strict_raises_on_scalar_list(self):
        import sqlalchemyseed.errors as errors
        entities = {
            "model": "tests.models.Employee",
            "data": {
                "name": "Bob",
                "!company": [
                    {"model": "tests.models.Company", "data": {"name": "C0"}},
                    {"model": "tests.models.Company", "data": {"name": "C1"}},
                ],
            },
        }
        seeder = AsyncSeeder(self.session, strict=True)
        with self.assertRaises(errors.InvalidTypeError):
            await seeder.seed(entities)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_async_seeder.py::AsyncSeederTestCase::test_async_strict_raises_on_scalar_list -v`
Expected: FAILS with `TypeError` (`AsyncSeeder.__init__` has no `strict` argument yet).

- [ ] **Step 3: Forward `strict` in `AsyncSeeder`**

In `src/sqlalchemyseed/aio.py`, change `AsyncSeeder.__init__` and `.seed` (lines 21-32):
```python
    def __init__(self, session: AsyncSession, ref_prefix: str = "!"):
        self.session = session
        self.ref_prefix = ref_prefix
        self._seeder: Seeder = None

    async def seed(self, entities: Union[list, dict], add_to_session: bool = True):
        def _run(sync_session):
            seeder = Seeder(sync_session, ref_prefix=self.ref_prefix)
            seeder.seed(entities, add_to_session=add_to_session)
            return seeder

        self._seeder = await self.session.run_sync(_run)
```
to:
```python
    def __init__(self, session: AsyncSession, ref_prefix: str = "!", strict: bool = False):
        self.session = session
        self.ref_prefix = ref_prefix
        self.strict = strict
        self._seeder: Seeder = None

    async def seed(self, entities: Union[list, dict], add_to_session: bool = True):
        def _run(sync_session):
            seeder = Seeder(sync_session, ref_prefix=self.ref_prefix, strict=self.strict)
            seeder.seed(entities, add_to_session=add_to_session)
            return seeder

        self._seeder = await self.session.run_sync(_run)
```

- [ ] **Step 4: Forward `strict` in `AsyncHybridSeeder`**

In `src/sqlalchemyseed/aio.py`, change `AsyncHybridSeeder.__init__` and `.seed` (lines 47-58):
```python
    def __init__(self, session: AsyncSession, ref_prefix: str = "!"):
        self.session = session
        self.ref_prefix = ref_prefix
        self._seeder: HybridSeeder = None

    async def seed(self, entities: Union[list, dict]):
        def _run(sync_session):
            seeder = HybridSeeder(sync_session, ref_prefix=self.ref_prefix)
            seeder.seed(entities)
            return seeder

        self._seeder = await self.session.run_sync(_run)
```
to:
```python
    def __init__(self, session: AsyncSession, ref_prefix: str = "!", strict: bool = False):
        self.session = session
        self.ref_prefix = ref_prefix
        self.strict = strict
        self._seeder: HybridSeeder = None

    async def seed(self, entities: Union[list, dict]):
        def _run(sync_session):
            seeder = HybridSeeder(sync_session, ref_prefix=self.ref_prefix, strict=self.strict)
            seeder.seed(entities)
            return seeder

        self._seeder = await self.session.run_sync(_run)
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_async_seeder.py::AsyncSeederTestCase::test_async_strict_raises_on_scalar_list -v`
Expected: PASS.

- [ ] **Step 6: Run the full suite to confirm no regressions**

Run: `uv run pytest -q`
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/sqlalchemyseed/aio.py tests/test_async_seeder.py
git commit -m "fix(aio): forward strict flag to async seeders

AsyncSeeder and AsyncHybridSeeder now accept strict and pass it into the
sync seeder they wrap, so the #3/#4 guards apply to async seeding too.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Final self-review checklist (run after all tasks)

- [ ] `uv run pytest -q` — full suite green.
- [ ] `git log --oneline main..HEAD` shows the design-doc commit plus four fix commits.
- [ ] PR description drafted: summarize the four-gap audit; state this PR closes #1, #3, #4; explicitly note **#2** (`filter` passes schema but the basic `Seeder` rejects it) is a known, unencodable single-schema limitation intentionally left out of scope.
