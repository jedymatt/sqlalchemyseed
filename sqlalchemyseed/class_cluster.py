"""
MIT License

Copyright (c) 2021 Jedy Matt Tabasco

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import importlib
from sqlalchemy.exc import NoInspectionAvailable
from inspect import isclass
from sqlalchemy import inspect


def parse_class_path(class_path: str):
    try:
        module_name, class_name = class_path.rsplit('.', 1)
    except ValueError:
        raise ValueError('Invalid module or class input format.')

    # if class_name not in classes:
    class_ = getattr(importlib.import_module(module_name), class_name)

    try:
        if isclass(class_) and inspect(class_):
            return class_
        else:
            raise TypeError("'{}' is not a class".format(class_name))
    except NoInspectionAvailable:
        raise TypeError(
            "'{}' is an unsupported class".format(class_name))


class ClassCluster:
    def __init__(self):
        self._classes = {}

    def add_class(self, class_path: str):
        if class_path in self._classes.keys():
            return

        self._classes[class_path] = parse_class_path(class_path)

    def __getitem__(self, class_path: str):
        return self._classes[class_path]

    @property
    def classes(self):
        return self._classes.values()

    def clear(self):
        self._classes.clear()
