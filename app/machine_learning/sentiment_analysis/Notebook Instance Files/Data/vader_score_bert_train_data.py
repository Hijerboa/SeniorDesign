from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_FILE_PATH = './vader_scored_tweets.csv'
OUTPUT_DIRECTORY = './vader_classified_tweets'
OUTPUT_FILE_PATH_BASE = '/classified_vader_scored_tweets_threshold_'
'''
THRESHOLDS = [[-0.4, 0.4],
              [-0.5, 0.5],
              [-0.6, 0.6],
              [-0.7, 0.7],
              [-0.75, 0.75]]
'''
THRESHOLDS = [[-0.25, 0.25],
              [-0.35, 0.35]]

sia_obj = SentimentIntensityAnalyzer()


def vader_score(tweet_text: str):
    return sia_obj.polarity_scores(tweet_text)


def generate_data():
    in_file = open(INPUT_FILE_PATH, 'r', encoding='utf-8', errors='replace')
    out_files = []
    for i in THRESHOLDS:
        tmp = open(f'{OUTPUT_DIRECTORY}{OUTPUT_FILE_PATH_BASE}{str(i).replace(" ", "")}.csv', 'w', encoding='utf-8', errors='replace')
        out_files.append(tmp)

    line = in_file.readline()

    class_dict = {'neg': -1, 'neu': 0, 'pos': 1}

    while line != '':
        text = line.split(',')[1].replace('\n', '')

        score_dict = vader_score(text)

        comp_val = score_dict['compound']
        for i in range(len(THRESHOLDS)):
            if comp_val <= THRESHOLDS[i][0]:
                score = -1
            elif comp_val >= THRESHOLDS[i][1]:
                score = 1
            else:
                score = 0
            out_files[i].write(f'{score},{text}\n')

        line = in_file.readline()


generate_data()
