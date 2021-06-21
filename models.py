from sqlalchemy import Integer, Column, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# one-to-one, done
# nested relationship, done
# filter and data, done
# one to many, done
#  many to many, done

player_title_table = Table('player_titles', Base.metadata,
                           Column('player_id', Integer, ForeignKey('players.id')),
                           Column('titles_id', Integer, ForeignKey('titles.id'))
                           )


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    titles = relationship('Title', back_populates='players', secondary=player_title_table)

    def __repr__(self):
        return f"<Player(name='{self.name}')>"


class Title(Base):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    players = relationship('Player', back_populates='titles', secondary=player_title_table)

    def __repr__(self):
        return f"<Title(name='{self.name}')>"


class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __repr__(self):
        return "<Location(name='%s')>" % (
            self.name
        )
