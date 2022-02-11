from util import cred_handler
from db.models import KeyRateLimit, Tweet, SearchPhrase, TwitterUser, Bill, CommitteeCodes, SubcommitteeCodes, Task, twitter_api_token_type
from db.database_connection import create_session, initialize

def update_key_refs():
    session = create_session()
    i = 0
    while True:
        try:
            i += 1
            #verify that key exists in cred.json
            cred_handler.get_secret(f'twitter_bearer_token_{i}')
            print(f'found secret for token {i}')
        except KeyError:
            print('key not found in cred.')
            exit()
        print(f'Checking key {i}')
        key = session.query(KeyRateLimit).where(KeyRateLimit.id == i).limit(1).all()
        print(key)
        if len(key) == 0:
            #key does not exist, create one
            print('adding key')
            new_key = KeyRateLimit(type = twitter_api_token_type.archive, id = i)
            print('created key')
            session.add(new_key)
            print('inserted')
            session.commit()
            print(f'commited key {i}')
        else:
            print('key already in db.')
        print('next key')

    
    