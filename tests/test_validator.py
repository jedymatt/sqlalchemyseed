import unittest


from sqlalchemyseed.validator import Key, _validate
from sqlalchemyseed.errors import InvalidJsonFormatError

validate = _validate


class TestSchemaValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.source_keys = [Key.data()]

    def test_valid_format(self):

        self.assertIsNone(validate(
            []
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": "18",
                    "$rel": {
                        "location": {
                            "where": {
                                "name": "Manila"
                            }
                        },
                        "spouse_id": {
                            "data": {
                                "name": "Juana Dela Cruz"
                            }
                        }
                    }
                }
            }
        ))

        self.assertIsNone(validate(
            [
                {
                    "model": "models.User",
                    "data": {
                        "name": "Juan Dela Cruz",
                        "age": "18",
                    }
                },
                {
                    "model": "models.User",
                    "where": {
                        "name": "Juan Dela Cruz",
                        "age": "18",
                    }
                }
            ]
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": "18",
                    "$rel": {
                        "location": {
                            "where": {
                                "name": "Manila"
                            }
                        }
                    }
                }
            }
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": "18",
                    "$rel": {
                        "location": {
                            "model": "models.Location",
                            "where": {
                                "name": "Manila"
                            }
                        }
                    }
                }
            }
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": "18",
                    "$rel": {
                        "cars": [
                            {
                                "model": "models.Car",
                                "where": {
                                    "name": "Toyota"
                                }
                            },
                            {
                                "model": "models.Car",
                                "where": {
                                    "name": "Honda"
                                }
                            }
                        ]
                    }
                }
            }
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": {
                    "name": "Juan Dela Cruz",
                    "age": "18",
                    "$rel": {
                        "cars": {
                            "model": "models.Car",
                            "where": [
                                {
                                    "name": "Toyota"
                                },
                                {
                                    "name": "Honda"
                                }
                            ]
                        }
                    }
                }
            }
        ))

        self.assertIsNone(validate(
            {
                "model": "models.User",
                "data": [
                    {
                        "name": "Juan Dela Cruz",
                    },
                    {
                        "name": "Juana Dela Cruz",
                    }
                ]
            }
        ))

    def test_invalid_format(self):
        with self.assertRaises(InvalidJsonFormatError):
            validate(1)

            validate(
                {
                    "model": "models.User",
                }
            )

            validate(
                {
                    "model": "models.User",
                    "data": {
                        "name": "Juan Dela Cruz",
                    },
                    "where": {
                        "name": "Juan Dela Cruz",
                    }
                }
            )
