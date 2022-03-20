import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

DATASET_ENCODING = "ISO-8859-1"
out_list = ['A', 'B', 'C']


def get_csv_as_df(dataset_path: str):
    print("Open file:", dataset_path)
    return pd.read_csv(dataset_path, encoding =DATASET_ENCODING,  names=['polarity', 'text'], index_col=False)


df = get_csv_as_df(f'collected.csv')

for i in out_list:
    df = shuffle(df)
    train, test = train_test_split(df, test_size=0.2)

    train.to_csv(f'./shuffled_tweets/shuffled_train_data_{i}.csv', header=False, index=False)
    test.to_csv(f'./shuffled_tweets/shuffled_test_data_{i}.csv', header=False, index=False)
