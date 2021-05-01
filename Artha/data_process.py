# import numpy as np
# import matplotlib.pyplot as plt
# import time
import json
import contractions
from datetime import datetime
import csv
# from datetime import datetime, timedelta


def load_tweets(username):
    with open("../data/tweets/u"+username+".json", "r") as r:
        return json.load(r)


# sample output: ['checkra_', '995500158417711104', 'Loma', 'LomahCrypto']
def load_following(username):
    with open("../data/follows/u"+username+".csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', )
        next(reader, None)
        follows = list(reader)
        return [[username]+follow for follow in follows]


def remove_tags(text):
    if text and text[0] == "@":
        return remove_tags(text.split(" ", 1)[1]) if " " in text else ""
    else:
        return text


def clean_text(text): return contractions.fix(
                                    remove_tags(text)
                                    .replace("&amp;", "and")
                                    .replace("@", ""))


def clean_tweets(tweets):
    tweet_text = []
    # strips initial tweet mentions to only store text
    for ind, tweet in enumerate(tweets):
        sent = clean_text(tweet["full_text"])

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


def time_diff(date_string):
    time = datetime.now() - datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
    return time.days + (time.seconds+time.microseconds/(10**6))/86400
