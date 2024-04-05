from os import getenv

LOCALHOST_API_URL: str = "http://fake_twitter:8000/api"

USER_API_URL: str = f"{LOCALHOST_API_URL}/users"

TWEET_API_URL: str = f"{LOCALHOST_API_URL}/tweets"

TWEET_BY_ID_API_URL: str = f"{TWEET_API_URL}/{{tweet_id}}"

LIKE_API_URL: str = f"{TWEET_BY_ID_API_URL}/likes"

REPOST_API_URL: str = f"{TWEET_BY_ID_API_URL}/repost"

USER_BY_ID_API_URL: str = f"{USER_API_URL}/{{user_id}}"

FOLLOW_API_URL: str = f"{USER_BY_ID_API_URL}/follow"

MEDIA_API_URL: str = f"{LOCALHOST_API_URL}/medias"

ADMIN_API_URL: str = f"{LOCALHOST_API_URL}/admin/user"

ADMIN_CREDENTIALS: dict = {
    "login": getenv("ADMIN_LOGIN"),
    "password": getenv("ADMIN_PASSWORD"),
}

API_KEYWORD: str = getenv("API_KEYWORD") or "api-key"

USER_1: dict = {
    "api_key": "web_test_1_header",
    "name": "web_test_1",
}

USER_2: dict = {
    "api_key": "web_test_2_header",
    "name": "web_test_2",
}

USER_3: dict = {
    "name": "Hopefully Valid",
    "api_key": "Definitely Valid"
}

TWEET_1: dict = {"tweet_data": "LOL"}

TWEET_2: dict = {"tweet_data": "KEK"}

INVALID_MEDIA_TWEET: dict = {"tweet_data": "KEK", "tweet_media_ids": [-1,]}

VALID_MEDIA_FILE_PATH = "/tests/valid_image_test.jpeg"

INVALID_EXTENSION_MEDIA_FILE_PATH = "/tests/invalid_extenion_file_test.txt"

INVALID_SIZE_MEDIA_FILE_PATH = "/tests/invalid_size_file_test.jpeg"

INVALID_API_KEY = "THIS API KEY IS TOTALLY INVALID"
