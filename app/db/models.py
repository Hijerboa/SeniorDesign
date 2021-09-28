from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, UniqueConstraint, LargeBinary, \
    Table, DateTime
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class PrimaryKeyBase:
    id = Column(Integer, primary_key=True, autoincrement=True)


tweet_to_search = Table(
    'tweet_to_search', Base.metadata,
    Column('tweet_id', ForeignKey('tweets.id')),
    Column('phrase_id', ForeignKey('search_phrases.id'))
)

class SearchPhrase(PrimaryKeyBase, Base):
    __tablename__ = 'search_phrases'

    search_phrase = Column(String(length=64), nullable=False)


# Tweet class does not have it's own ID field. Instead the twitter ID is used as the primary key
class Tweet(Base):
    __tablename__ = 'tweets'

    id = Column(String(length=32), unique=True, nullable=False, primary_key=True)
    author_id = Column(String(length=32), nullable=False)
    inserted = Column(DateTime, name='inserted_time', default=datetime.datetime.utcnow(), nullable=False)
    created_at = Column(DateTime, name='time_tweeted', nullable=False)
    text = Column(String(length=1024), nullable=False)
    source = Column(String(length=64), nullable=True)
    lang = Column(String(length=8), nullable=True)
    retweet = Column(Boolean, default=False, nullable=False)
    retweet_original_id = Column(String(length=32), nullable=True, default=None)
    reply = Column(Boolean, default=False, nullable=False)
    reply_to_id = Column(String(length=32), nullable=True, default=None)
    search_phrases = relationship(SearchPhrase, secondary=tweet_to_search)


class User(PrimaryKeyBase, Base):
    __tablename__ = 'users'

    name = Column(String(length=64), name='username', nullable=False, unique=True)
    email = Column(String(length=64), name='user_email', nullable=False, unique=True)
    key_hash = Column(String(length=256), name='user_key_hash', nullable=False, unique=True)
    creation = Column(DateTime, name='creation_time', default=datetime.datetime.utcnow(), nullable=False)
    updated = Column(DateTime, name='updated_time', default=datetime.datetime.utcnow(), nullable=False)
    role = Column(String(length=32), name='role', nullable=False)