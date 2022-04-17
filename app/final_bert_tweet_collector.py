import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from db.database_connection import initialize, create_session
from db.models import Bill, SearchPhrase, Tweet

sia_obj = SentimentIntensityAnalyzer()

def vader_score(tweet_text: str):
    score_dict = sia_obj.polarity_scores(tweet_text)
    comp_val = score_dict['compound']

    if comp_val <= -0.35:
        return -1
    elif comp_val >= 0.35:
        return 1
    else:
        return 0


initialize()
session = create_session()

all_tweets = []


total_count = 0
bill = session.query(Bill).filter(Bill.bill_id=='hr1-117').first()
for phrase in bill.keywords:
    print(phrase.id)
    tweets = session.query(Tweet).where(Tweet.search_phrases.contains(phrase)).count()
    total_count += tweets


random.shuffle(all_tweets)
print(len(all_tweets))

# Write to vader CSV here
vader_f = open('final_tweets.csv', 'w')
for t in all_tweets:
    tweet = str(t).replace(',', '').replace(';', '').replace('\n', '')
    score = vader_score(tweet)
    vader_f.write(f'{score}, {tweet}\n')
vader_f.close()

session.close()