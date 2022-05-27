import unittest

from sqlalchemyseed.json import JsonWalker


class TestJsonWalker(unittest.TestCase):
    """
    TestJsonWalker class
    """

    def setUp(self) -> None:
        self.walker = JsonWalker()

    def test_forward(self):
        """
        Test JsonWalker.forward
        """

        json = {
            'key': {
                'key_1': 'value_1',
                'arr': [
                    0,
                    1,
                    2
                ]
            }
        }

        self.walker.reset(json)
        self.walker.forward(['key', 'key_1'])
        expected_value = json['key']['key_1']
        self.assertEqual(self.walker.json, expected_value)

    def test_backward(self):
        """
        Test JsonWalker.backward
        """

        json = \
            {
                'a': {
                    'aa': {
                        'aaa': 'value'
                    }
                }
            }

        self.walker.reset(json)
        self.walker.forward(['a', 'aa', 'aaa'])
        self.walker.backward()
        self.assertEqual(self.walker.json, json['a']['aa'])
        self.walker.backward()
        self.assertEqual(self.walker.json, json['a'])


if __name__ == '__main__':
    unittest.main()
