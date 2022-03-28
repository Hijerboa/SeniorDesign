# Imports here

CONF_THRESHOLD = 0


def get_average(bill_id: str):
    # Get all tweets iterable
    # TEMP STAND IN
    iterable_tweets = []

    count = 0
    sum = 0
    for tweet in iterable_tweets:
        if tweet.confidence > CONF_THRESHOLD:
            count += 1
            sum += tweet.score
    
    return sum/count