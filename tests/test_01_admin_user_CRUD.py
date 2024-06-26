import pytest
import requests

from .conftest import ADMIN_API_URL, ADMIN_CREDENTIALS, USER_1, USER_2, USER_3

USERS_ID_LIST = []


@pytest.mark.parametrize(
    "user_data, exp_code, exp_result",
    [
        (USER_1, 200, True),
        (USER_2, 200, True),
    ],
)
def test_create_user(user_data, exp_code, exp_result):
    query = {**ADMIN_CREDENTIALS, "user_data": user_data}
    create_user_response = requests.post(ADMIN_API_URL, json=query)
    created_user_response_data = create_user_response.json()
    USERS_ID_LIST.append(created_user_response_data.get("created_user_data").get("id"))
    assert create_user_response.status_code == exp_code
    assert created_user_response_data.get("result") is exp_result


@pytest.mark.parametrize(
    "invalid_user_data, exp_code, exp_result",
    [
        (USER_1, 409, False),
        ("random_string", 422, False),
        ({"name": "random", "pepe_key": "PEPE"}, 422, False),
        ({"api_key": "valid", "blame": "nobody"}, 422, False),
    ],
)
def test_create_user_invalid_data(invalid_user_data, exp_code, exp_result):
    query = {**ADMIN_CREDENTIALS, "user_data": invalid_user_data}
    invalid_data_response = requests.post(ADMIN_API_URL, json=query)
    assert invalid_data_response.status_code == exp_code
    assert invalid_data_response.json().get("result") is exp_result


@pytest.mark.parametrize(
    "invalid_admin_credentials, valid_user_data, exp_code, exp_result",
    [
        ("random_string", USER_3, 422, False),
        (
            {
                "login": ADMIN_CREDENTIALS.get("login"),
                "wordpass": ADMIN_CREDENTIALS.get("password"),
            },
            USER_3,
            422,
            False,
        ),
        (
            {
                "logout": ADMIN_CREDENTIALS.get("login"),
                "password": ADMIN_CREDENTIALS.get("password"),
            },
            USER_3,
            422,
            False,
        ),
        (
            {
                "login": ADMIN_CREDENTIALS["login"][:-1],
                "password": ADMIN_CREDENTIALS["password"],
            },
            USER_3,
            401,
            False,
        ),
        (
            {
                "login": ADMIN_CREDENTIALS["login"],
                "password": ADMIN_CREDENTIALS["password"][:-1],
            },
            USER_3,
            401,
            False,
        ),
    ],
)
def test_create_delete_user_invalid_credentials(
    invalid_admin_credentials, valid_user_data, exp_code, exp_result
):
    if isinstance(invalid_admin_credentials, dict):
        query = {**invalid_admin_credentials, "user_data": valid_user_data}
    else:
        query = {"string": invalid_admin_credentials, "user_data": valid_user_data}
    invalid_admin_credentials_response = requests.post(ADMIN_API_URL, json=query)
    assert invalid_admin_credentials_response.status_code == exp_code
    assert invalid_admin_credentials_response.json().get("result") is exp_result

    invalid_admin_credentials_response = requests.delete(ADMIN_API_URL, json=query)
    assert invalid_admin_credentials_response.status_code == exp_code
    assert invalid_admin_credentials_response.json().get("result") is exp_result


@pytest.mark.parametrize(
    "user_data, exp_code, exp_result",
    [
        (USER_1, 200, True),
        (USER_2, 200, True),
    ],
)
def test_delete_user(user_data, exp_code, exp_result):
    user_data.update({"id": USERS_ID_LIST.pop(0)})
    query = {**ADMIN_CREDENTIALS, "user_data": user_data}
    delete_user_response = requests.delete(ADMIN_API_URL, json=query)
    assert delete_user_response.status_code == exp_code
    assert delete_user_response.json().get("result") is exp_result


@pytest.mark.parametrize(
    "invalid_user_data, exp_code, exp_result",
    [
        (USER_3, 404, False),
        ("random_string", 422, False),
        ({"id": -1, "name": "random", "pepe_key": "PEPE"}, 422, False),
        ({"id": -1, "api_key": "valid", "blame": "nobody"}, 422, False),
    ],
)
def test_delete_user_invalid_data(invalid_user_data, exp_code, exp_result):
    query = {**ADMIN_CREDENTIALS, "user_data": invalid_user_data}
    invalid_data_response = requests.delete(ADMIN_API_URL, json=query)
    assert invalid_data_response.status_code == exp_code
    assert invalid_data_response.json().get("result") is exp_result
