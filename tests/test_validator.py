import unittest

from sqlalchemyseed import errors
from sqlalchemyseed.validator import SchemaValidator
from tests import instances as ins


class TestSchemaValidator(unittest.TestCase):

    def test_parent(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT))

    def test_parent_with_extra_length_invalid(self):
        self.assertRaises(errors.MaxLengthExceededError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITH_EXTRA_LENGTH_INVALID))

    def test_parent_with_empty_data(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_WITH_EMPTY_DATA))

    def test_parent_with_multi_data(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_WITH_MULTI_DATA))

    def test_parent_without_data_invalid(self):
        self.assertRaises(errors.MissingRequiredKeyError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITHOUT_DATA_INVALID))

    def test_parent_to_child(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_TO_CHILD))

    def test_parent_to_children(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_TO_CHILDREN))

    def test_parent_to_children_without_model(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_TO_CHILDREN_WITHOUT_MODEL))

    def test_parent_to_children_with_multi_data(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA))

    def test_parent_to_children_with_multi_data_without_model(self):
        self.assertIsNone(SchemaValidator.validate(ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA_WITHOUT_MODEL))
