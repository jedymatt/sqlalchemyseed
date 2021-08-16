from sqlalchemyseed.loader import load_entities_from_csv
from tests.models import Company

company_filepath = './res/companies.csv'

if __name__ == '__main__':
    entities = load_entities_from_csv(company_filepath, Company)
    print(entities)
