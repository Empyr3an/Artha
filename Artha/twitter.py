import requests
from requests_oauthlib import OAuth1
# import itertools
import numpy as np
import json
from tqdm import tqdm
# from configs import twitter_config as c


# TODO organize methods better, add tests
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

    # get info on a specific user
    def user_lookup(self, user, payload=None):
        options = "?"
        url = self.endpoint2 + "/users"
        if payload:
            options += "user.fields="+",".join(payload)

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

    # method to get userdata for list of user id
    def multiple_user_lookup(self, ids, payload=None):
        if not payload:
            payload = ['created_at',
                       'description',
                       'entities',
                       'id',
                       'name',
                       'protected',
                       'url',
                       'username',
                       'verified',
                       'public_metrics']

        follows_data = []
        for i in tqdm(range(0, int(len(ids)/100)+1)):
            if len(ids[i*100:i*100 + 100]) > 0:
                req = requests.get('https://api.twitter.com/2/users' +
                                   '?user.fields=' + ','.join(payload) +
                                   '&ids=' + ','.join(ids[i*100:i*100 + 100]),
                                   headers=self.bearer)
            else:
                break
            if req.status_code != 200:
                return req
            else:
                follows_data[len(follows_data)-1:
                             len(follows_data)-1] = req.json()["data"]

        return follows_data

    # for given user, return list of all ids user follows, endpt2
    def get_following2(self, user_name):
        user_id = self.user_lookup(user_name)["id"]
        url = self.endpoint2 + "/users/" + user_id +\
                               "/following?max_results=1000"

        data = []

        req = requests.get(url, headers=self.bearer)
        # return req
        if req.status_code != 200:
            return req.status_code
        data = req.json()["data"]

        while "next_token" in req.json()["meta"]:
            req = requests.get(url+"&pagination_token=" +
                               req.json()["meta"]["next_token"],
                               headers=self.bearer)

            if req.status_code != 200:
                return req.status_code

            data[len(data)-1:len(data)-1] = req.json()["data"]

        return [str(i["id"]) for i in data]

    # for given user, return list of all ids user follows, endpt1
    def get_following1(self, user_name):
        url = self.endpoint1 + ("/friends/ids.json?" +
                                "&count=5000" +
                                "&screen_name=" + user_name)

        req = requests.get(url, auth=self.oauth)
        if req.status_code != 200:
            return req.status_code
        data = req.json()["ids"]

        while req.json()["next_cursor"] > -1:
            req = requests.get(url+"&cursor=" +
                               req.json()["next_cursor_str"],
                               auth=self.oauth)
            if req.status_code != 200:
                return req.status_code
            data[len(data)-1:len(data)-1] = req.json()["ids"]

        return [str(i) for i in data]

    # returns generator of user's tweets
    def get_historical_tweets(self, user_name, cnt=500,
                              start_date=None, tweet_fields=None):

        if not start_date:  # normally get twee from earliest history
            user_data = self.user_lookup(user_name, payload=["created_at"])
            start_date = user_data["created_at"]

        if not tweet_fields:  # my default selected payload parameters
            tweet_fields = ["created_at", "context_annotations", "entities",
                            "in_reply_to_user_id", "referenced_tweets"
                            ]

        url = self.endpoint2 + ('/tweets/search/all?max_results=' + str(cnt) +
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

    # from a user, finds difference in people between each user
    def update_with_new_followers(self, from_user):

        to_follow = self.get_follow_differences(from_user, self.username)
        people_to_ignore = ['3393103900',
                            '1356259499431129092',
                            '1036115996',
                            '1272699992575217664'
                            ]
        followed = []
        for follow in to_follow:
            if follow not in people_to_ignore:
                try:
                    self.follow_user_id(follow)
                except Exception as e:
                    raise(e)
                else:
                    followed.append(follow)
                    # follow_lookup = self.user_lookup(follow)
                    # print("Followed", follow["name"])

        return followed

    # returns all user ids user1 follows that user2 does not
    def get_follow_differences(self, user1, user2):
        return np.setdiff1d(self.get_following1(user1),
                            self.get_following1(user2))

    # follow a specific user
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

# TODO add method to get usernames of multiple people at once
    def rate_limits(self):
        return requests.get(self.endpoint1 +
                            "/application/rate_limit_status.json",
                            auth=self.oauth).json()

    # gets latest 20 tweets
    def home_timeline(self, count=200):
        return requests.get(self.endpoint1+"/statuses/home_timeline.json",
                            auth=self.oauth).json()

    # check for valid authorization
    def test_auth(self):
        return requests.get(self.endpoint2+"/tweets?ids=1228393702244134912",
                            headers=self.bearer).status_code


# error_codes = {
#                 200: "OK",
#                 304: "Not Modified",
#                 400: "Bad Request",
#                 401: "Unauthorized",
#                 403: "Forbidden",
#                 404: "Not Found",
#                 406: "Not Acceptable",
#                 410: "Gone",
#                 422: "Unprocessable Entity",
#                 429: "Too Many Requests",
#                 500: "Internal Server Error",
#                 502: "Bad Gateway",
#                 503: "Service Unavailable",
#                 504: "Gateway Timeout"
#             }
