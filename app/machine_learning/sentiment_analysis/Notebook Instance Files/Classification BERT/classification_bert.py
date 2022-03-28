# %% [markdown]
# ## Install and Import Requirements

# %%
import os, time
from re import I
from typing import List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import clone_model
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import InputExample, InputFeatures
import copy

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
    def __init__(self, model_file: str, csv_file: str, csv_size: int, dataset_columns: List[str], test_labels: List[int], polarity_lambda):
        self.model_file = model_file
        self.csv_file = csv_file
        self.csv_size = csv_size
        self.dataset_columns = dataset_columns
        self.test_labels = test_labels
        self.polarity_lambda = polarity_lambda

temp_config = Config(
    "TRAINED_MODEL_IAN_1_EPOCHS",
    "ian.csv",
    250,
    ["polarity", "ids", "date", "query", "user", "text"],
    [0, 2, 4],
    lambda x: int(x/2)
)

preprocessed_1600000_dataset_config = Config(
    "TRAINED_MODEL",
    "../Data/training.1600000.processed.noemoticon.csv",
    1600000,
    ["polarity", "ids", "date", "query", "user", "text"],
    [0, 2, 4],
    lambda x: int(x/2)
)

one_million_model = Config(
    "TRAINED_MODEL_1000000_4",
    "../Data/new_100000_4_threshold.csv",
    100000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x + 1
)

one_million_model_5 = Config(
    "TRAINED_MODEL_1000000_5",
    "../Data/new_100000_5_threshold.csv",
    100000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x + 1
)

one_million_model_6 = Config(
    "TRAINED_MODEL_1000000_6",
    "../Data/new_100000_6_threshold.csv",
    100000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x + 1
)

one_million_model_7 = Config(
    "TRAINED_MODEL_1000000_7",
    "../Data/new_100000_7_threshold.csv",
    100000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x + 1
)

vader_maxval_dataset_config = Config(
    "TRAINED_MODEL_VADER_MAXVAL",
    "../Data/classified_vader_scored_tweets_max_val.csv",
    30000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)


vader_compval_dataset_config = Config(
    "TRAINED_MODEL_VADER_COMPVAL",
    "../Data/classified_vader_scored_tweets_compound_val.csv",
    30000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

tdm_dataset_config = Config(
    "TRAINED_MODEL_MANUAL",
    "../Data/testdata.manual.2009.06.14.csv",
    500,
    ["polarity", "ids", "date", "query", "user", "text"],
    [0, 2, 4],
    lambda x: int(x/2)
)

ian_dataset_config = Config(
    "TRAINED_MODEL_IAN",
    "../Data/ian.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

ian2_dataset_config = Config(
    "TRAINED_MODEL_IAN2",
    "../Data/ian2.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

aidan_dataset_config = Config(
    "TRAINED_MODEL_AIDAN",
    "../Data/aidan.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

nathan_dataset_config = Config(
    "TRAINED_MODEL_NATHAN",
    "../Data/nathan.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

nick_dataset_config = Config(
    "TRAINED_MODEL_NICK",
    "../Data/nick.csv",
    250,
    ["text", "polarity"],
    [-1, 0, 1],
    lambda x: x+1
)

shuffled_model = Config(
    "TRAINED_MODEL_SHUFFLED_4",
    f"../Data/shuffled_train_data_A.csv",
    1000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

shuffled_version = 'B' # 'A' || 'B' || 'C'

shuffled_train_config = Config(
    "TRAINED_MODEL_SHUFFLED",
    f"../Data/shuffled_train_data_{shuffled_version}.csv",
    1000,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
)

shuffled_test_config = Config(
    "TEST_MODEL_SHUFFLED",
    f"../Data/shuffled_test_data_{shuffled_version}.csv",
    250,
    ["polarity", "text"],
    [-1, 0, 1],
    lambda x: x+1
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

# %% [markdown]
# ## Load a Model

# %%
def load_model(model_file: str):
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    new_model = TFBertForSequenceClassification.from_pretrained(os.path.join(location, model_file), num_labels=3)
    new_model.summary()
    return new_model

# %% [markdown]
# ## Model Testing Functions

# %%
def make_prediction(model, tweet: str, labels: List[int]):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    prediction = tf.argmax(tf_predictions, axis=1).numpy()
    return labels[prediction[0]]
        

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
    accuracy_score = i/config.csv_size
    print(f"Accuracy: {accuracy_score}")
    return accuracy_score


def make_prediction_confidence(model, tweet: str, labels: List[int]):
    tf_batch = TOKENIZER(tweet, max_length=128, padding=True, truncation=True, return_tensors='tf')
    tf_outputs = model(tf_batch)
    tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
    prediction = tf.argmax(tf_predictions, axis=1).numpy()
    conf = tf_predictions[0, prediction[0]].numpy()
    if conf > 0.99:
        return labels[prediction[0]]
    else:
        return None
        

def test_model_confidence(model, config: Config):
    """
    model: object returned from load_model()
    config: Config for the file you are testing
    """
    df = get_csv_as_df(config.csv_file, config.dataset_columns)
    start_time = time.time()
    count = 0
    i = 0
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"running {index}")
        pred = make_prediction_confidence(model, row['text'], config.test_labels)
        if (pred != None):
            count += 1
            if (row['polarity'] == pred):
               i += 1
    print(f"TESTING TOOK {(time.time() - start_time) / config.csv_size} per tweet")
    accuracy_score = i/count
    print(f'Scored: {count}')
    print(f'Unscored: {config.csv_size-count}')
    print(f"Accuracy: {accuracy_score}")
    return accuracy_score
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
        model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=3)
    else:
        model = load_model(input_config.model_file)
        
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
    )
    
    print('\nTRAINING MODEL\n')
    model.fit(train_data, epochs=EPOCHS, validation_data=validation_data)

    print('\nSAVING MODEL\n')
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    path = os.path.join(location, output_config.model_file)
    model.save_pretrained(path, save_model=True)


def TRAIN_NO_SAVE(model, output_config: Config):
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
        
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5, epsilon=1e-08, clipnorm=1.0), 
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy('accuracy')]
    )
    
    print('\nTRAINING MODEL\n')
    model.fit(train_data, epochs=EPOCHS, validation_data=validation_data)

    return model

# %% [markdown]
# ## TRAINING

# %% [markdown]
# ## EVALUATION
model = load_model(shuffled_model.model_file)
# test_model(model, shuffled_test_config)
test_model_confidence(model, shuffled_test_config)
# test_model(model, ian_dataset_config)
# test_model(model, aidan_dataset_config)
# test_model(model, nick_dataset_config)
# test_model(model, nathan_dataset_config)
# test_model(model, tdm_dataset_config)
# %%
'''
csv_configs = {ian_dataset_config, aidan_dataset_config, nick_dataset_config, nathan_dataset_config}

def recursive_fine_tuning(count: int, training_sequence: List[Config], model):

    train_seq = copy.deepcopy(training_sequence)
    remaining = csv_configs - set(train_seq)

    # Test current model
    outfile = open('recursive_ft_results.txt', 'a')
    outfile.write(f'{train_seq}\n')
    for conf in remaining:
        outfile.write(f'*\t{conf.csv_file}:{test_model(model, conf)}\n')
    outfile.write(f'*\t{tdm_dataset_config.csv_file}:{test_model(model, tdm_dataset_config)}\n')
    outfile.close()

    if count < 4:
        train_seq_readable = [conf.csv_file.split('/')[-1].split('.')[0] for conf in train_seq]
        input(f'{train_seq_readable}')

        model_path = f'TEMP_MODELS/{train_seq_readable}'
        model.save_pretrained(model_path, save_model=True)

        if len(remaining) == 1:
            for conf in set(train_seq):
                if train_seq.count(conf) < 3:
                    # Need copy(model) to not overwrite current model which will be needed for all iterations of the loop
                    recursive_fine_tuning(count+1, train_seq + [conf], TRAIN_NO_SAVE(load_model(model_path), conf))
        elif len(remaining) > 1:
            for conf in csv_configs:
                if train_seq.count(conf) < 3:
                    recursive_fine_tuning(count+1, train_seq + [conf], TRAIN_NO_SAVE(load_model(model_path), conf))

        os.rmdir(model_path)


base_model = load_model(next_for_one_million_model.model_file)
recursive_fine_tuning(0, [], base_model)
'''

'''
def auto_test_funct(model, training_perm: List[Config]):
    outfile = open("three_perm_results.txt", 'a')
    configs_set = {ian_dataset_config, aidan_dataset_config, nathan_dataset_config, nick_dataset_config}
    testable = configs_set - set(training_perm)

    training_perm_string = '['
    for i in training_perm:
        training_perm_string += i.csv_file + ', '
    training_perm_string += ']'

    outfile.write(training_perm_string + '\n')

    for i in testable:
        testing_file_name = i.csv_file
        acc = test_model(model, i)
        result_string = testing_file_name + ': ' + str(acc)

        outfile.write(f'*\t{result_string}\n')

    outfile.close()

x: List[Config] = [ian_dataset_config, aidan_dataset_config, nathan_dataset_config, nick_dataset_config]
for i in range(0,4):
    TRAIN(one_million_model, x[i], 0)
    model = load_model(x[i].model_file, 0)
    auto_test_funct(model, [x[i]])
    for j in range(0,4):
        TRAIN(x[i], x[j], 1)
        model = load_model(x[j].model_file, 1)
        auto_test_funct(model, [x[i], x[j]])
        for k in range(0,4):
            TRAIN(x[j], x[k], 2)
            model = load_model(x[k].model_file, 2)
            auto_test_funct(model, [x[i], x[j], x[k]])
'''