from util.politician_info_puller import get_congress_members
#from util.twitter_api_puller import get_tweets

"""for i in range(80, 118):
    get_congress_members(i, 'senate')
    if i > 101:
        get_congress_members(i, 'house')
#get_tweets('impeach biden')
get_tweets('H.Res.57')
get_tweets('abuse of power biden')
get_tweets('biden high crimes')
get_tweets('impeach joe biden')
get_tweets('criminal biden')"""

from scripts.TestBillCollector import do_things
do_things()

#from scripts.congress_info_puller import get_congress_members
#get_congress_members()