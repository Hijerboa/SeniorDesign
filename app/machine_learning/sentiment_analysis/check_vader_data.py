def validate_data():
    f = open('app/machine_learning/sentiment_analysis/vader_scored_tweets.csv', 'r')

    line = f.readline()
    while line != '':
        if line[0] == '1':
            print('BAD')
        line = f.readline()
