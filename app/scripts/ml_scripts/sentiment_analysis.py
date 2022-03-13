import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification


# Tokenizer - preprocessing, prepares inputs for the model
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")

MODE_WEIGHTS_PATH = ''
MODEL = TFBertForSequenceClassification.from_pretrained(MODE_WEIGHTS_PATH, num_labels=3)

LABELS = [-1, 0, 1]


def predict_sentiment(tweet: str):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = MODEL(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    prediction = tf.argmax(tf_predictions, axis=1).numpy()
    return LABELS[prediction[0]]