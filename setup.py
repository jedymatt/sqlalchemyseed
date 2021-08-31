import os
import re

from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


with open(os.path.join('src', 'sqlalchemyseed', '__init__.py'), 'r') as f:
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    VERSION = re.search(pattern, f.read(), re.MULTILINE).group(1)


setup(version=VERSION,)
