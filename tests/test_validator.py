import unittest
from sqlalchemyseed import validator

from src.sqlalchemyseed import errors
from src.sqlalchemyseed.validator import SchemaValidator, Key
from tests import instances as ins


class TestSchemaValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.source_keys = [Key.data()]

    def test_parent(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT, source_keys=self.source_keys))

    def test_parent_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: SchemaValidator.validate(ins.PARENT_INVALID, source_keys=self.source_keys))

    def test_parent_empty(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_EMPTY, source_keys=self.source_keys))

    def test_parent_empty_data_list_invalid(self):
        self.assertRaises(errors.EmptyDataError,
                          lambda: SchemaValidator.validate(ins.PARENT_EMPTY_DATA_LIST_INVALID, source_keys=self.source_keys))

    def test_parent_missing_model_invalid(self):
        self.assertRaises(errors.MissingKeyError,
                          lambda: SchemaValidator.validate(ins.PARENT_MISSING_MODEL_INVALID, source_keys=self.source_keys))

    def test_parent_invalid_model_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: SchemaValidator.validate(ins.PARENT_INVALID_MODEL_INVALID, source_keys=self.source_keys))

    def test_parent_with_extra_length_invalid(self):
        self.assertRaises(errors.MaxLengthExceededError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITH_EXTRA_LENGTH_INVALID, source_keys=self.source_keys))

    def test_parent_with_empty_data(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_WITH_EMPTY_DATA, source_keys=self.source_keys))

    def test_parent_with_multi_data(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_WITH_MULTI_DATA, source_keys=self.source_keys))

    def test_parent_without_data_invalid(self):
        self.assertRaises(errors.MissingKeyError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITHOUT_DATA_INVALID, source_keys=self.source_keys))

    def test_parent_with_data_and_invalid_data_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITH_DATA_AND_INVALID_DATA_INVALID, source_keys=self.source_keys))

    def test_parent_with_invalid_data_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: SchemaValidator.validate(ins.PARENT_WITH_INVALID_DATA_INVALID, source_keys=self.source_keys))

    def test_parent_to_child(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_TO_CHILD, source_keys=self.source_keys))

    def test_parent_to_children(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_TO_CHILDREN, source_keys=self.source_keys))

    def test_parent_to_children_without_model(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_TO_CHILDREN_WITHOUT_MODEL, source_keys=self.source_keys))

    def test_parent_to_children_with_multi_data(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA, source_keys=self.source_keys))

    def test_parent_to_children_with_multi_data_without_model(self):
        self.assertIsNone(SchemaValidator.validate(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA_WITHOUT_MODEL, source_keys=self.source_keys))


class TestKey(unittest.TestCase):
    def test_key_equal_key(self):
        self.assertEqual(Key.model(), Key(name='model', type_=str))

    def test_key_not_equal(self):
        self.assertNotEqual(Key.model(), Key.data())

    def test_key_equal_string(self):
        self.assertEqual(Key.model(), 'model')

    def test_key_not_equal_other_instance(self):
        self.assertNotEqual(Key.model(), object())
