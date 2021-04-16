from config import mongo_config as c
import pymongo
import urllib


# TODO CLEANUP MONGO USECASE
class TMongo:

    username = urllib.parse.quote_plus(c.mongo_username)
    password = urllib.parse.quote_plus(c.mongo_password)
    cluster = pymongo.MongoClient("mongodb+srv://{}:{}"
                                  "@cluster0.qpf0e.mongodb.net"
                                  "/Artha?retryWrites=true&w=majority"
                                  .format(username, password))
    db = cluster["Twitter"]

    # store all user tweets to mongodb
    @classmethod
    def mongo_tweets(cls, twitter, username):
        # adds desired

        tweet_fields = [
            'text',
            'attachments',
            'context_annotations',
            'created_at',
            'entities'
        ]

        gen = twitter.get_tweets(user_name=username, tweet_fields=weet_fields)

        # following.append(str(twitter.user_lookup(username)["id"]))

        # url = ('https://api.twitter.com/2/users?user.fields='
        #     'created_at,'
        #     #    'description,'
        #     'entities,'
        #     'id,'
        #     'name,'
        #     #    'protected,'
        #     #    'url,'
        #     'username,'
        #     'verified,'
        #     'public_metrics'
        #     '&ids=')

        follow_data = []
        for i in range(0, int(len(following)/100)+1):
            req = requests.get(url+",".join(following[i*100:i*100 + 100]),
                            headers=twitter.bearer)
            follow_data[len(follow_data)-1:
                        len(follow_data)-1] = req.json()["data"]

        return cls.db["TwitterUsers"].update_many(
                                    [user for user in follow_data])
        # print("updated mongo")