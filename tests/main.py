import functools
from timeit import default_timer as timer

from sqlalchemyseed import BasicSeeder
from sqlalchemyseed import Seeder
from sqlalchemyseed import load_entities_from_json
from db import session

DATA_PATH = 'test.json'


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

schema = BasicSeeder()
seeder = Seeder()


@benchmark
def test_schema(entities_):
    schema.root(entities_)


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


arr = []

for _ in range(100):
    arr.extend(entities)

print(test_seed.__name__, ':', test_seed(arr))

print(test_schema.__name__, ':', test_schema(arr))

# average(test_seed, 1)
# average(test_schema, 1)
#
# compare(test_seed, test_schema, 1)

print(seeder.object_instances)
print(schema.instances)
session.add_all(schema.instances)
print(session.new)
