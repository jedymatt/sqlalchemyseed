import re

from setuptools import setup

# VERSION = ''
with open('sqlalchemyseed/__init__.py', 'r') as f:
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    VERSION = re.search(pattern, f.read(), re.MULTILINE).group(1)

setup(
    name='sqlalchemyseed',
    author='jedymatt',
    url='https://github.com/jedymatt/sqlalchemyseed',
    version=VERSION,
    license='MIT',
    packages=['sqlalchemyseed'],
    install_requires=['SQLAlchemy>=1.4.0'],
    python_requires='>=3.6.0'
)
