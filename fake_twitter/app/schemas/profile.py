"""
Schemas for validation of user's profile info
"""


from pydantic import Field

from .result import DefaultPositiveResult
from .user import UserBaseOutSchema


class ProfileOutSchema(UserBaseOutSchema):
    """
    Schema for profile data response
    """

    following: list[UserBaseOutSchema] = Field(
        title="List of user's followed users",
        examples=[
            [
                {
                    "id": 2,
                    "name": "John",
                },
                {
                    "id": 3,
                    "name": "Jane",
                },
            ],
        ],
    )
    followers: list[UserBaseOutSchema] = Field(
        title="List of user's followers",
        examples=[
            [
                {
                    "id": 4,
                    "name": "John",
                },
                {
                    "id": 5,
                    "name": "Jane",
                },
            ],
        ],
    )


class ProfileResultSchema(DefaultPositiveResult):
    """
    Schema for profile data response, paired with default positive response {"result": True}
    """

    user: ProfileOutSchema = Field()
