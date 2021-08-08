import re

from readme_renderer import markdown
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

# VERSION = ''
with open('sqlalchemyseed/__init__.py', 'r') as f:
    pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
    VERSION = re.search(pattern, f.read(), re.MULTILINE).group(1)


extras_require = {
    'yaml': ['PyYAML>=5.4.0']
}


setup(
    name='sqlalchemyseed',
    author='jedymatt',
    url='https://github.com/jedymatt/sqlalchemyseed',
    long_description=markdown.render(LONG_DESCRIPTION),
    long_description_content_type='text/markdown',
    description='SQLAlchemy seeder.',
    version=VERSION,
    license='MIT',
    packages=['sqlalchemyseed'],
    # package_data={'sqlalchemyseed': ['res/*']},
    install_requires=['SQLAlchemy>=1.4.0'],
    extras_require=extras_require,
    python_requires='>=3.6.0',
    keywords='sqlalchemy seed seeder json yaml',
    project_urls={
        'Source': 'https://github.com/jedymatt/sqlalchemyseed',
        'Tracker': 'https://github.com/jedymatt/sqlalchemyseed/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
