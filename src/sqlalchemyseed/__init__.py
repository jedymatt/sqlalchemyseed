"""
SQLAlchemy seeder that supports nested relationships with an easy to read text files.
"""

from .seeder import HybridSeeder
from .seeder import Seeder
from .loader import load_entities_from_json
from .loader import load_entities_from_yaml
from .loader import load_entities_from_csv
from . import util
from . import attribute

try:
    # Requires SQLAlchemy's async extra (greenlet); optional for sync-only users.
    from .aio import AsyncHybridSeeder
    from .aio import AsyncSeeder
except ImportError:
    pass


__version__ = "2.5.0"

if __name__ == '__main__':
    pass
