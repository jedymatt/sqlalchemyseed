import functools
from timeit import default_timer as timer

import db
from sqlalchemyseed import HybridSeeder
from sqlalchemyseed import load_entities_from_json

DATA_PATH = 'test.json'


def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        res = func(*args, **kwargs)
        end = timer()
        print(end - start)
        return res

    return wrapper


db.create_tables()

data = load_entities_from_json(DATA_PATH)

seeder = HybridSeeder(db.session)


@benchmark
def test():
    seeder.seed(data)


test()
print(seeder.object_instances)
print(db.session.new)
print(db.session.dirty)
