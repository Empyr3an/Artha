# import numpy as np
# import matplotlib.pyplot as plt
# import time
import json
import contractions
from datetime import datetime, timedelta
import pandas as pd


def clean_text(text):
    return contractions.fix(text.replace("&amp;", "and")
                                .replace("@", ""))


def load_tweets(username):
    with open("../data/tweets/u"+username+"tweets.json", "r") as r:
        return json.load(r)


def remove_first_tags(text):
    if text and text[0] == "@":
        if " " in text:
            return remove_first_tags(text.split(" ", 1)[1])
        else:
            return ""
    else:
        return text


def clean_tweets(tweets):
    tweet_text = []
    # strips initial tweet mentions to only store text
    for ind, tweet in enumerate(tweets):
        sent = remove_first_tags(tweet["full_text"]).replace("@", "")
        if not sent:
            tweets.pop(ind)
        else:
            cleaned_tweet = (sent, {
                        "created_at": tweet["created_at"],
                        "id": tweet["id"]  # ,
                        # "user_mentions": [user["screen_name"]
                        #                   for user in tweet["user_mentions"]]
                        })
            tweet_text.append(cleaned_tweet)
            # returns tuple of (text, {created date, tweet index})
            # TODO uncomment user mentions here if needed
    return tweet_text


def _get_tweet_scores(docs, ticker, trim):
    tweet_scores = [[doc._.tweeted_at, doc._.polarity, ind] for ind, doc in enumerate(docs)]

    if ticker:
        to_remove = [ind for ind, doc in enumerate(docs) if ticker not in doc._.tickers]
        for i in sorted(to_remove, reverse=True):
            del tweet_scores[i]

    i = 0
    if trim:
        while i < len(tweet_scores)-1:
            cur_tweet = tweet_scores[i]
            next_tweet = tweet_scores[i+1]

            cur_time = datetime.strptime(cur_tweet[0], '%m/%d/%Y %H:%M:%S')
            next_time = datetime.strptime(next_tweet[0], '%m/%d/%Y %H:%M:%S')

            time_diff = cur_time-next_time

            if time_diff < timedelta(seconds=5):
                tweet_scores[i][1] = (cur_tweet[1]+next_tweet[1])/2
                del tweet_scores[i+1]
            else:
                i += 1

    return tweet_scores


def tweet_df(docs, ticker=None, trim=True):
    tweet_scores = _get_tweet_scores(docs, ticker, trim)
    tweet_times = pd.to_datetime([i[0] for i in tweet_scores])
    return pd.DataFrame([[i[1], i[2]] for i in tweet_scores],
                        index=tweet_times,
                        columns=["Sentiment", "Tweet_num"])
