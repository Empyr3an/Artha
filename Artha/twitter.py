import requests
from requests_oauthlib import OAuth1
import sqlite3
import itertools

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

    def get_follows(self, user_name):
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

    def get_follows1(self, user_name):
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


class TSQLite:

    def __init__(self, location):
        self.conn = sqlite3.connect(location)
        self.cur = self.conn.cursor()

    def create_follow_table(self, twitter, username):
        gen = twitter.get_follows(username)  # generator of follows
        following = list(itertools.chain.from_iterable(gen))  # flatten gen
        with self.conn:
            self.cur.execute("\
                CREATE TABLE u" + username + "\
                (id integer, name text, username text)")
            for user_info in following:
                self.cur.execute("INSERT INTO u" + username +
                                 " VALUES(:id, :name, :username)", user_info)

    def drop_table(self, name):
        with self.conn:
            self.cur.execute("DROP TABLE u"+name)

    def current_tables(self):
        tables = [v[0] for v in
                  self.conn.execute("""
                        SELECT name
                        FROM sqlite_master
                        WHERE type='table';
                  """).fetchall()
                  if v[0] != "sqlite_sequence"]

        return [(v, len(self.conn.execute("SELECT id FROM " + v).fetchall()))
                for v in tables]

    # TODO implement autofollow
