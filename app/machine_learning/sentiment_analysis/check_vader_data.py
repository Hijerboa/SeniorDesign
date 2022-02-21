def validate_data():
    f = open('app/machine_learning/sentiment_analysis/vader_scored_tweets.csv', 'r')

    line = f.readline()
    while line != '':
        if line[0] == '1':
            print('BAD')
        line = f.readline()

def fix_data():
    f = open('app/machine_learning/sentiment_analysis/vader_scored_tweets.csv', 'r', encoding='utf-8', errors='replace')
    fd = open('app/machine_learning/sentiment_analysis/clean.csv', 'w', encoding='utf-8', errors='replace')

    line = f.readline()
    while line != '':
        fd.write(line)
        line = f.readline()

