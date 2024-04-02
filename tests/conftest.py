from os import getenv


LOCALHOST_API_URL = "http://fake_twitter:8000/api/"

USER_API_URL = "user"

TWEET_API_URL = "tweet"

LIKE_API_URL = f"{TWEET_API_URL}/{{tweet_id}}/like"

REPOST_API_URL = f"{TWEET_API_URL}/{{tweet_id}}/repost"

FOLLOW_API_URL = f"{USER_API_URL}/{{followed_id}}/follow"

MEDIA_API_URL = "media"

ADMIN_API_URL = "admin/user"

ADMIN_CREDENTIALS = {
    "login": getenv("ADMIN_LOGIN"),
    "password": getenv("ADMIN_PASSWORD"),
}

USER_1 = {
    "api_key": "web_test_1_header",
    "name": "web_test_1",
}

USER_2 = {
    "api_key": "web_test_2_header",
    "name": "web_test_2",
}

USER_3 = {
    "name": "Hopefully Valid",
    "api_key": "Definitely Valid"
}

TWEET_1 = {
    "tweet_data": "LOL"
}

TWEET_2 = {
    "tweet_data": "KEK"
}

