from pydantic import BaseModel, Field

from .repost import RepostOutSchema
from .result import DefaultResult
from .tweet import TweetOutSchema
from .user import UserBaseOutSchema


class ProfileOutSchema(UserBaseOutSchema):
    tweets: list[TweetOutSchema | RepostOutSchema] = Field(
        title="List of user's tweets and reposts",
        examples=[
            [
                {
                    "uuid": "58977674-4581-4d26-b862-2bf4c2b23a49",
                    "author": {
                        "uuid": "205bc500-c348-47ad-984c-7ab9c16633ae",
                        "name": "lol",
                    },
                    "content": "Later, alligator",
                    "views": 0,
                    "likes": 0,
                    "reposts": 0,
                    "images": [],
                    "created_at": "2024-02-04T09:30:14+00:00",
                },
                {
                    "uuid": "58977674-4581-4d26-b862-2bf4c2b23a49",
                    "repost": {
                        "uuid": "58977674-4581-4d26-b862-2bf4c2b23a49",
                        "author": {
                            "uuid": "205bc500-c348-47ad-984c-7ab9c16633ae",
                            "name": "lol",
                        },
                        "content": "Lol kek azazaza",
                        "views": 1,
                        "likes": 1,
                        "reposts": 1,
                        "images": ["1", "2"],
                        "created_at": "2024-02-04T09:30:14+00:00",
                    },
                    "created_at": "2024-02-04T09:30:14+00:00",
                },
            ]
        ],
    )
    followed: list[UserBaseOutSchema] = Field(
        title="List of user's followed users",
        examples=[
            [
                {
                    "uuid": "bdd7e8c8-f65c-4978-9c70-95ec39b13f9d",
                    "name": "John",
                },
                {
                    "uuid": "58977674-4581-4d26-b862-2bf4c2b23a49",
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
                    "uuid": "bdd7e8c8-f65c-4978-9c70-95ec39b13f9d",
                    "name": "John",
                },
                {
                    "uuid": "58977674-4581-4d26-b862-2bf4c2b23a49",
                    "name": "Jane",
                },
            ],
        ],
    )


class ProfileResultSchema(DefaultResult):
    user: ProfileOutSchema = Field()
