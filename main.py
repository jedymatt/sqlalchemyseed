from db import engine, session
from models import Base, Player
from sqlalchemyseed import load_entities_from_json, create_objects

Base.metadata.create_all(engine)

data = load_entities_from_json('temp.json')

objects = create_objects(session, data)

# session.add_all(objects)
# session.commit()

result = session.query(Player).all()

print(result)
for res in result:
    print(res, res.titles)
