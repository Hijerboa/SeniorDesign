from typing import List
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification

LABELS = [-1, 0, 1]

# Model
MODEL_FILE_PATH = 'app/models/BERT_724'
MODEL = TFBertForSequenceClassification.from_pretrained(MODEL_FILE_PATH, num_labels=3)

# Tokenizer - preprocessing, prepares inputs for the model
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")


def make_prediction(tweet: str):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = MODEL(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    prediction = tf.argmax(tf_predictions, axis=1).numpy()
    polarity = LABELS[prediction[0]]
    conf = tf_predictions[0, prediction[0]].numpy()
    return (polarity, conf)
        

def score_batch(tweets: List[str]):
    scores = []
    for text in tweets:
        scores.append(make_prediction(text))

    return scores
