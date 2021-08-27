import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from sqlalchemyseed.loader import load_entities_from_csv
from tests.models import Company, Base, Employee
from sqlalchemy.orm import object_mapper, class_mapper
from sqlalchemy import inspect

engine = create_engine('sqlite://')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# theory 1, string foreign key query, denied
# theory 2, query using column instance, accepted


with Session(autoflush=True) as session:
    session: sqlalchemy.orm.Session = session
    # session.autoflush = True

    company = Company(name='MyCompany')
    session.add(company)
    # session.
    kwargs = {'name': 'MyCompany'}
    foreign_key_column = (list(Employee.company_id.foreign_keys)[0]).column
    from sqlalchemy import Column
    print(type(foreign_key_column), type(Column))

    print(session.query(foreign_key_column).filter_by(name='MyCompany').one())

# print(class_mapper(Company).c)
#
# for cc in class_mapper(Company).c:
#     print(vars(cc))
