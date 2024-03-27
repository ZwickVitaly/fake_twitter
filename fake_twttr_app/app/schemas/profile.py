from pydantic import BaseModel, Field

from .repost import RepostOutSchema
from .result import DefaultPositiveResult
from .tweet import TweetOutSchema
from .user import UserBaseOutSchema


class ProfileOutSchema(UserBaseOutSchema):
    # tweets: list[TweetOutSchema | RepostOutSchema] = Field(
    #     title="List of user's tweets and reposts",
    #     examples=[
    #         [
    #             {
    #                 "id": 1,
    #                 "author": {
    #                     "id": 1,
    #                     "name": "lol",
    #                 },
    #                 "content": "Later, alligator",
    #                 "views": 0,
    #                 "likes": 0,
    #                 "reposts": 0,
    #                 "images": [],
    #                 "created_at": "2024-02-04T09:30:14+00:00",
    #             },
    #             {
    #                 "id": 2,
    #                 "repost": {
    #                     "id": 3,
    #                     "author": {
    #                         "id": 3,
    #                         "name": "lol",
    #                     },
    #                     "content": "Lol kek azazaza",
    #                     "views": 1,
    #                     "likes": 1,
    #                     "reposts": 1,
    #                     "images": ["1", "2"],
    #                     "created_at": "2024-02-04T09:30:14+00:00",
    #                 },
    #                 "created_at": "2024-02-04T09:30:14+00:00",
    #             },
    #         ]
    #     ],
    # )
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
    user: ProfileOutSchema = Field()
