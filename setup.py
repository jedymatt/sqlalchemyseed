from setuptools import setup
from sqlalchemyseed import __version__

setup(
    name='sqlalchemyseed',
    author='jedymatt',
    url='https://github.com/jedymatt/sqlalchemyseed',
    version=__version__,
    license='MIT',
    packages=['sqlalchemyseed'],
    install_requires=['SQLAlchemy>=1.4.0'],
    python_requires='>=3.6.0'
)
