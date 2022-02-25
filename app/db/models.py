from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, UniqueConstraint, LargeBinary, \
    Table, DateTime, Date, Text, Enum, null, JSON
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relation, relationship
import datetime
import enum

Base = declarative_base()

class phrase_types(enum.Enum):
    title = 1
    summary = 2
    manual = 3
    

class twitter_api_token_type(enum.Enum):
    archive = 1
    non_archive = 2
    
class PrimaryKeyBase:
    id = Column(Integer, primary_key=True, autoincrement=True)


tweet_to_search = Table(
    'tweet_to_search', Base.metadata,
    Column('tweet_id', ForeignKey('tweets.id')),
    Column('phrase_id', ForeignKey('search_phrases.id'))
)

bill_to_search = Table(
    'bill_to_search', Base.metadata,
    Column('bill_id', ForeignKey('bills.bill_id')),
    Column('phrase_id', ForeignKey('search_phrases.id'))
)

bill_to_committee_code = Table(
    'bill_to_committee_code', Base.metadata,
    Column('bill_id', ForeignKey('bills.bill_id')),
    Column('committee_code', ForeignKey('committee_codes.id'))
)

bill_to_subcommittee_code = Table(
    'bill_to_subcommittee_code', Base.metadata,
    Column('bill_id', ForeignKey('bills.bill_id')),
    Column('subcommittee_code', ForeignKey('subcommittee_codes.id'))
)

bill_to_subject = Table(
    'bill_to_subject', Base.metadata,
    Column('bill_id', ForeignKey('bills.bill_id')),
    Column('subject', ForeignKey('bill_subjects.id'))
)


class SearchPhrase(PrimaryKeyBase, Base):
    __tablename__ = 'search_phrases'

    search_phrase = Column(String(length=128), nullable=False)
    type = Column(Enum(phrase_types), nullable=True, default=phrase_types.manual)

    def __repr__(self):
        return f'{self.search_phrase} (TYPE: {self.type})'


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
    seniment= Column(Float, nullable=True)
    search_phrases = relationship(SearchPhrase, secondary=tweet_to_search)

    def __repr__(self):
        return f'{self.text[:50]}'


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

    def __repr__(self):
        return f'{self.display_name} (ID: {self.id})'


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

    def __repr__(self):
        name = [self.first_name]
        if not self.middle_name is None:
            name.append(self.middle_name)
        name.append(self.last_name)
        if not self.suffix is None:
            name.append(self.suffix)
        return ' '.join(name)


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

    def __repr__(self):
        return f'{self.title}'


class CommitteeCodes(PrimaryKeyBase, Base):
    __tablename__ = 'committee_codes'

    committee_code = Column(String(length=32))

    def __repr__(self):
        return f'Code: {self.committee_code}'


class SubcommitteeCodes(PrimaryKeyBase, Base):
    __tablename__ = 'subcommittee_codes'

    subcommittee_code = Column(String(length=32))

    def __repr__(self):
        return f'Code: {self.subcommittee_code}'

class BillSubject(PrimaryKeyBase, Base):
    __tablename__ = 'bill_subjects'

    name = Column(String(length=128))
    url_name = Column(String(length=128))

    def __repr__(self):
        return f'Subject: {self.name}'


class Bill(Base):
    __tablename__ = 'bills'

    bill_id = Column(String(length=16), unique=True, primary_key=True, nullable=False)
    congress = Column(Integer(), nullable=False)
    bill_slug = Column(String(length=16), nullable=False)
    bill_type = Column(String(length=8))
    number = Column(String(length=16))
    title = Column(String(length=2048))
    short_title = Column(String(length=1024))
    sponsor_id = Column(String(length=16))
    sponsor_party = Column(String(length=16))
    gpo_pdf_uri = Column(String(length=1024))
    congressdotgov_url = Column(String(length=1024))
    govtrack_url = Column(String(length=1024))
    introduced_date = Column(Date)
    active = Column(Boolean())
    last_vote = Column(Date)
    house_passage = Column(Date)
    senate_passage = Column(Date)
    enacted = Column(Date)
    vetoed = Column(Date)
    cosponsors = Column(Integer())
    dem_cosponsors = Column(Integer())
    rep_cosponsors = Column(Integer())
    committees = Column(String(length=128))
    primary_subject = Column(String(length=1024))
    summary = Column(Text(16000000))
    summary_short = Column(String(length=4096))
    latest_major_action_date = Column(Date)
    latest_major_action = Column(String(length=2048))
    committee_codes = relationship(CommitteeCodes, secondary=bill_to_committee_code)
    sub_committee_codes = relationship(SubcommitteeCodes, secondary=bill_to_subcommittee_code)
    subjects = relationship(BillSubject, secondary=bill_to_subject)
    inserted = Column(DateTime, name='inserted_time', default=datetime.datetime.utcnow(), nullable=False)
    sentiment = Column(Float(), nullable=True)
    actions = relationship('BillAction', backref='bill_object')
    versions = relationship('BillVersion', backref='bill_object')
    keywords = relationship(SearchPhrase, secondary=bill_to_search)

    def __repr__(self):
        return f'{self.title} ({self.bill_slug})'

class User(PrimaryKeyBase, Base):
    __tablename__ = 'users'

    name = Column(String(length=64), name='username', nullable=False, unique=True)
    email = Column(String(length=64), name='user_email', nullable=False, unique=True)
    key_hash = Column(String(length=256), name='user_key_hash', nullable=False, unique=True)
    creation = Column(DateTime, name='creation_time', default=datetime.datetime.utcnow(), nullable=False)
    updated = Column(DateTime, name='updated_time', default=datetime.datetime.utcnow(), nullable=False)
    role = Column(String(length=32), name='role', nullable=False)

    def __repr__(self):
        return f'name: {self.name}\trole: {self.role}'
    
    
class TaskError(PrimaryKeyBase, Base):
    __tablename__ = 'task_errors'
    
    description = Column(String(length=4096), nullable=False)
    creation = Column(DateTime, name='creation_time', default=datetime.datetime.utcnow(), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    task = relationship('Task', backref='errors')

class Task(PrimaryKeyBase, Base):
    __tablename__ = 'tasks'
    
    complete = Column(Boolean, default=False, nullable=False)
    error = Column(Boolean, default=False, nullable=False)
    creation = Column(DateTime, name='creation_time', default=datetime.datetime.utcnow(), nullable=False)
    launched_by_id = Column(Integer, ForeignKey('users.id'))
    launched_by = relationship(User, backref='tasks')
    type = Column(String(length=256))
    parameters = Column(JSON)


class BillAction(PrimaryKeyBase, Base):
    __tablename__ = 'bill_actions'

    bill = Column(String(length=16), ForeignKey('bills.bill_id'))
    order = Column(Integer)
    chamber = Column(String(length=16))
    action_type = Column(String(length=256))
    datetime = Column(DateTime, nullable=False)
    description = Column(String(length=4096))

    def __repr__(self):
        return f'id: {self.bill})\tdate: {self.datetime}\tdesc: {self.description[:50]}'


class BillVersion(PrimaryKeyBase, Base):
    __tablename__ = 'bill_verions'

    bill = Column(String(length=16), ForeignKey('bills.bill_id'))
    status = Column(String(length=64))
    title = Column(String(length=8))
    url = Column(String(length=512))
    congressdotgov_url = Column(String(length=512), nullable=True)
    full_text = Column(LONGTEXT())

    def __repr__(self):
        return f'{self.title} (id: {self.bill})\tstatus: {self.status}'


class KeyRateLimit(PrimaryKeyBase, Base):
    __tablename__ = 'key_rate_limit'
    
    last_query = Column(DateTime(), nullable=False, default=datetime.datetime.utcnow(),)
    type = Column(Enum(twitter_api_token_type), nullable=False)
    tweets_pulled = Column(Integer(), nullable=False, default=0)
    locked = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'key id: {self.id}\tkey type: {self.type}\tlast query: {self.last_query}\ttotal usage: {self.tweets_pulled}\tLocked: {self.locked}'



class SearchPhraseDates(PrimaryKeyBase, Base):
    __tablename__ = 'search_phrase_date'
    
    search_phrase_id = Column(ForeignKey(SearchPhrase.id))
    search_phrase = relationship(SearchPhrase)
    start_date = Column(DateTime(), nullable=False)
    end_date = Column(DateTime(), nullable=False)

    def __repr__(self):
        return f'phrase id: {self.search_phrase_id}\tphrase: {self.search_phrase}\trange: {self.start_date}-{self.end_date}'
