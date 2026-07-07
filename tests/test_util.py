"""Tests for util.get_model_class error paths."""

import pytest

from sqlalchemyseed import errors, util


def test_get_model_class_with_unsupported_class():
    with pytest.raises(errors.UnsupportedClassError, match="tests.models.UnsupportedClass"):
        util.get_model_class("tests.models.UnsupportedClass")


def test_get_model_class_with_invalid_module_path():
    with pytest.raises(errors.InvalidModelPath, match="tests.no_such_module.Thing"):
        util.get_model_class("tests.no_such_module.Thing")
