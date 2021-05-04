
import numpy as np
from datetime import datetime
# import math


def to_datetime(date_string):
    return datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')


def from_datetime(date_obj):
    return datetime.strftime(date_obj, '%m/%d/%Y %H:%M:%S')


# takes in date strings
def time_diff(cur_time, prev_time):
    time = to_datetime(cur_time) - to_datetime(prev_time)
    return time.days + (time.seconds+time.microseconds/(10**6))/86400


# win_start_date in format of "04/03/2021 00:00:00"
def mention_window(docs, win_start_date, win_length):

    for ind, doc in enumerate(docs):
        diff = time_diff(win_start_date, doc._.tweeted_at)
        # print(diff)
        if diff > 0:
            window_start = ind
            break
    try:
        window_start
    except UnboundLocalError as e:
        print("Window Length or date incorrect")
        raise e

    for ind, doc in enumerate(docs):
        diff = time_diff(win_start_date, doc._.tweeted_at)
        window_end = ind
        if diff > win_length:
            break
    # window start is newest tweet, end is oldest tweet
    return window_start, window_end


def get_mention_edges(docs, username, follow_weight, win_start_date=None,
                      win_length=31, norm=True):
    def expo_func(x): return np.exp(-.07*x)
    def norm_vec(x): return x/np.linalg.norm(x)

    if not win_start_date:
        win_start_date = datetime.strftime(datetime.utcnow(),
                                           '%m/%d/%Y %H:%M:%S')

    start, end = mention_window(docs,
                                win_start_date=win_start_date,
                                win_length=win_length)

    sub_docs = docs[start:end]

    # flattened ticks from all docs
    all_ticks = set([tick for doc in sub_docs
                     for tick in doc._.tickers])

    # lookup each row of mentions matrix
    tick_lookup = {tick: index for index, tick in enumerate(all_ticks)}

    # initialize empty matrix to hold all coins and mentions
    mentions = np.zeros((len(tick_lookup), len(sub_docs)))

    # fill in values of dict lists where ticker is mentioned
    for ind, doc in enumerate(sub_docs):
        for tick in doc._.tickers:
            mentions[tick_lookup[tick]][ind] += 1

    # function of array of tweet times
    tweet_times = expo_func(np.array(
                       [time_diff(win_start_date, doc._.tweeted_at)
                        for doc in sub_docs]))

    # multiply matrix of mentions by time vector
    tick_weights = np.matmul(mentions, tweet_times)

    # get norm vector of each tick's relavance if chosen
    if norm:
        tick_weights = tick_weights/np.linalg.norm(tick_weights, ord=1)

    # # list of edges to add
    return list(zip([username] * len(sub_docs),
                list(tick_lookup.keys()),
                (1-follow_weight) * tick_weights))
