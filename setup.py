import re

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# VERSION = ''
with open('sqlalchemyseed/__init__.py', 'r') as f:
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    VERSION = re.search(pattern, f.read(), re.MULTILINE).group(1)

setup(
    name='sqlalchemyseed',
    author='jedymatt',
    url='https://github.com/jedymatt/sqlalchemyseed',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version=VERSION,
    license='MIT',
    packages=['sqlalchemyseed'],
    install_requires=['SQLAlchemy>=1.4.0'],
    python_requires='>=3.6.0'
)
