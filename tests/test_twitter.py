from Artha import twitter, configs
from Artha.twitter import TwitterAPI
from Artha.configs import twitter_config as c

checkra = TwitterAPI(username="checkra_",
                     bearer_token=c.c_bearer,
                     key=c.c_key,
                     secret=c.c_secret,
                     token=c.c_token,
                     token_secret=c.c_token_secret)


def test_user_lookup():
    # print("hi")
    print(c.c_secret)
    assert checkra.user_lookup("895646764694355968")["username"] ==\
           'HarshaSomisetty'
    assert checkra.user_lookup("HarshaSomisetty")["id"] ==\
           '895646764694355968'
# class TestTwitterAPI:

#     def __init__(self)

# TODO create tests for twitter sqlite stuff
