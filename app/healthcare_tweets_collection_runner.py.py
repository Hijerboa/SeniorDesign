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

group = session.query(SearchPhrase).filter(SearchPhrase.id.in_([47, 65, 76, 79, 107, 113, 114, 115, 116, 119])).limit(11000).all()
for phrase in group:
    tweets = session.query(Tweet).where(Tweet.search_phrases.contains(phrase)).limit(2000).all()
    for tweet in tweets:
        all_tweets.append(tweet)

random.shuffle(all_tweets)
print(len(all_tweets))

man_tweets = all_tweets[:1000]
vader_tweets = all_tweets[1000:11000]

# Write to man CSV here
man_f = open('healthcare_tweets.csv', 'w')
for t in man_tweets:
    tweet = str(t).replace(',', '').replace(';', '').replace('\n', '')
    man_f.write(f'{tweet}\n')
man_f.close()

# Write to vader CSV here
vader_f = open('healthcare_tweets_vader_score.csv', 'w')
for t in vader_tweets:
    tweet = str(t).replace(',', '').replace(';', '').replace('\n', '')
    score = vader_score(tweet)
    vader_f.write(f'{score}, {tweet}\n')
vader_f.close()

session.close()