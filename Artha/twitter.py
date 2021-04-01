import requests
from requests_oauthlib import OAuth1
import itertools
import pymongo
import urllib
from . import mongo_config as c


# import time


class TwitterAPI:

    def __init__(self, bearer_token, key=None, secret=None,
                 token=None, token_secret=None):

        self.endpoint2 = 'https://api.twitter.com/2'
        self.endpoint1 = 'https://api.twitter.com/1.1'
        self.bearer = {"Authorization": "Bearer " + bearer_token}

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
        try:
            req = requests.get(url, headers=self.bearer)
            yield req.json()["data"]
        except Exception as e:
            raise e

        while "next_token" in req["meta"]:
            try:
                req = requests.get(url+"&pagination_token=" +
                                   req["meta"]["next_token"],
                                   headers=self.bearer)
                yield req.json()["data"]
            except Exception as e:
                raise e

    def get_following1(self, user_name):
        # user_id = self.user_lookup(user_name)["id"]
        url = self.endpoint1 + "/friends/ids.json?" +\
                               "&count=5000" +\
                               "&screen_name=" + user_name
        try:
            req = requests.get(url, auth=self.oauth)
            yield req.json()["ids"]
        except Exception as e:
            raise e

        while req.json()["next_cursor"] > -1:
            try:
                req = requests.get(url+"&cursor=" +
                                   req.json()["next_cursor_str"],
                                   auth=self.oauth)
                yield req.json()["ids"]
            except Exception as e:
                raise e

    def get_tweets(self, user_name, results=500,
                   start_date=None, tweet_fields=None):
        if not start_date:
            user_data = self.user_lookup(user_name, user_fields=["created_at"])
            start_date = user_data["created_at"]

        url = self.endpoint + '/tweets/search/all?max_results=' +\
                              str(results) + '&start_time=' + start_date +\
                              '&query=from:' + user_name

        if tweet_fields:
            url += "&tweet.fields=" + ",".join(tweet_fields)
        else:
            url += "&tweet.fields=" + ",".join([
                    "created_at", "context_annotations", "entities",
                    "in_reply_to_user_id", "referenced_tweets"
                    ])
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


class TMongo:

    username = urllib.parse.quote_plus(c.mongo_username)
    password = urllib.parse.quote_plus(c.mongo_password)
    cluster = pymongo.MongoClient("mongodb+srv://{}:{}@cluster0.qpf0e.mongodb.net/ \
                                   Artha?retryWrites=true&w=majority"
                                  .format(username, password))
    db = cluster["Twitter"]

    @classmethod
    def update_account_data(cls, twitter, username, following):
        following.append(twitter.user_lookup(username)["id"])
        url = "https://api.twitter.com/2/users?user.fields=\
               created_at,\
               description,\
               entities,\
               id,\
               name,\
               protected,\
               url,\
               username,\
               verified,\
               public_metrics\
               &ids="

        follow_data = []
        for i in range(0, int(len(following)/100)+1):
            req = requests.get(url+",".join(following[i*100:i*100 + 100]),
                               headers=twitter.bearer)["data"]
            follow_data[len(follow_data)-1:len(follow_data)-1] = req.json()

        cls.db["TwitterUsers"].insert_many([user for user in follow_data])


class TSQLite:

    @classmethod
    def create_follow_table(cls, conn, twitter, username):
        gen = twitter.get_following1(username)  # generator of follows
        following = list(map(str, list(itertools.chain.from_iterable(gen))))

        try:
            with conn:
                conn.cursor().execute("\
                    CREATE TABLE following\
                    (account_id str)")
                for user_info in following:
                    conn.cursor().execute("INSERT INTO following\
                                          VALUES(:id)", [user_info])
        except Exception as e:
            print(following[:10])
            raise e

        TMongo.update_account_data(twitter, username, following)

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

        return [(v, len(conn.cursor().execute("SELECT id \
                                               FROM " + v).fetchall()))
                for v in tables]

        # TODO implement autofollow
