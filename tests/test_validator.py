import unittest

from sqlalchemyseed.validator import SchemaValidator


class TestSchemaValidator(unittest.TestCase):

    def test_valid_empty_entity(self):
        instance = [

        ]
        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_empty_entities(self):
        instance = [
            {}
        ]
        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_entity_with_empty_args(self):
        instance = {
            'model': 'models.Company',
            'data': {

            }
        }
        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_entity_with_args(self):
        instance = {
            'model': 'models.Company',
            'data': {
                'name': 'Company Name'
            }
        }

        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_entities_with_empty_args(self):
        instance = [
            {
                'model': 'models.Company',
                'data': {

                }
            },
            {
                'model': 'models.Company',
                'data': {

                }
            }
        ]

        self.assertIsNone(SchemaValidator.validate(instance))

    def test_entity_with_relationship(self):
        instance = [
            {
                'model': 'models.Company',
                'data': {
                    '!employees': {
                        'model': 'models.Employee',
                        'data': {

                        }
                    }
                }
            },
        ]

        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_entity_relationships(self):
        instance = [
            {
                'model': 'models.Company',
                'data': {
                    '!employees': {
                        'model': 'models.Employee',
                        'data': {

                        }
                    }
                }
            },
        ]

        self.assertIsNone(SchemaValidator.validate(instance))

    def test_invalid_entity_with_empty_relationships(self):
        instance = [
            {
                'model': 'models.Company',
                'data':
                    {
                        '!employees': {
                            'model': 'models.Employee',
                            'data': [

                            ]
                        }
                    }

            },
        ]
        self.assertRaises(ValueError, lambda: SchemaValidator.validate(instance))

    def test_valid_empty_relationships_list(self):
        instance = [
            {
                'model': 'models.Company',
                'data':
                    {
                        '!employees': []
                    }
            },
        ]

        self.assertIsNone(SchemaValidator.validate(instance))

    def test_valid_empty_relationships_dict(self):
        instance = [
            {
                'model': 'models.Company',
                'data':
                    {
                        '!employees': {}
                    }
            },
        ]

        self.assertIsNone(SchemaValidator.validate(instance))


if __name__ == '__main__':
    unittest.main()
