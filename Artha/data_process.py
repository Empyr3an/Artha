# import numpy as np
# import matplotlib.pyplot as plt
# import time
import json
import contractions
import csv
# from datetime import datetime, timedelta


def load_tweets(username, location="../data/tweets/u"):
    with open(location+username+".json", "r") as r:
        return json.load(r)


# sample output: ['checkra_', '995500158417711104', 'Loma', 'LomahCrypto']
def load_following(username, location="../data/follows/u"):
    with open(location+username+".csv", "r") as csvfile:
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


def clean_tweets(tweets, username):
    tweet_text = []

    text_key = "full_text" if "full_text" in tweets[0].keys() else "text"

    # strips initial tweet mentions to only store text
    for ind, tweet in enumerate(tweets):
        sent = clean_text(tweet[text_key])

        if not sent:
            tweets.pop(ind)
        else:
            cleaned_tweet = (sent, {
                        "created_at": tweet["created_at"],
                        "id": tweet["id"],
                        "username": username
                        # "user_mentions": [user["screen_name"]
                        #                   for user in tweet["user_mentions"]]
                        })
            tweet_text.append(cleaned_tweet)
            # returns tuple of (text, {created date, tweet index})
            # TODO uncomment user mentions here if needed
    return tweet_text
