import unittest

from sqlalchemyseed.seeder import Seeder


class TestSeeder(unittest.TestCase):
    def test_seed(self):
        instance = {
            'model': 'tests.models.Company',
            'data': {
                'name': 'MyCompany',
                '!employees': {
                    'model': 'tests.models.Employee',
                    'data': [
                        {
                            'name': 'John Smith'
                        },
                        {
                            'name': 'Juan Dela Cruz'
                        }
                    ]
                }
            }
        }

        seeder = Seeder()
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 1)

    def test_seed_no_relationship(self):
        instance = {
            'model': 'tests.models.Company',
            'data': [
                {
                    'name': 'Shader',
                },
                {
                    'name': 'One'
                }
            ]
        }

        seeder = Seeder()
        # self.assertIsNone(seeder.seed(instance))
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 2)

    def test_seed_multiple_entities(self):
        instance = [
            {
                "model": "models.Company",
                "data": {
                    "name": "Mike Corporation",
                    "!employees": {
                        "model": "models.Employee",
                        "data": {
                        }
                    }
                }
            },
            {
                "model": "models.Company",
                "data": [
                    {

                    }
                ]
            },
            {
                "model": "models.Company",
                "data": {

                }
            }
        ]

        seeder = Seeder()
        seeder.seed(instance, False)
        self.assertEqual(len(seeder.instances), 3)


if __name__ == '__main__':
    unittest.main()
