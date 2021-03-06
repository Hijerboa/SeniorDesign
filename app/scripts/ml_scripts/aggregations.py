from machine_learning.aggregation.aggregation_scaffold import get_tweets, get_flat_sentiment, verified_user_sentiment, politician_sentiment, \
    more_than_average_likes, confidence_weighting, count_in_buckets

def get_aggregations_dict(bill_id):

    tweets, initial_dict = get_tweets(bill_id)
    initial_dict['non_conf_thresholded_flat'] = get_flat_sentiment(tweets)
    initial_dict['conf_thresholded_flat'] = get_flat_sentiment(tweets, confidence_thresholding=True)

    initial_dict['non_conf_thresholded_verified'] = verified_user_sentiment(tweets)
    initial_dict['conf_thresholded_verified'] = verified_user_sentiment(tweets, confidence_thresholding=True)

    initial_dict['non_conf_thresholded_politicians'] = politician_sentiment(tweets)

    initial_dict['non_conf_thresholded_std_mean_likes'] = more_than_average_likes(tweets)
    initial_dict['conf_thresholded_std_mean_likes'] = more_than_average_likes(tweets, confidence_thresholding=True)

    initial_dict['confidence_weighted'] = confidence_weighting(tweets)
    
    initial_dict['count_in_buckets'] = count_in_buckets(tweets)

    return initial_dict