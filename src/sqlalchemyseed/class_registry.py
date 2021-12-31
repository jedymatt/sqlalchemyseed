"""
class_registry module
"""

import importlib

from . import errors, util


def parse_class_path(class_path: str):
    """
    Parse the path of the class the specified class
    """
    try:
        module_name, class_name = class_path.rsplit('.', 1)
    except ValueError as error:
        raise errors.ParseError(
            'Invalid module or class input format.') from error

    # if class_name not in classes:
    try:
        class_ = getattr(importlib.import_module(module_name), class_name)
    except AttributeError as error:
        raise errors.NotInModuleError(
            f"{class_name} is not found in module {module_name}.") from error

    if util.is_supported_class(class_):
        return class_

    raise errors.UnsupportedClassError(
        f"'{class_name}' is an unsupported class")


class ClassRegistry:
    """
    Register classes
    """

    def __init__(self):
        self._classes = {}

    def register_class(self, class_path: str):
        """

        :param class_path: module.class (str)
        :return: registered class
        """

        if class_path not in self._classes:
            self._classes[class_path] = parse_class_path(class_path)

        return self._classes[class_path]

    def __getitem__(self, class_path: str):
        return self._classes[class_path]

    @property
    def classes(self) -> tuple:
        """
        Return tuple of registered classes
        """
        return tuple(self._classes)

    def clear(self):
        """
        Clear registered classes
        """
        self._classes.clear()
