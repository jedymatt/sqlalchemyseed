import unittest
import warnings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import Seeder, errors
from tests.models import Base


class TestForgottenPrefixGuard(unittest.TestCase):
    """Gap #3: a relationship attribute written WITHOUT the '!' prefix is
    silently dropped at seed time. It must warn by default and raise when
    strict=True."""

    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _entity(self):
        # 'employees' IS a relationship on Company, but written without '!'.
        return {
            "model": "tests.models.Company",
            "data": {
                "name": "Acme",
                "employees": [
                    {"model": "tests.models.Employee", "data": {"name": "Bob"}}
                ],
            },
        }

    def test_strict_false_warns_and_drops(self):
        seeder = Seeder(self.Session(), strict=False)
        with self.assertWarns(UserWarning):
            seeder.seed(self._entity())
        company = seeder.instances[0]
        self.assertEqual(list(company.employees), [])  # relationship dropped

    def test_strict_true_raises(self):
        seeder = Seeder(self.Session(), strict=True)
        with self.assertRaises(errors.InvalidKeyError):
            seeder.seed(self._entity())

    def test_correct_prefix_seeds_and_does_not_warn_under_strict(self):
        entity = {
            "model": "tests.models.Company",
            "data": {
                "name": "Acme",
                "!employees": [
                    {"model": "tests.models.Employee", "data": {"name": "Bob"}}
                ],
            },
        }
        seeder = Seeder(self.Session(), strict=True)
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning would fail the test
            seeder.seed(entity)
        company = seeder.instances[0]
        self.assertEqual({e.name for e in company.employees}, {"Bob"})


class TestScalarCardinalityGuard(unittest.TestCase):
    """Gap #4: a list bound to a scalar (uselist=False) relationship silently
    keeps only the last element. A list of >1 must warn by default and raise
    when strict=True; a list of exactly 1 is fine (no false positive)."""

    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def _entity(self, n):
        # Employee.company is uselist=False (scalar); feed it a list of n.
        companies = [
            {"model": "tests.models.Company", "data": {"name": f"C{i}"}}
            for i in range(n)
        ]
        return {
            "model": "tests.models.Employee",
            "data": {"name": "Bob", "!company": companies},
        }

    def test_list_gt_1_strict_false_warns(self):
        seeder = Seeder(self.Session(), strict=False)
        with self.assertWarns(UserWarning):
            seeder.seed(self._entity(2))

    def test_list_gt_1_strict_true_raises(self):
        seeder = Seeder(self.Session(), strict=True)
        with self.assertRaises(errors.InvalidTypeError):
            seeder.seed(self._entity(2))

    def test_list_eq_1_no_warning_even_strict(self):
        seeder = Seeder(self.Session(), strict=True)
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # any warning would fail the test
            seeder.seed(self._entity(1))
        employee = seeder.instances[0]
        self.assertEqual(employee.company.name, "C0")
