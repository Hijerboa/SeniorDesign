from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from sqlalchemy.sql.expression import func
from db.database_connection import initialize, create_session
from db.models import Tweet
from datetime import datetime
from emoji import UNICODE_EMOJI

stopwords = ['', 'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

# Load VADER sentiment analyzer
sia_obj = SentimentIntensityAnalyzer()

# Load spaCy objects
spacy_tokenizer = spacy.load("en_core_web_sm")

def vader_score(tweet_text: str):
    # Get raw VADER score
    sentiment_dict = sia_obj.polarity_scores(tweet_text)

    # Tokenize text
    tokens = spacy_tokenizer(tweet_text)
    # Remove stopwords
    # Lemmatize
    # POS tagging
    # Get emojis/hashtags/adjectives(?)
    # VADER score selected/important tokens
    # Weighted average of scores

    return sentiment_dict

    
def test_sentiment_analysis():
    initialize()
    session = create_session()
    num_tests = 1
    tweets = session.query(Tweet).limit(num_tests).all()
    start = datetime.now()
    sentiments = [vader_score(t.text) for t in tweets]
    text = [t.text for t in tweets]
    end = datetime.now()
    delta = end - start
    for i in range(num_tests):
        print(f'SCORE: {sentiments[i]}')
        print(f'TEXT: {text[i]}\n')
    print(f'Took {delta.seconds} seconds')