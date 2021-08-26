PARENT = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company'
    }
}

PARENT_WITH_EXTRA_LENGTH_INVALID = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company'
    },
    'extra': 'extra value'
}

PARENT_WITH_EMPTY_DATA = {
    'model': 'tests.models.Company',
    'data': {}
}

PARENT_WITHOUT_DATA_INVALID = {
    'model': 'tests.models.Company'
}

PARENT_WITH_MULTI_DATA = {
    'model': 'tests.models.Company',
    'data': [
        {
            'name': 'My Company'
        },
        {
            'name': 'Second Company'
        }
    ]
}

PARENTS = [
    {
        'model': 'tests.models.Company',
        'data': {
            'name': 'My Company'
        }
    },
    {
        'model': 'tests.models.Company',
        'data': {
            'name': 'Another Company'
        }
    }
]

PARENTS_WITH_EMPTY_DATA = [
    {
        'model': 'tests.models.Company',
        'data': {}
    },
    {
        'model': 'tests.models.Company',
        'data': {}
    }
]

PARENTS_WITHOUT_DATA_INVALID = [
    {
        'model': 'tests.models.Company'
    },
    {
        'model': 'tests.models.Company'
    }
]

PARENTS_WITH_MULTI_DATA = [
    {
        'model': 'tests.models.Company',
        'data': [
            {
                'name': 'My Company'
            },
            {
                'name': 'Second Company'
            }
        ]
    },
    {
        'model': 'tests.models.Company',
        'data': [
            {
                'name': 'Third Company'
            },
            {
                'name': 'Fourth Company'
            }
        ]
    }
]

PARENT_TO_CHILD = {
    'model': 'tests.models.Employee',
    'data': {
        'name': 'Juan Dela Cruz',
        '!company': {
            'model': 'tests.models.Company',
            'data': {
                'name': 'Juan Company'
            }
        }
    }
}

PARENT_TO_CHILD_WITHOUT_PREFIX_INVALID = {
    'model': 'tests.models.Employee',
    'data': {
        'name': 'Juan Dela Cruz',
        'company': {
            'model': 'tests.models.Company',
            'data': {
                'name': 'Juan Company'
            }
        }
    }
}

PARENT_TO_CHILD_WITHOUT_CHILD_MODEL = {
    'model': 'tests.models.Employee',
    'data': {
        'name': 'Juan Dela Cruz',
        '!company': {
            'data': {
                'name': 'Juan Company'
            }
        }
    }
}

PARENT_TO_CHILDREN = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company',
        '!employees': [
            {
                'model': 'tests.models.Employee',
                'data':
                    {
                        'name': 'John Smith'
                    }
            },
            {
                'model': 'tests.models.Employee',
                'data':
                    {
                        'name': 'Juan Dela Cruz'
                    }
            }

        ]
    }
}

PARENT_TO_CHILDREN_WITHOUT_MODEL = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company',
        '!employees': [
            {
                'data':
                    {
                        'name': 'John Smith'
                    }
            },
            {
                'data':
                    {
                        'name': 'Juan Dela Cruz'
                    }
            }

        ]
    }
}

PARENT_TO_CHILDREN_WITH_MULTI_DATA = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company',
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

PARENT_TO_CHILDREN_WITH_MULTI_DATA_WITHOUT_MODEL = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'My Company',
        '!employees': {
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

instance = {
    'model': 'tests.models.Company',
    'data': {
        'name': 'MyCompany',
        '!employees': {
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

instance = {
    'model': 'tests.models.Company',
    'data': [
        {
            'name': 'MyCompany',
            '!employees': {
                'model': 'tests.models.Employee',
                'data': {
                    'name': 'John Smith'
                }

            }
        },
        {
            'name': 'MySecondCompany'
        },
    ]
}

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

instance = {
    'model': 'tests.models.Employee',
    'data': {
        'name': 'Juan',
        '!company': {
            'model': 'tests.models.Company',
            'data': {
                'Juan\'s Company'
            }
        }
    }
}

instance = [
    {
        "model": "tests.models.Company",
        "data": {
            "name": "Mike Corporation",
            "!employees": {
                "model": "tests.models.Employee",
                "data": {
                }
            }
        }
    },
    {
        "model": "tests.models.Company",
        "data": [
            {

            }
        ]
    },
    {
        "model": "tests.models.Company",
        "data": {

        }
    }
]
