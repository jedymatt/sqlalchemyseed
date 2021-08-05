from sqlalchemyseed import validator
import models

obj = [
    {
        'model': 'models.Company',
        'data': {
            'name': 'Mike Incorporated',
            'employees': [
                {
                    'model': 'models.Employee',
                    'data': {
                        'name': 'Juan Dela Cruz'
                    }
                }
            ]
        }
    }
]

tree = validator.__Tree(obj)

tree.walk()

print(tree.obj)

# print(models.Company().employees.property.uselist)
nike = models.Company(name='Nike')
