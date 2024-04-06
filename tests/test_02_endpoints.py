from types import NoneType

import pytest
import requests
from .conftest import (
    FOLLOW_API_URL,
    LIKE_API_URL,
    MEDIA_API_URL,
    TWEET_1,
    TWEET_2,
    INVALID_TWEET,
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
    USER_BY_ID_API_URL,
)


@pytest.fixture(scope="module", autouse=False)
def user_setup():
    user_1_response = requests.post(
        ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_1}
    )
    USER_1.update({"id": user_1_response.json()["created_user_data"]["id"]})
    user_2_response = requests.post(
        ADMIN_API_URL, json={**ADMIN_CREDENTIALS, "user_data": USER_2}
    )
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
def test_post_media_valid_data(
    media_file, exp_code, exp_media_id_type, exp_result, user_setup
):
    new_media_response = requests.post(
        MEDIA_API_URL, files=media_file, headers={API_KEYWORD: USER_1["api_key"]}
    )
    response_data = new_media_response.json()
    response_media_id = response_data.get("media_id")
    if isinstance(response_media_id, int):
        TWEET_1.update(
            {
                "tweet_media_ids": [
                    response_media_id,
                ]
            }
        )
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
    invalid_media_response = requests.post(
        MEDIA_API_URL, files=media_file, headers={API_KEYWORD: api_key}
    )
    response_data = invalid_media_response.json()
    assert invalid_media_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "user, tweet_data, exp_code, exp_result",
    [
        (USER_1, TWEET_1, 200, True),
        (USER_2, TWEET_2, 200, True),
    ],
)
def test_post_tweet_valid_data(user, tweet_data, exp_code, exp_result, user_setup):
    new_tweet_response = requests.post(
        TWEET_API_URL, json=tweet_data, headers={API_KEYWORD: user["api_key"]}
    )
    response_data = new_tweet_response.json()
    tweet_id = response_data.get("tweet_id")
    tweet_data.update(
        {"id": tweet_id, "author": {"id": user["id"], "name": user["name"]}}
    )
    assert new_tweet_response.status_code == exp_code
    assert isinstance(tweet_id, int)
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, tweet_data, exp_code, exp_result",
    [
        (USER_1["api_key"], INVALID_TWEET, 422, False),
        (INVALID_API_KEY, TWEET_2, 401, False),
        (USER_1["api_key"], {"schweet_data": "Charlie, wake up!"}, 422, False),
    ],
)
def test_post_tweet_invalid_data(api_key, tweet_data, exp_code, exp_result, user_setup):
    new_tweet_response = requests.post(
        TWEET_API_URL, json=tweet_data, headers={API_KEYWORD: api_key}
    )
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
    pre_liked_tweet_response = requests.get(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    pre_liked_tweet_data = pre_liked_tweet_response.json()
    pre_liked_likes = len(pre_liked_tweet_data["tweet"]["likes"])
    new_like_response = requests.post(
        LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    response_data = new_like_response.json()
    assert new_like_response.status_code == exp_code
    assert response_data.get("result") is exp_result
    liked_tweet_response = requests.get(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
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
    new_tweet_response = requests.post(
        LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
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
    liked_tweet_response = requests.get(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    liked_tweet_data = liked_tweet_response.json()
    likes = len(liked_tweet_data["tweet"]["likes"])
    new_like_response = requests.delete(
        LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    response_data = new_like_response.json()
    assert new_like_response.status_code == exp_code
    assert response_data.get("result") is exp_result
    unliked_tweet_response = requests.get(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
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
    new_tweet_response = requests.post(
        LIKE_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    response_data = new_tweet_response.json()
    assert new_tweet_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "api_key, exp_code, exp_result",
    [
        (INVALID_API_KEY, 401, False),
        (USER_1["api_key"], 200, True),
    ],
)
def test_get_tweets(api_key, exp_code, exp_result, user_setup):
    tweets_response = requests.get(TWEET_API_URL, headers={API_KEYWORD: api_key})
    tweets_response_data = tweets_response.json()
    assert tweets_response.status_code == exp_code
    assert tweets_response_data.get("result") == exp_result
    if tweets_response.status_code == 200:
        received_tweets = tweets_response_data.get("tweets")
        for expected_tweet in [TWEET_1, TWEET_2]:
            assert any(
                [
                    all(
                        (
                            expected_tweet["id"] == received_tweet["id"],
                            expected_tweet["tweet_data"] == received_tweet["content"],
                            [
                                f"/static/{media_id}.jpeg"
                                for media_id in expected_tweet["tweet_media_ids"]
                            ]
                            == received_tweet["attachments"],
                            expected_tweet["author"]["id"]
                            == received_tweet["author"]["id"],
                            expected_tweet["author"]["name"]
                            == received_tweet["author"]["name"],
                        )
                    )
                    for received_tweet in received_tweets
                ]
            )


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_1, 200, True),
        (INVALID_API_KEY, TWEET_1, 401, False),
        (USER_1["api_key"], INVALID_TWEET, 404, False),
    ],
)
def test_get_tweet_by_id(api_key, tweet, exp_code, exp_result, user_setup):
    tweet_response = requests.get(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    tweet_response_data = tweet_response.json()
    assert tweet_response.status_code == exp_code
    assert tweet_response_data.get("result") == exp_result
    if tweet_response.status_code == 200:
        received_tweet = tweet_response_data["tweet"]
        assert all(
            (
                tweet["id"] == received_tweet["id"],
                tweet["tweet_data"] == received_tweet["content"],
                [f"/static/{media_id}.jpeg" for media_id in tweet["tweet_media_ids"]]
                == received_tweet["attachments"],
                tweet["author"]["id"] == received_tweet["author"]["id"],
                tweet["author"]["name"] == received_tweet["author"]["name"],
            )
        )


@pytest.mark.parametrize(
    "api_key, tweet, exp_code, exp_result",
    [
        (USER_1["api_key"], TWEET_1, 200, True),
        (INVALID_API_KEY, TWEET_1, 401, False),
        (USER_1["api_key"], TWEET_2, 403, False),
        (USER_1["api_key"], INVALID_TWEET, 404, False),
    ],
)
def test_delete_tweet_by_id(api_key, tweet, exp_code, exp_result, user_setup):
    tweet_response = requests.delete(
        TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]), headers={API_KEYWORD: api_key}
    )
    tweet_response_data = tweet_response.json()
    assert tweet_response.status_code == exp_code
    assert tweet_response_data.get("result") == exp_result
    if tweet_response.status_code == 200:
        deleted_tweet_response = requests.get(
            TWEET_BY_ID_API_URL.format(tweet_id=tweet["id"]),
            headers={API_KEYWORD: api_key},
        )
        assert deleted_tweet_response.status_code == 404


@pytest.mark.parametrize(
    "follower, followed_user, exp_code, exp_result",
    [
        (USER_1, USER_2, 200, True),
        (USER_2, USER_1, 200, True),
    ],
)
def test_post_follow_valid_data(
    follower, followed_user, exp_code, exp_result, user_setup
):
    pre_followed_user_response = requests.get(
        USER_BY_ID_API_URL.format(user_id=followed_user["id"]),
        headers={API_KEYWORD: follower["api_key"]},
    )
    pre_followed_user_data = pre_followed_user_response.json()
    assert pre_followed_user_data["user"]["followers"] == []
    new_follow_response = requests.post(
        FOLLOW_API_URL.format(user_id=followed_user["id"]),
        headers={API_KEYWORD: follower["api_key"]},
    )
    response_data = new_follow_response.json()
    assert new_follow_response.status_code == exp_code
    assert response_data.get("result") is exp_result
    followed_user_response = requests.get(
        USER_BY_ID_API_URL.format(user_id=followed_user["id"]),
        headers={API_KEYWORD: follower["api_key"]},
    )
    followed_user_data = followed_user_response.json()
    assert followed_user_data["user"]["followers"][0]["id"] == follower["id"]


@pytest.mark.parametrize(
    "follower, followed_user, exp_code, exp_result",
    [
        (USER_1, USER_1, 409, False),
        (USER_2, USER_1, 409, False),
        (USER_3, USER_1, 401, False),
        (USER_2, USER_3, 404, False),
    ],
)
def test_post_follow_invalid_data(
    follower, followed_user, exp_code, exp_result, user_setup
):
    new_follow_response = requests.post(
        FOLLOW_API_URL.format(user_id=followed_user["id"]),
        headers={API_KEYWORD: follower["api_key"]},
    )
    response_data = new_follow_response.json()
    assert new_follow_response.status_code == exp_code
    assert response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "follower, followed_user, exp_code, exp_result",
    [
        (USER_1, USER_2, 200, True),
        (USER_3, USER_1, 401, False),
    ],
)
def test_delete_follow(follower, followed_user, exp_code, exp_result, user_setup):
    delete_follow_response = requests.delete(
        FOLLOW_API_URL.format(user_id=followed_user["id"]),
        headers={API_KEYWORD: follower["api_key"]},
    )
    delete_follow_response_data = delete_follow_response.json()
    assert delete_follow_response.status_code == exp_code
    assert delete_follow_response_data.get("result") is exp_result
    if delete_follow_response.status_code == 200:
        deleted_follow_user_response = requests.get(
            USER_BY_ID_API_URL.format(user_id=followed_user["id"]),
            headers={API_KEYWORD: follower["api_key"]},
        )
        deleted_follow_user_data = deleted_follow_user_response.json()
        assert deleted_follow_user_data["user"]["followers"] == []


@pytest.mark.parametrize(
    "user, searched_user, exp_code, exp_result",
    [
        (USER_1, USER_2, 200, True),
        (USER_1, USER_1, 200, True),
        (USER_3, USER_1, 401, False),
        (USER_1, USER_3, 404, False),
    ],
)
def test_get_user(user, searched_user, exp_code, exp_result, user_setup):
    if user is searched_user:
        url = USER_BY_ID_API_URL.format(user_id="me")
    else:
        url = USER_BY_ID_API_URL.format(user_id=searched_user["id"])
    user_response = requests.get(url, headers={API_KEYWORD: user["api_key"]})
    user_response_data = user_response.json()
    assert user_response.status_code == exp_code
    assert user_response_data.get("result") == exp_result
    if user_response.status_code == 200:
        if url == "me":
            exp_user = user
        else:
            exp_user = searched_user
        received_user = user_response_data["user"]
        assert all(
            (
                received_user["id"] == exp_user["id"],
                received_user["name"] == exp_user["name"],
            )
        )
