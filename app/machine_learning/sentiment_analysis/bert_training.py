import os, time
import re
from tkinter import Y
from typing import List
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

class Config:
    def __init__(self, model_file: str, csv_file: str, csv_size: int, dataset_columns: List[str], test_labels: List[int]):
        self.model_file = model_file
        self.csv_file = csv_file
        self.csv_size = csv_size
        self.dataset_columns = dataset_columns
        self.test_labels = test_labels

# Tokenizer - preprocessing, prepares inputs for the model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

DATASET_COLUMNS = ["polarity", "ids", "date", "query", "user", "text"]
# DATASET_COLUMNS = ["polarity", "text"]
DATASET_ENCODING = "ISO-8859-1"
# DATASET_FILENAME = "training.1600000.processed.noemoticon.csv"
# DATASET_FILENAME = "ian.csv"
DATASET_FILENAME = "testdata.manual.2009.06.14.csv"
# TEST_DATASET = "testdata.manual.2009.06.14.csv"
TEST_DATASET = "testdata.manual.2009.06.14.csv"
MODEL_NAME = "TRAINED_MODEL_TEST"
INPUT_FEATURES_LOGGING = True
BATCH_SIZE = 8

# Potential fix if GPU problems, for now seems to work without
# gpus = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpus[0], True)

config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
sess = tf.compat.v1.Session(config=config)

decode_map = {0: 0.5, 2: 1, 4: 1.5}
def decode_sentiment(label):
    return decode_map[int(label)]

def get_csv_as_df(dataset_name: str, columns: List[str]):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    dataset_path = os.path.join(__location__, dataset_name)
    print("Open file:", dataset_path)
    return pd.read_csv(dataset_path, encoding =DATASET_ENCODING , names=columns)

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

def TRAIN(input_config: Config, output_config: Config):
    """
    input_config: pass None if starting from base model, otherwise pass config for model you want to fine tune
    output_config: Pass config for resulting model after training completes
    """

    print('Getting csv in pandas dataframe')
    df = get_csv_as_df(output_config.csv_file, output_config.dataset_columns)
    # remove unnecessary columns / cleanup text / map to our sentiment scores
    data_df = pd.DataFrame({
        'polarity': df['polarity'].apply(lambda x: float(x)+1),
        'text': df['text'].replace(r'\n', '', regex=True)
    })

    # Converting data into proper input format for training the model
    # InputExamples are fed to the tokenizer. 
    input_examples = data_df.apply(lambda x: InputExample(None, text_a=x['text'], text_b=None, label=x['polarity']), axis=1)
    train_input_examples, test_input_examples = train_test_split(input_examples, test_size=0.2)

    # Converting data to TensorFlow dataset objects
    tf_train_dataset = get_tf_dataset(list(train_input_examples))
    tf_test_dataset = get_tf_dataset(list(test_input_examples))

    train_data = tf_train_dataset.shuffle(50).batch(BATCH_SIZE).repeat(2)
    validation_data = tf_test_dataset.shuffle(10).batch(BATCH_SIZE).repeat(2)

    print('TRAINING MODEL')
    if input_config == None:
        print('NO INPUT CONFIG PROVIDED, LOADING BASE MODEL')
        model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased")
    else:
        model = load_model(input_config.model_file)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
    )
    model.fit(train_data, epochs=2, validation_data=validation_data)

    print('SAVING MODEL')
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(location, output_config.model_file)
    model.save_pretrained(path, save_model=True)

### THIS IS FOR TESTING MODEL ###

def load_model(model_file: str):
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    new_model = TFBertForSequenceClassification.from_pretrained(os.path.join(location, model_file))
    new_model.summary()
    return new_model

def make_prediction(model, tweet: str, labels: List[int]):
    tf_batch = tokenizer(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    tf_predictions = np.asarray(tf_predictions).tolist()
    if abs(tf_predictions[0][0] - tf_predictions[0][1]) < 0.00:
        return labels[1]
    elif tf_predictions[0][0] > tf_predictions[0][1]:
        return labels[0]
    else:
        return labels[2]

def test_model(model, config: Config):
    """
    model: object returned from load_model()
    config: Config for the file you are testing
    """
    df = get_csv_as_df(config.csv_file, config.dataset_columns)
    start_time = time.time()
    i = 0
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"running {index}")
        if row['polarity'] == make_prediction(model, row['text'], config.test_labels):
            i += 1
    print(f"TESTING TOOK {(time.time() - start_time) / config.csv_size} per tweet")
    print(f"Accuracy: {i/config.csv_size}")