# %% [markdown]
# ## Install and Import Requirements

# %%
import os, time
from typing import List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import InputExample, InputFeatures

# %% [markdown]
# ## Declare Globals and Configs

# %%
DATASET_ENCODING = "ISO-8859-1"
INPUT_FEATURES_LOGGING = True
BATCH_SIZE = 8
EPOCHS = 1

# Tokenizer - preprocessing, prepares inputs for the model
TOKENIZER = BertTokenizer.from_pretrained("bert-base-uncased")

class Config:
    def __init__(self, model_file: str, csv_file: str, csv_size: int, dataset_columns: List[str], test_labels: List[int], polarity_lambda, reverse_polarity_lambda):
        self.model_file = model_file
        self.csv_file = csv_file
        self.csv_size = csv_size
        self.dataset_columns = dataset_columns
        self.test_labels = test_labels
        self.polarity_lambda = polarity_lambda
        self.reverse_polarity_lambda = reverse_polarity_lambda

preprocessed_1600000_dataset_config = Config(
    "TRAINED_MODEL",
    "../Data/training.1600000.processed.noemoticon.csv",
    1600000,
    ["polarity", "ids", "date", "query", "user", "text"],
    [0, 2, 4],
    lambda x: float(x)/4,
    None
)

vader_dataset_config = Config(
    "TRAINED_MODEL_VADER",
    "../Data/vader_scored_tweets.csv",
    30000,
    ["polarity", "text"],
    None,
    lambda x: (x+1)/2,
    lambda x: x * 2 -1,
)

manual_dataset_config = Config(
    "TRAINED_MODEL_MANUAL",
    "../Data/testdata.manual.2009.06.14.csv",
    500,
    ["polarity", "ids", "date", "query", "user", "text"],
    [0, 2, 4],
    lambda x: float(x)/4,
    None
)

ian_dataset_config = Config(
    "TRAINED_MODEL_IAN",
    "../Data/ian.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: float(x+1)/2,
    None
)

# %% [markdown]
# ## Data Handling Functions

# %%
def get_csv_as_df(dataset_path: str, columns: List[str]):
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
        input_dict = TOKENIZER.encode_plus(
            e.text_a,
            add_special_tokens=True,
            max_length=280,
            return_token_type_ids=True,
            return_attention_mask=True,
            pad_to_max_length=True,
            truncation=True
        )

        input_ids, token_type_ids, attention_mask = (input_dict["input_ids"], input_dict["token_type_ids"], input_dict['attention_mask'])
        features.append(InputFeatures(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids, label=float(e.label)))

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
        output_types=({"input_ids": tf.int32, "attention_mask": tf.int32, "token_type_ids": tf.int32}, tf.float32),
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

# %% [markdown]
# ## Load a Model

# %%
def load_model(model_file: str):
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    new_model = TFBertForSequenceClassification.from_pretrained(os.path.join(location, model_file), num_labels=1)
    new_model.summary()
    return new_model

# %% [markdown]
# ## Model Testing Functions

# %%
def make_prediction_classification(model, tweet: str, config: Config):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_prediction = np.asarray(tf_outputs[0]).tolist()[0][0]
    # prediction = config.reverse_polarity_lambda(tf_prediction)
    prediction = tf_prediction * 2 - 1
    if prediction >= 0.5:
        return config.test_labels[2]
    elif prediction <= -0.5:
        return config.test_labels[0]
    else:
        return config.test_labels[1]


def test_model_classification(model, config: Config):
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
        if row['polarity'] == make_prediction_classification(model, row['text'], config):
            i += 1
    print(f"TESTING TOOK {(time.time() - start_time) / config.csv_size} per tweet")
    print(f"Accuracy: {i/config.csv_size}")
        

def make_prediction_regression(model, tweet: str, config: Config):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_prediction = np.asarray(tf_outputs[0]).tolist()[0][0]
    print(tf_prediction)
    return config.reverse_polarity_lambda(tf_prediction)


def test_model_regression(model, config: Config):
    """
    model: object returned from load_model()
    config: Config for the file you are testing
    """
    df = get_csv_as_df(config.csv_file, config.dataset_columns)
    start_time = time.time()
    sum_abs_error = 0
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"running {index}")
        sum_abs_error += np.abs(row['polarity'] - make_prediction_regression(model, row['text'], config))
    print(f"TESTING TOOK {(time.time() - start_time) / config.csv_size} per tweet")
    print(f"Mean Absolute Error: {sum_abs_error/config.csv_size}")

# %% [markdown]
# ## Train a Model

# %%
def TRAIN(input_config: Config, output_config: Config):
    """
    input_config: pass None if starting from base model, otherwise pass config for model you want to fine tune
    output_config: Pass config for resulting model after training completes
    """

    print('\nLOADING DATA\n')
    df = get_csv_as_df(output_config.csv_file, output_config.dataset_columns)
    # remove unnecessary columns / cleanup text / map to our sentiment scores
    data_df = pd.DataFrame({
        'polarity': df['polarity'].apply(output_config.polarity_lambda),
        'text': df['text'].replace(r'\n', '', regex=True)
    })

    # Converting data into proper input format for training the model
    # InputExamples are fed to the tokenizer. 
    input_examples = data_df.apply(lambda x: InputExample(None, text_a=x['text'], text_b=None, label=x['polarity']), axis=1)
    train_input_examples, validation_input_examples = train_test_split(input_examples, test_size=0.2)

    # Converting data to TensorFlow dataset objects
    ### "get_tf_dataset" IS THE ONLY PART I HAVENT CHECKED. JUST HOPING IT WORKS ###
    tf_train_dataset = get_tf_dataset(list(train_input_examples))
    tf_validation_dataset = get_tf_dataset(list(validation_input_examples))

    # Shuffle Data
    train_data = tf_train_dataset.shuffle(int(output_config.csv_size/10*0.8)).batch(BATCH_SIZE).repeat(2)
    validation_data = tf_validation_dataset.shuffle(int(output_config.csv_size/10*0.2)).batch(BATCH_SIZE).repeat(2)

    print('\nLOADING MODEL\n')
    if input_config == None:
        print('NO INPUT CONFIG PROVIDED, LOADING BASE MODEL')
        model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=1)
    else:
        model = load_model(input_config.model_file)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
        loss=tf.keras.losses.MeanAbsoluteError(), 
        metrics=[tf.keras.metrics.MeanAbsoluteError('average error')]
    )
    
    print('\nTRAINING MODEL\n')
    model.fit(train_data, epochs=EPOCHS, validation_data=validation_data)

    print('\nSAVING MODEL\n')
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(location, output_config.model_file)
    model.save_pretrained(path, save_model=True)

# %% [markdown]
# ## TRAINING

# %%
# TRAIN(None, vader_dataset_config)

# %% [markdown]
# ## EVALUATION

model = load_model(vader_dataset_config.model_file)
test_model_classification(model, manual_dataset_config)
test_model_classification(model, ian_dataset_config)


# %%

