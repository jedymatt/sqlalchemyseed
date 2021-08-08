import re

from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


with open('sqlalchemyseed/__init__.py', 'r') as f:
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    VERSION = re.search(pattern, f.read(), re.MULTILINE).group(1)


packages = ['sqlalchemyseed']

install_requires = [
    'SQLAlchemy>=1.4',
]

extras_require = {
    'yaml': ['PyYAML>=5.4']
}


setup(
    name='sqlalchemyseed',
    version=VERSION,
    description='SQLAlchemy seeder.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/jedymatt/sqlalchemyseed',
    author='jedymatt',
    author_email='jedymatt@gmail.com',
    license='MIT',
    packages=packages,
    # package_data={'sqlalchemyseed': ['res/*']},
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires='>=3.6',
    project_urls={
        'Source': 'https://github.com/jedymatt/sqlalchemyseed',
        'Tracker': 'https://github.com/jedymatt/sqlalchemyseed/issues',
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='sqlalchemy, seed, seeder, json, yaml',
)
