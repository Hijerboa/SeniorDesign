import os, time
import re
from tkinter import Y
import numpy as np
import pandas as pd
from torch import cuda
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
import csv
from sklearn import metrics
import logging
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import InputExample, InputFeatures

# SequenceClassification - BERT with extra layers at the end for sentiment scoring
model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")
tf.debugging.set_log_device_placement(True)
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
# Tokenizer - preprocessing, prepares inputs for the model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

DATASET_COLUMNS = ["polarity", "ids", "date", "query", "user", "text"]
DATASET_ENCODING = "ISO-8859-1"
# DATASET_FILENAME = "training.1600000.processed.noemoticon.csv"
DATASET_FILENAME = "poop2.csv"
VALIDATE_DATASET = "testdata.manual.2009.06.14.csv"
INPUT_FEATURES_LOGGING = True
BATCH_SIZE = 8

# gpus = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpus[0], True)

config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
sess = tf.compat.v1.Session(config=config)

decode_map = {0: 0.5, 2: 1, 4: 1.5}
def decode_sentiment(label):
    return decode_map[int(label)]

def get_csv_as_df(dataset_name):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    dataset_path = os.path.join(__location__, dataset_name)
    print("Open file:", dataset_path)
    return pd.read_csv(dataset_path, encoding =DATASET_ENCODING , names=DATASET_COLUMNS)

def get_tf_dataset(input_examples):
    """
    Converts a dataframe of Input Examples
    :return: dataset (tensorflow object) of tensors
    """
    # What we are inputing into the vector
    features = []
    i = 0
    for e in list(input_examples):
        i += 1
        if i % 10000 == 0 and INPUT_FEATURES_LOGGING:
            print(f'{i} | {e}')
        input_dict = tokenizer.encode_plus(
            e.text_a,
            add_special_tokens=True,
            max_length=280,
            return_token_type_ids=True,
            return_attention_mask=True,
            pad_to_max_length=True,
            truncation=True
        )

        input_ids, token_type_ids, attention_mask = (input_dict["input_ids"], input_dict["token_type_ids"], input_dict['attention_mask'])
        features.append(InputFeatures(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, label=e.label))

    def gen():
        for f in features:
            yield (
                {
                    "input_ids": f.input_ids,
                    "attention_mask": f.attention_mask,
                    "token_type_ids": f.token_type_ids,
                },
                f.label,
            )

    tf_dataset = tf.data.Dataset.from_generator(
        generator=gen,
        output_types=({"input_ids": tf.int32, "attention_mask": tf.int32, "token_type_ids": tf.int32}, tf.int64),
        output_shapes=(
            {
                "input_ids": tf.TensorShape([None]),
                "attention_mask": tf.TensorShape([None]),
                "token_type_ids": tf.TensorShape([None]),
            },
            tf.TensorShape([]),
        ),
    )
    return tf_dataset

def TRAIN():

    df = get_csv_as_df(DATASET_FILENAME)

    # remove unnecessary columns / cleanup text / map to our sentiment scores
    data_df = pd.DataFrame({
        'label': df['polarity'].apply(lambda x: decode_sentiment(x)),
        'text': df['text'].replace(r'\n', '', regex=True)
    })
    print("HEAD\n")
    print(data_df.head())

    # InputExamples are fed to the tokenizer. 
    input_examples = data_df.apply(lambda x: InputExample(None, text_a=x['text'], text_b=None, label=x['label']), axis=1)
    train_input_examples, test_input_examples = train_test_split(input_examples, test_size=0.2)
    print("TRAIN INPUT EXAMPLES")
    print(train_input_examples)
    print("TRAIN INPUT EXAMPLES")
    print(test_input_examples)

    tf_train_dataset = get_tf_dataset(list(train_input_examples))
    tf_test_dataset = get_tf_dataset(list(test_input_examples))
    print("TF TRAIN DATA")
    print(tf_train_dataset)
    print("TF TEST DATA")
    print(tf_test_dataset)

    train_data = tf_train_dataset.shuffle(100).batch(BATCH_SIZE).repeat(2)
    test_data = tf_test_dataset.batch(BATCH_SIZE)
    print("TRAIN DATA\n")
    print(train_data)
    print("TEST DATA\n")
    print(test_data)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
    )
    
    model.fit(train_data, epochs=2, validation_data=test_data)

    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(location, 'TRAINED_MODEL')
    model.save_pretrained(path, save_model=True)

def load_model():
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    new_model = TFBertForSequenceClassification.from_pretrained(os.path.join(location, 'TRAINED_MODEL'))
    new_model.summary()
    return new_model

def make_prediction(model, tweet: str):
    tf_batch = tokenizer(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    labels = [0, 4]
    label = tf.argmax(tf_predictions, axis=1)
    label = label.numpy()
    return labels[label[0]]

# def test_model(model):
#     df = get_csv_as_df(VALIDATE_DATASET)
#     data_df = pd.DataFrame({
#         'label': df['polarity'].apply(lambda x: decode_sentiment(x)),
#         'text': df['text'].replace(r'\n', '', regex=True)
#     })

#     input_examples = data_df.apply(lambda x: InputExample(None, text_a=x['text'], text_b=None, label=x['label']), axis=1)
#     tf_dataset = get_tf_dataset(list(input_examples))

#     # y = data_df.apply(lambda z: z['label'], axis=1)
#     # # y = tf.convert_to_tensor(list(y))
#     model.compile(
#         optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
#         loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
#         metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
#     )

#     loss, acc = model.evaluate(tf_dataset)
#     print(f"Loss: {loss} | Accuracy: {acc}")

def test_model(model):
    df = get_csv_as_df(VALIDATE_DATASET)
    start_time = time.time()
    output_values = set()
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"running {index}")
        output_values.add(make_prediction(model, row['text']))
    print(f"TESTING TOOK {(time.time() - start_time) / 500} per tweet")
    print(output_values)