import functools
from timeit import default_timer as timer

from sqlalchemyseed import Seeder, HybridSeeder
from sqlalchemyseed import load_entities_from_json
from db import session, create_tables
from sqlalchemy import inspect, Integer, Column

DATA_PATH = 'test.json'

create_tables()


def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        func(*args, **kwargs)
        end = timer()
        # print("{}: {}".format(func.__name__, (end - start)))
        time_passed = end - start
        return time_passed

    return wrapper


entities: list = load_entities_from_json(DATA_PATH)

seeder = HybridSeeder(session)


@benchmark
def test_seed(entities_):
    seeder.seed(entities_)


def average(func, num):
    result = 0
    for _ in range(num):
        result += func()

    print('average', func.__name__, ':', round(result / num, 6))


def compare(func1, func2, num):
    count1 = 0
    count2 = 0
    for _ in range(num):
        time1 = func1()
        time2 = func2()
        if time1 < time2:
            count1 += 1
        elif time2 < time1:
            count2 += 1

    print(func1.__name__, ':', count1, ',', func2.__name__, ':', count2)


print(test_seed.__name__, ':', test_seed(entities))

# average(test_seed, 1)
# average(test_schema, 1)
#
# compare(test_seed, test_schema, 1)
from models import Parent, Base

parent = Parent()

# print(seeder.object_instances)

print(seeder.instances)
