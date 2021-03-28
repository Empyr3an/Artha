import requests
from requests_oauthlib import OAuth1

class TwitterAPI:

    def __init__(self, bearer_token, key=None, secret=None,
                 token=None, token_secret=None):
        self.bearer = {"Authorization": "Bearer " + bearer_token}
        self.endpoint = 'https://api.twitter.com/2'

        if key and secret and token and token_secret:
            self.oauth = OAuth1(key, secret, token, token_secret)
            self.content = {"Content-type": "application/json"}

    def user_lookup(self, user, user_fields=None):
        options = "?"

        if user_fields:
            options += "user.fields="+",".join(user_fields)

        try:
            return requests.get("users/" + user +
                                options,
                                headers=self.bearer).json()["data"]
        except Exception:
            try:
                return requests.get(self.endpoint +
                                    "/users/by/username/" +
                                    user + options,
                                    headers=self.bearer).json()["data"]
            except Exception:
                raise ValueError("not a valid user")

    def get_follows(self, user_name):
        user_id = self.user_lookup(user_name)["id"]
        url = (self.endpoint + "/users/" + user_id +
               "/following?max_results=1000")
        try:
            req = requests.get(url, headers=self.bearer).json()
            yield req["data"]
        except Exception as e:
            raise e

        while "next_token" in req["meta"]:
            try:
                req = requests.get(url+"&pagination_token=" +
                                   req["meta"]["next_token"],
                                   headers=self.bearer).json()
                yield req["data"]
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
        return requests.get("https://api.twitter.com/1.1/application/rate_limit_status.json", auth=self.oauth).json()

    def home_timeline(self):
        return requests.get("https://api.twitter.com/1.1/statuses/home_timeline.json", auth=self.oauth).json()
