import pandas as pd
import os

DATASET_ENCODING = "ISO-8859-1"
DATASET_FILENAME = "training.1600000.processed.noemoticon.csv"
TWEETS_PER_DF = 750
# DATASET_FILENAME = "poop.csv"

def get_csv_as_df():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    dataset_path = os.path.join(__location__, DATASET_FILENAME)
    print("Open file:", dataset_path)
    return pd.read_csv(dataset_path, encoding=DATASET_ENCODING, names=["polarity", "ids", "date", "query", "user", "text"])

def new_csv():
    df = get_csv_as_df()
    df1 = df[df.polarity == 0]
    df1 = df1.iloc[:TWEETS_PER_DF, : ]
    df2 = df[df.polarity == 4]
    df2 = df2.iloc[0:TWEETS_PER_DF, : ]
    final_df = pd.concat([df1, df2])
    final_df.to_csv("poop2.csv", index=False, header=False)