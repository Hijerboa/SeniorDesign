from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT_FILE_PATH = './vader_scored_tweets.csv'
OUTPUT_FILE_PATH_COMPVAL = './classified_vader_scored_tweets_compound_val.csv'
OUTPUT_FILE_PATH_MAXVAL = './classified_vader_scored_tweets_max_val.csv'

sia_obj = SentimentIntensityAnalyzer()


def vader_score(tweet_text: str):
    return sia_obj.polarity_scores(tweet_text) 


def generate_data():
    in_file = open(INPUT_FILE_PATH, 'r', encoding='utf-8', errors='replace')
    out_file_cv = open(OUTPUT_FILE_PATH_COMPVAL, 'w', encoding='utf-8', errors='replace')
    out_file_mv = open(OUTPUT_FILE_PATH_MAXVAL, 'w', encoding='utf-8', errors='replace')

    line = in_file.readline()

    class_dict = {'neg':-1, 'neu':0, 'pos':1}

    while line != '':
        text = line.split(',')[1].replace('\n', '')

        score_dict = vader_score(text)
        
        comp_val = score_dict['compound']
        if comp_val <= -0.5:
            score = -1
        elif comp_val >= 0.5:
            score = 1
        else:
            score = 0
        out_file_cv.write(f'{score},{text}\n')

        score_dict.pop('compound')
        score = class_dict[max(score_dict, key=score_dict.get)]
        out_file_mv.write(f'{score},{text}\n')

        line = in_file.readline()

generate_data()
