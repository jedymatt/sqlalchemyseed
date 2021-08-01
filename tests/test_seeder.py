import unittest

from db import session
from sqlalchemyseed import Seeder


class TestSeeder(unittest.TestCase):
    def test_initialize(self):
        seeder = Seeder()
        self.assertEqual(seeder.session, None)

    def test_initialize_with_session(self):
        seeder = Seeder(session)
        self.assertEqual(seeder.session, session)

    def test_seed(self):
        # FIXME : Cannot create a list of children when 'children' type is dict
        data = {
            'model': 'models.Parent',
            'data': {
                'children': {
                    'model': 'models.Child',
                    'data': [
                        {

                        },
                        {

                        }
                    ]
                }

            }
        }
        seeder = Seeder(session)

        seeder.seed(data, add_to_session=True)
        print(seeder.instances)


if __name__ == '__main__':
    unittest.main()
