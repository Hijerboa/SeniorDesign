from typing import List, Tuple
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from db.models import Tweet

LABELS = [-1, 0, 1]

# Model
MODEL_FILE_PATH = 'models/BERT_724'
MODEL = TFBertForSequenceClassification.from_pretrained(
    MODEL_FILE_PATH, num_labels=3
)

# Tokenizer - preprocessing, prepares inputs for the model
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")


def make_prediction(tweet: str):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True,
                         truncation=True, return_tensors='tf')
    tf_outputs = MODEL(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    prediction = tf.argmax(tf_predictions, axis=1).numpy()
    polarity = LABELS[prediction[0]]
    conf = tf_predictions[0, prediction[0]].numpy()
    return (polarity, conf)


# Takes a list of tweets and returns a list of tuples containing (tweet_id, tweet_text, polarity, confidence)
def score_batch(tweets: Tuple[str, str]):
    """Returns a list of tweets and their confidence/sentiments

    Args:
        tweets (Tuple[id, text]): List of tuples

    Returns:
        _type_: [Tuple(id, polarity, confidence)]
    """
    return [(t[0],)+ make_prediction(t[1]) for t in tweets]
