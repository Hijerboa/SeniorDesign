def insert_tweets(tweets, connection):
    collection = connection.biden_tweets
    collection.insert_many(tweets)
