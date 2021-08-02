from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed import HybridSeeder, Seeder
from models import Base

engine = create_engine('sqlite://')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
seeder = Seeder(session)

entities = [
    {
        'model': 'models.Child',
        'data': {
            'age': 5
        }
    },
    {
        'model': 'tests.models.Parent',
        'data': {
            'children': [
                {
                    'model': 'tests.models.Child',
                    'filter': {
                        'age': 5
                    }
                }
            ]
        }
    }

]

seeder.seed(entities)
print(seeder.instances)
