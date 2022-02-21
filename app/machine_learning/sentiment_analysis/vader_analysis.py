from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import pandas as pd
import time

DATASET_COLUMNS = ["polarity", "ids", "date", "query", "user", "text"]
DATASET_ENCODING = "ISO-8859-1"
# DATASET_FILENAME = "training.1600000.processed.noemoticon.csv"
DATASET_FILENAME = "poop2.csv"
VALIDATE_DATASET = "testdata.manual.2009.06.14.csv"
INPUT_FEATURES_LOGGING = True
BATCH_SIZE = 8


def get_csv_as_df(dataset_name):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    dataset_path = os.path.join(__location__, dataset_name)
    print("Open file:", dataset_path)
    return pd.read_csv(dataset_path, encoding =DATASET_ENCODING , names=DATASET_COLUMNS)


def test_vader():
    sia_obj = SentimentIntensityAnalyzer()
    df = get_csv_as_df(VALIDATE_DATASET)
    start_time = time.time()
    accuracy = 0
    for index, row in df.iterrows():
        if index % 100 == 0:
            print(f"running {index}")
        pred_dict = sia_obj.polarity_scores(row['text'])
        pred_keys = ['neg', 'neu', 'pos']
        pred_vals = [0, 2, 4]
        max = 0
        pred = -1
        for i in range(3):
            if pred_dict[pred_keys[i]] > max:
                pred = pred_vals[i]
        if pred == row['polarity']:
            accuracy += 1
    print(f"TESTING TOOK {(time.time() - start_time) / 500} per tweet")
    accuracy /= 500
    print(f'Accuracy: {accuracy}')