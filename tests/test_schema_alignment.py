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
