import requests
from requests_oauthlib import OAuth1
# import itertools
import pymongo
import urllib
from . import mongo_config as c
import numpy as np
import json


class TwitterAPI:

    def __init__(self, username, bearer_token, key=None, secret=None,
                 token=None, token_secret=None):

        self.endpoint2 = 'https://api.twitter.com/2'
        self.endpoint1 = 'https://api.twitter.com/1.1'
        self.bearer = {"Authorization": "Bearer " + bearer_token}
        self.username = username
        self.id = requests.get(self.endpoint2+"/users/by/username/"+username,
                               headers=self.bearer).json()["data"]["id"]

        if key and secret and token and token_secret:
            self.oauth = OAuth1(key, secret, token, token_secret)
            self.content = {"Content-type": "application/json"}

    def user_lookup(self, user, user_fields=None):
        options = "?"
        url = self.endpoint2 + "/users"
        if user_fields:
            options += "user.fields="+",".join(user_fields)

        try:
            req = requests.get(url + "/" + user +
                               options, headers=self.bearer)
            if req.status_code == 200:
                return req.json()['data']
            else:
                req2 = requests.get(url + "/by/username/" +
                                    user + options, headers=self.bearer)
                if req2.status_code == 200:
                    return req2.json()['data']
                else:
                    raise ValueError(req2.url)

        except Exception as e:
            raise ValueError(e)

    def get_following(self, user_name):
        user_id = self.user_lookup(user_name)["id"]
        url = self.endpoint2 + "/users/" + user_id +\
                               "/following?max_results=1000"

        data = []
        try:
            req = requests.get(url, headers=self.bearer)
            data = req.json()["data"]
        except Exception as e:
            raise e

        while "next_token" in req.json()["meta"]:
            try:
                req = requests.get(url+"&pagination_token=" +
                                   req["meta"]["next_token"],
                                   headers=self.bearer)
                data[len(data)-1:len(data)-1] = req.json()["data"]
            except Exception as e:
                raise e

        return [str(i) for i in data]

    def get_following1(self, user_name):
        url = self.endpoint1 + ("/friends/ids.json?" +
                                "&count=5000" +
                                "&screen_name=" + user_name)
        try:
            req = requests.get(url, auth=self.oauth)
            data = req.json()["ids"]
        except Exception as e:
            raise e

        while req.json()["next_cursor"] > -1:
            try:
                req = requests.get(url+"&cursor=" +
                                   req.json()["next_cursor_str"],
                                   auth=self.oauth)
                data[len(data)-1:len(data)-1] = req.json()["ids"]
            except Exception as e:
                print(req.json())
                raise e

        return [str(i) for i in data]

    def get_tweets(self, user_name, count=500,
                   start_date=None, tweet_fields=None):
        if not start_date:  # get tweets from earliest of history
            user_data = self.user_lookup(user_name, user_fields=["created_at"])
            start_date = user_data["created_at"]

        if not tweet_fields:  # my default selected payload parameters
            tweet_fields = ["created_at", "context_annotations", "entities",
                            "in_reply_to_user_id", "referenced_tweets"
                            ]

        url = self.endpoint + ('/tweets/search/all?max_results=' + str(count) +
                               '&start_time=' + start_date +
                               '&query=from:' + user_name +
                               '&tweet.fields=' + ','.join(tweet_fields))

        try:
            req = requests.get(url, headers=self.bearer)
            yield req.json()["data"]
        except Exception as e:
            raise e

        while "next_token" in req.json()["meta"]:
            try:
                req = requests.get(url + "&next_token=" +
                                   req.json()["meta"]["next_token"],
                                   headers=self.bearer)
                yield req.json()["data"]
            except Exception as e:
                raise e

    def update_with_new_followers(self, from_user):

        to_follow = self.get_follow_differences(from_user, self.username)
        blacklist = ['3393103900',
                     '1356259499431129092',
                     '1036115996',
                     '1272699992575217664'
                     ]
        for follow in to_follow:
            if follow not in blacklist:
                try:
                    self.follow_user_id(follow)
                except Exception as e:
                    raise(e)
                else:
                    print("followed", self.user_lookup(follow)["name"], follow)

    # returns all user ids user1 follows that user2 does not
    def get_follow_differences(self, user1, user2):
        return np.setdiff1d(self.get_following1(user1),
                            self.get_following1(user2))

    def follow_user_id(self, user_id):
        try:
            requests.post(
                self.endpoint2+"/users/"+self.id+"/following",
                auth=self.oauth,
                headers={"Content-type": "application/json"},
                data=json.dumps({"target_user_id": user_id})
            )
        except Exception as e:
            return e

    def rate_limits(self):
        return requests.get(self.endpoint1 +
                            "/application/rate_limit_status.json",
                            auth=self.oauth).json()

    def home_timeline(self):
        return requests.get(self.endpoint1+"/statuses/home_timeline.json",
                            auth=self.oauth).json()

    def test_auth(self):
        return requests.get(self.endpoint2+"/tweets?ids=1228393702244134912",
                            headers=self.bearer).status_code


# class to manage reference data stored in mongodb
class TMongo:

    username = urllib.parse.quote_plus(c.mongo_username)
    password = urllib.parse.quote_plus(c.mongo_password)
    cluster = pymongo.MongoClient("mongodb+srv://{}:{}"
                                  "@cluster0.qpf0e.mongodb.net"
                                  "/Artha?retryWrites=true&w=majority"
                                  .format(username, password))
    db = cluster["Twitter"]

    # add information about a user and all their following to mongodb database
    @classmethod
    def update_account_data(cls, twitter, username, following):
        # adds desired
        following.append(str(twitter.user_lookup(username)["id"]))

        url = ('https://api.twitter.com/2/users?user.fields='
               'created_at,'
               'description,'
               'entities,'
               'id,'
               'name,'
               'protected,'
               'url,'
               'username,'
               'verified,'
               'public_metrics'
               '&ids=')

        follow_data = []
        for i in range(0, int(len(following)/100)+1):
            req = requests.get(url+",".join(following[i*100:i*100 + 100]),
                               headers=twitter.bearer).json()["data"]
            follow_data[len(follow_data)-1:len(follow_data)-1] = req

        # return cls.db["TwitterUsers"].update_many(
        #                           [user for user in follow_data])
        # print("updated mongo")


class TSQLite:

    @classmethod
    def create_follow_table(cls, conn, twitter, username):
        print('creating table for ', username)
        following = [str(id) for id in twitter.get_following1(username)]
        # following_names = 
        try:
            with conn:
                if "following" in cls.current_tables(conn):
                    conn.cursor().execute("DROP TABLE following")

                conn.cursor().execute("\
                    CREATE TABLE following\
                    (account_id str)")

                for user_id in following:
                    conn.cursor().execute("INSERT INTO following\
                                           VALUES(:account_id)", [user_id])
        except Exception as e:
            print(following[:10])
            raise e
        # print("updating mongo")
        # TMongo.update_account_data(twitter, username, following)

    @classmethod
    def drop_table(cls, conn, name):
        with conn:
            conn.cursor().execute("DROP TABLE u"+name)

    @classmethod
    def current_tables(cls, conn):
        tables = [v[0] for v in
                  conn.cursor().execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table';
                  """).fetchall()
                  if v[0] != "sqlite_sequence"]

        return tables
