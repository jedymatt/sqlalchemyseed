import unittest
from sqlalchemyseed import validator

from src.sqlalchemyseed import errors
from src.sqlalchemyseed.validator import SchemaValidator, Key, hybrid_validate, validate
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

    def test_parent_with_unknown_key_invalid(self):
        with self.assertRaises(errors.InvalidKeyError):
            hybrid_validate(ins.PARENT_WITH_UNKNOWN_KEY_INVALID)

    def test_parent_empty_dict(self):
        self.assertIsNone(hybrid_validate(ins.PARENT_EMPTY_DICT))

    def test_parent_with_non_string_attribute_invalid(self):
        with self.assertRaises(errors.InvalidTypeError):
            hybrid_validate(ins.PARENT_WITH_NON_STRING_ATTRIBUTE_INVALID)

    def test_parent_with_data_and_filter_invalid(self):
        with self.assertRaises(errors.InvalidKeyError):
            hybrid_validate(ins.PARENT_WITH_DATA_AND_FILTER_INVALID)

    def test_child_empty_dict_invalid(self):
        with self.assertRaises(errors.MissingKeyError):
            hybrid_validate(ins.PARENT_TO_CHILD_EMPTY_INVALID)

    def test_child_with_unknown_key_invalid(self):
        with self.assertRaises(errors.InvalidKeyError):
            hybrid_validate(ins.PARENT_TO_CHILD_UNKNOWN_KEY_INVALID)

    def test_basic_validate_rejects_filter_key(self):
        with self.assertRaises(errors.InvalidKeyError):
            validate(ins.BASIC_PARENT_WITH_FILTER_INVALID)

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
