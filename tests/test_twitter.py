import pytest
from Artha import twitter
import config as c

checkra = twitter.TwitterAPI(bearer_token=c.c_bearer, key=c.c_key, secret=c.c_secret, token=c.c_token, token_secret=c.c_token_secret)


# @pytest.fixture
def test_user_lookup():
    # print("hi")
    print(c.c_secret)
    assert checkra.user_lookup("895646764694355968")["data"]["username"] == 'HarshaSomisetty'
    assert checkra.user_lookup("HarshaSomisetty")["data"]["id"] == '895646764694355968'
