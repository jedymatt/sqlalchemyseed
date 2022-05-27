import unittest
from sqlalchemyseed import validator

from src.sqlalchemyseed import errors
from src.sqlalchemyseed.validator import SchemaValidator, Key, hybrid_validate
from tests import instances as ins


class TestSchemaValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.source_keys = [Key.data()]

    def test_parent(self):
        self.assertIsNone(hybrid_validate(ins.PARENT))

    def test_parent_invalid(self):
        with self.assertRaises(errors.InvalidTypeError):
            hybrid_validate(ins.PARENT_INVALID)

    def test_parent_empty(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_EMPTY))

    def test_parent_empty_data_list_invalid(self):
        with self.assertRaises(errors.EmptyDataError):
            hybrid_validate(ins.PARENT_EMPTY_DATA_LIST_INVALID)

    def test_parent_missing_model_invalid(self):
        with self.assertRaises(errors.MissingKeyError):
            hybrid_validate(ins.PARENT_MISSING_MODEL_INVALID)

    def test_parent_invalid_model_invalid(self):
        with self.assertRaises(errors.InvalidTypeError):
            hybrid_validate(ins.PARENT_INVALID_MODEL_INVALID)

    def test_parent_with_extra_length_invalid(self):
        with self.assertRaises(errors.MaxLengthExceededError):
            hybrid_validate(ins.PARENT_WITH_EXTRA_LENGTH_INVALID)

    def test_parent_with_empty_data(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_WITH_EMPTY_DATA))

    def test_parent_with_multi_data(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_WITH_MULTI_DATA))

    def test_parent_without_data_invalid(self):
        self.assertRaises(errors.MissingKeyError,
                          lambda: hybrid_validate(ins.PARENT_WITHOUT_DATA_INVALID))

    def test_parent_with_data_and_invalid_data_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: hybrid_validate(ins.PARENT_WITH_DATA_AND_INVALID_DATA_INVALID))

    def test_parent_with_invalid_data_invalid(self):
        self.assertRaises(errors.InvalidTypeError,
                          lambda: hybrid_validate(ins.PARENT_WITH_INVALID_DATA_INVALID))

    def test_parent_to_child(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_TO_CHILD))

    def test_parent_to_children(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_TO_CHILDREN))

    def test_parent_to_children_without_model(self):
        self.assertIsNone(hybrid_validate(
            ins.PARENT_TO_CHILDREN_WITHOUT_MODEL))

    def test_parent_to_children_with_multi_data(self):
        self.assertIsNone(hybrid_validate(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA))

    def test_parent_to_children_with_multi_data_without_model(self):
        self.assertIsNone(hybrid_validate(
            ins.PARENT_TO_CHILDREN_WITH_MULTI_DATA_WITHOUT_MODEL))


class TestKey(unittest.TestCase):
    def test_key_equal_key(self):
        self.assertEqual(Key.model(), Key(name='model', type_=str))

    def test_key_not_equal(self):
        self.assertNotEqual(Key.model(), Key.data())

    def test_key_equal_string(self):
        self.assertEqual(Key.model(), 'model')

    def test_key_not_equal_other_instance(self):
        self.assertNotEqual(Key.model(), object())
