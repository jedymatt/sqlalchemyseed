# Validator/Seeder Hardening — Design

**Date:** 2026-07-07
**Branch:** `fix/validator-schema-gaps`
**Status:** Approved (design), pending implementation plan

## Background

An audit of `schema.json`, `validator.py`, and `seeder.py` (see conversation
that produced this spec) surfaced four gaps between what the JSON schema
accepts, what the runtime validator accepts, and what the seeder actually does
at seed time. Two were confirmed as schema↔validator divergences via a direct
probe; two were confirmed as silent runtime failures by seeding against real
SQLAlchemy models on SQLite.

| # | Gap | schema | validator | runtime |
|---|---|---|---|---|
| 1 | Empty top-level `{}` | FAIL | PASS | seeds nothing |
| 2 | `filter` key + basic `Seeder` | PASS | FAIL (`InvalidKeyError`) | n/a |
| 3 | Forgotten `!` on a relationship | PASS | PASS | **silently dropped** |
| 4 | Array bound to a scalar (`uselist=False`) relationship | PASS | PASS | **silent last-wins data loss** |

## Goals

Close gaps **#1, #3, #4** in a single PR on `fix/validator-schema-gaps`.

- **#1** — realign the schema with the validator's existing "empty parent = seed
  nothing" backward-compat carve-out (added in `dac0dd2`).
- **#3, #4** — turn today's *silent* seed-time failures into, at minimum, a
  warning; escalate to a hard error under an opt-in `strict` flag.

## Non-goals

- **Gap #2** is out of scope. A single static JSON schema cannot know whether a
  file will be consumed by `Seeder` (rejects `filter`) or `HybridSeeder`
  (accepts it). This is a documented limitation (`schema.json`'s own
  `description` already states `filter` is HybridSeeder-only) and will be noted
  in the PR description only.
- No changes to the traversal architecture. Validation remains model-blind
  until seed time; the #3/#4 guards live at seed time precisely because they
  require ORM metadata (`attr_is_relationship`, `property.uselist`).
- No new dependencies, no new public modules.

## Part (a) — Empty-dict schema fix (#1)

`validator._pre_validate` treats an empty **top-level** dict as "seed nothing",
and only for a parent (`entity_is_parent=True`, `validator.py:110-113`). Empty
`[]` already passes the schema; only `{}` fails, because the root `anyOf` routes
a dict to `parent_entity`, which requires `model`.

**Change:** add a third branch to the root `anyOf` in
`src/sqlalchemyseed/res/schema.json`:

```json
"anyOf": [
    { "$ref": "#/definitions/parent_entity" },
    { "type": "array", "items": { "$ref": "#/definitions/parent_entity" } },
    {
        "type": "object",
        "maxProperties": 0,
        "$comment": "Empty object = seed nothing (backward compat, parent level only)."
    }
]
```

The empty-object branch is added **only at the root**. Nested/child empty dicts
still fail via `entity` (which requires `oneOf` of `data`/`filter`), matching the
validator's parent-only carve-out. This keeps the two layers in lockstep — the
explicit alignment goal of the branch.

## Part (b) — Opt-in `strict` guards (#3, #4)

### Constructor flag

Add `strict: bool = False` to all four seeders:

- `Seeder(session=None, ref_prefix="!", strict=False)`
- `HybridSeeder(session, ref_prefix="!", strict=False)`
- `AsyncSeeder(session, ref_prefix="!", strict=False)`
- `AsyncHybridSeeder(session, ref_prefix="!", strict=False)`

The async seeders wrap the sync ones through `AsyncSession.run_sync`
(`aio.py`), so they simply forward `strict` into the sync seeder they construct.
No async-specific guard logic is needed.

Default `strict=False` → **warn and keep current behavior** (non-breaking).
`strict=True` → **raise** (for CI/tests that want silent failures to be fatal).

### Guard #3 — forgotten `!`

**Location:** `filter_kwargs` (`seeder.py:63`), the shared helper both seeders
use to build constructor kwargs.

Today it silently drops any non-`!` key whose name resolves to a **relationship**
attribute (`not attr_is_relationship(...)`). New behavior for exactly those
dropped-because-relationship keys:

- `strict=True` → raise
  `errors.InvalidKeyError("'addresses' is a relationship; did you mean '!addresses'?")`
- `strict=False` → `warnings.warn(...)` with the same message, then drop as
  before.

`filter_kwargs` gains a `strict` parameter (callers pass `self.strict`). Keys
that resolve to plain columns are unaffected; the guard fires **only** when the
dropped key is a relationship — i.e. the genuine "forgotten prefix" case.

### Guard #4 — array bound to a scalar relationship

**Location:** the child-recursion point in each seeder's `_seed_children`, where
both the parent instance and the child value's shape are available
(`Seeder._seed_children` `seeder.py:173`; `HybridSeeder._seed_children`
`seeder.py:254`).

When the stripped `attr_name` resolves to a **scalar** relationship
(`attr_is_relationship` and `property.uselist is False`) **and** the child value
is a **list with more than one item**:

- `strict=True` → raise
  `errors.InvalidTypeError("relationship 'company' is scalar (uselist=False) but received a list of N items")`
- `strict=False` → `warnings.warn(...)`, then keep today's last-wins behavior.

**Only lists of length > 1 trigger the guard.** A single-element list against a
scalar relationship works correctly today (last-wins with one element is
correct), so flagging it would be a false positive.

A single shared helper (e.g. `check_scalar_cardinality(instance, attr_name,
value, strict)` in `attribute.py`) is called from both `_seed_children` sites so
the logic is defined once.

### Error types

Reuse existing `errors.InvalidKeyError` (#3) and `errors.InvalidTypeError` (#4).
No new exception classes — consistent with the error consolidation in `7c59dba`
and `dac0dd2` (e.g. `MaxLengthExceededError` collapsed into `InvalidKeyError`).

## Testing (TDD, tests written first)

Real SQLite models mirroring `tests/models.py` (a `User` with a `uselist=True`
`addresses` relationship and a scalar `uselist=False` `company` relationship).

- **#1 alignment:** assert `jsonschema.validate({}, schema)` passes **and**
  `validator.validate({})` passes — a regression test asserting the schema and
  validator **agree** on `{}`. Also assert a nested/child `{}` still fails on
  both layers.
- **#3:** `strict=False` → `pytest.warns` and the relationship is dropped;
  `strict=True` → `pytest.raises(errors.InvalidKeyError)`.
- **#4:** list of >1 against a scalar relationship → `strict=False`
  `pytest.warns` + last-wins preserved; `strict=True`
  `pytest.raises(errors.InvalidTypeError)`. A list of exactly 1 against a scalar
  relationship raises/warns **nothing** (no false positive).
- **No regressions:** existing correctly-prefixed seed data seeds identically
  under `strict=True` (guards produce no false positives); the async seeders
  forward `strict` correctly.

## Files touched

- `src/sqlalchemyseed/res/schema.json` — root `anyOf` empty-object branch.
- `src/sqlalchemyseed/seeder.py` — `strict` on `Seeder`/`HybridSeeder`;
  `filter_kwargs` gains `strict`; `_seed_children` guard calls.
- `src/sqlalchemyseed/attribute.py` — shared scalar-cardinality helper.
- `src/sqlalchemyseed/aio.py` — `strict` on async seeders, forwarded to sync.
- `tests/` — new tests for #1, #3, #4 and regression coverage.

## PR description notes

- Summarize the four-gap audit and which three this PR closes.
- Explicitly call out **#2** as a known, unencodable single-schema limitation
  that is intentionally not addressed here.
