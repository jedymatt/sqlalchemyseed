from sqlalchemyseed.loader import load_entities_from_csv
from tests.models import Company, Base
from sqlalchemy.orm import object_mapper
from sqlalchemy import inspect

company_filepath = './res/companies.csv'

if __name__ == '__main__':
    company = Company()
    print(vars(list(Company().__class__.registry.mappers)[0]))
    # print(list(type(company).registry.mappers))

