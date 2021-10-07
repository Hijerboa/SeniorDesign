from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, UniqueConstraint, LargeBinary, \
    Table, DateTime, Date
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
    reply = Column(Boolean, default=False, nullable=False)
    reply_to_id = Column(String(length=32), nullable=True, default=None)
    retweets = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)
    replies = Column(Integer, nullable=False)
    quote_count = Column(Integer, nullable=False)
    search_phrases = relationship(SearchPhrase, secondary=tweet_to_search)


class TwitterUser(Base):
    __tablename__ = 'twitter_users'

    id = Column(String(length=32), unique=True, nullable=False, primary_key=True)
    display_name = Column(String(length=128), nullable=False)
    followers_count = Column(Integer(), nullable=False)
    following_count = Column(Integer(), nullable=False)
    tweet_count = Column(Integer(), nullable=False)
    listed_count = Column(Integer(), nullable=False)
    url = Column(String(length=256), nullable=True)
    protected = Column(Boolean, nullable=False, default=False)
    verified = Column(Boolean, nullable=False, default=False)
    description = Column(String(length=1024), nullable=True)
    inserted = Column(DateTime, name='inserted_time', default=datetime.datetime.utcnow(), nullable=False)
    created_at = Column(DateTime, name='account_created', nullable=False)
    profile_image_url = Column(String(length=256), nullable=True)
    username = Column(String(length=128), nullable=False)
    location = Column(String(length=512), nullable=True)


class CongressMemberData(Base, PrimaryKeyBase):
    __tablename__ = 'congress_member_data'

    propublica_id = Column(String(length=32), unique=True, nullable=False)
    first_name = Column(String(length=32), nullable=False)
    middle_name = Column(String(length=64), nullable=True)
    last_name = Column(String(length=64), nullable=False)
    suffix = Column(String(length=16), nullable=True, default=None)
    date_of_birth = Column(String(length=32))
    gender = Column(String(length=2), nullable=True)
    party = Column(String(length = 32), nullable=True)
    twitter_account = Column(String(length=128), nullable=True)
    facebook_account = Column(String(length=128), nullable=True)
    youtube_account = Column(String(length=128), nullable=True)
    govtrack_id  = Column(Integer(), nullable=True)
    cspan_id = Column(Integer(), nullable=True)
    votesmart_id = Column(Integer(), nullable=True)
    icpsr_id = Column(Integer(), nullable=True)
    crp_id = Column(String(length=32))
    google_entity_id = Column(String(length=64))
    fec_canidate_id = Column(String(length=32))
    inserted = Column(DateTime, name='inserted_time', default=datetime.datetime.utcnow(), nullable=False)


class CongressMemberInstance(Base, PrimaryKeyBase):
    __tablename__ = 'congress_member_instance'

    congress_member_id = Column(Integer(), ForeignKey('congress_member_data.id'))
    congress = Column(Integer(), nullable=False)
    chamber = Column(String(length=16), nullable=False)
    title = Column(String(length=64), nullable=True)
    short_title = Column(String(length=16), nullable=True)
    leadership_role = Column(String(length=64), nullable=True)
    seniority = Column(String(length=8), nullable=True)
    next_election = Column(String(length=8), nullable=True)
    total_votes = Column(Integer())
    missed_votes = Column(Integer())
    total_present = Column(Integer())
    senate_class = Column(String(length=16), nullable=True)
    senate_rank = Column(String(length=16), nullable=True)
    missed_votes_pct = Column(Float())
    votes_with_party_pct = Column(Float())
    votes_against_party_pct = Column(Float())
    inserted = Column(DateTime, name='inserted_time', default=datetime.datetime.utcnow(), nullable=False)


class User(PrimaryKeyBase, Base):
    __tablename__ = 'users'

    name = Column(String(length=64), name='username', nullable=False, unique=True)
    email = Column(String(length=64), name='user_email', nullable=False, unique=True)
    key_hash = Column(String(length=256), name='user_key_hash', nullable=False, unique=True)
    creation = Column(DateTime, name='creation_time', default=datetime.datetime.utcnow(), nullable=False)
    updated = Column(DateTime, name='updated_time', default=datetime.datetime.utcnow(), nullable=False)
    role = Column(String(length=32), name='role', nullable=False)