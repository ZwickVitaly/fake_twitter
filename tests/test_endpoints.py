from types import NoneType

import pytest
import requests
from .conftest import (
    FOLLOW_API_URL,
    LIKE_API_URL,
    MEDIA_API_URL,
    REPOST_API_URL,
    TWEET_1,
    TWEET_2,
    INVALID_MEDIA_TWEET,
    TWEET_API_URL,
    USER_1,
    USER_2,
    USER_3,
    USER_API_URL,
    ADMIN_CREDENTIALS,
    ADMIN_API_URL,
    API_KEYWORD,
    VALID_MEDIA_FILE_PATH,
    INVALID_SIZE_MEDIA_FILE_PATH,
    INVALID_EXTENSION_MEDIA_FILE_PATH,
    INVALID_API_KEY,
    TWEET_BY_ID_API_URL,
    USER_BY_ID_API_URL
)


@pytest.fixture(scope="session", autouse=False)
def user_setup():
    user_1_response = requests.post(ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_1})
    USER_1.update({"id": user_1_response.json()["created_user_data"]["id"]})
    user_2_response = requests.post(ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_2})
    USER_2.update({"id": user_2_response.json()["created_user_data"]["id"]})
    yield
    requests.delete(ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_1})
    requests.delete(ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_2})


@pytest.mark.parametrize(
    "media_file, exp_code, exp_media_id_type, exp_result",
    [
        ({"file": open(VALID_MEDIA_FILE_PATH, "rb")}, 200, int, True),
        ({"file": open(INVALID_EXTENSION_MEDIA_FILE_PATH, "rb")}, 400, NoneType, False),
        ({"file": open(INVALID_SIZE_MEDIA_FILE_PATH, "rb")}, 400, NoneType, False),
    ],
)
def test_post_media_valid_data(media_file, exp_code, exp_media_id_type, exp_result, user_setup):
    new_media_response = requests.post(MEDIA_API_URL, files=media_file, headers={API_KEYWORD: USER_1["api_key"]})
    response_data = new_media_response.json()
    response_media_id = response_data.get("media_id")
    if response_media_id:
        TWEET_1.update({"tweet_media_ids": [response_media_id,]})
    assert new_media_response.status_code == exp_code
    assert isinstance(response_media_id, exp_media_id_type)
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, media_file, exp_code, exp_result",
    [
        (INVALID_API_KEY, {"file": open(VALID_MEDIA_FILE_PATH, "rb")}, 401, False),
        (USER_1["api_key"], {"solo": "zolo"}, 422, False),
        (USER_1["api_key"], None, 422, False),
    ],
)
def test_post_media_invalid_data(api_key, media_file, exp_code, exp_result, user_setup):
    invalid_media_response = requests.post(MEDIA_API_URL, files=media_file, headers={API_KEYWORD: api_key})
    response_data = invalid_media_response.json()
    assert invalid_media_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, tweet_data, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_1, 200, True),
        (USER_2["api_key"], TWEET_2, 200, True),
    ],
)
def test_post_tweet_valid_data(api_key, tweet_data, exp_code, exp_result, user_setup):
    new_tweet_response = requests.post(TWEET_API_URL, json=tweet_data, headers={API_KEYWORD: api_key})
    response_data = new_tweet_response.json()
    tweet_id = response_data.get("tweet_id")
    tweet_data.update({"id": tweet_id})
    assert new_tweet_response.status_code == exp_code
    assert isinstance(tweet_id, int)
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, tweet_data, exp_code, exp_result",
    [
        (USER_1["api_key"], INVALID_MEDIA_TWEET, 422, False),
        (INVALID_API_KEY, TWEET_2, 401, False),
        (USER_1["api_key"], {"schweet_data": "Charlie, wake up!"}, 422, False),
    ],
)
def test_post_tweet_invalid_data(api_key, tweet_data, exp_code, exp_result, user_setup):

    new_tweet_response = requests.post(TWEET_API_URL, json=tweet_data, headers={API_KEYWORD: api_key})
    response_data = new_tweet_response.json()
    assert new_tweet_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_2, 200, True),
        (USER_2["api_key"], TWEET_1, 200, True),
    ],
)
def test_post_like_valid_data(api_key, tweet, exp_code, exp_result, user_setup):
    pre_liked_tweet_response = requests.get(TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    pre_liked_tweet_data = pre_liked_tweet_response.json()
    pre_liked_likes = len(pre_liked_tweet_data["tweet"]["likes"])
    new_like_response = requests.post(LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    response_data = new_like_response.json()
    assert new_like_response.status_code == exp_code
    assert response_data.get("result") is exp_result
    liked_tweet_response = requests.get(TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    liked_tweet_data = liked_tweet_response.json()
    likes = len(liked_tweet_data["tweet"]["likes"])
    assert likes == (pre_liked_likes + 1)


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_2, 409, False),
        (USER_2["api_key"], TWEET_1, 409, False),
        (INVALID_API_KEY, TWEET_1, 401, False),
        (USER_2["api_key"], {"id": "random_string"}, 404, None),
        (USER_2["api_key"], {"id": -3}, 404, None),
    ],
)
def test_post_like_invalid_data(api_key, tweet, exp_code, exp_result, user_setup):
    new_tweet_response = requests.post(LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    response_data = new_tweet_response.json()
    assert new_tweet_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_2, 200, True),
        (USER_2["api_key"], TWEET_1, 200, True),
    ],
)
def test_delete_like_valid_data(api_key, tweet, exp_code, exp_result, user_setup):
    liked_tweet_response = requests.get(TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    liked_tweet_data = liked_tweet_response.json()
    likes = len(liked_tweet_data["tweet"]["likes"])
    new_like_response = requests.delete(LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    response_data = new_like_response.json()
    assert new_like_response.status_code == exp_code
    assert response_data.get("result") is exp_result
    unliked_tweet_response = requests.get(TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    unliked_tweet_data = unliked_tweet_response.json()
    unliked_likes = len(unliked_tweet_data["tweet"]["likes"])
    assert unliked_likes == (likes - 1)


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (INVALID_API_KEY, TWEET_1, 401, False),
        (USER_2["api_key"], {"id": "random_string"}, 404, None),
    ],
)
def test_delete_like_invalid_data(api_key, tweet, exp_code, exp_result, user_setup):
    new_tweet_response = requests.post(LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key})
    response_data = new_tweet_response.json()
    assert new_tweet_response.status_code == exp_code
    assert response_data.get("result") is exp_result

