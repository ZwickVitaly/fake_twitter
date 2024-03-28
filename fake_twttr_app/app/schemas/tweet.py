from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .user import UserBaseOutSchema


class NewTweetSchema(BaseModel):
    tweet_data: str = Field(
        title="Tweet content",
        examples=["Biden go Texas!", "I might been underestimating my sleep time"],
    )
    tweet_media_ids: Optional[list[int]] = Field(title="Tweet media ids", default=None)


class TweetOutSchema(BaseModel):
    id: int = Field(
        title="Tweet id",
        examples=[1, 2, 22],
    )
    author: UserBaseOutSchema = Field(
        title="User's info",
        examples=[
            {
                "id": 1,
                "name": "John",
            },
        ],
    )
    content: str = Field(
        title="Tweet content",
        examples=[
            "Another one bites the dust!",
            "Sleepy Joe strikes(sleeps) again!",
        ],
    )
    # views: int = Field(
    #     title="Tweet's views",
    #     examples=[0, 1, 2, 3],
    # )
    likes: list[UserBaseOutSchema] = Field(
        title="Tweet's likes",
        examples=[[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}], ],
    )
    # reposts: int = Field(
    #     title="Tweet's reposts",
    #     examples=[0, 1, 2, 3],
    # )
    attachments: list[str] = Field(
        title="List of tweet's images ids",
        examples=["/static/1.jpeg"],
    )
    # created_at: datetime = Field(
    #     title="Time of tweet creation",
    #     examples=[datetime.now()],
    # )


class FeedOutSchema(BaseModel):
    tweets: list[TweetOutSchema] = Field(
        title="Tweets list. If /personal - tweets are sorted by user's follows",
        examples=[
            [
                {
                    "id": 1,
                    "author": {
                        "id": 4,
                        "name": "lol",
                    },
                    "content": "Later, alligator",
                    # "views": 0,
                    "likes": [{"id": 2, "name": "Jane"}],
                    # "reposts": 0,
                    "attachments": [],
                    # "created_at": "2024-02-04T09:30:14+00:00",
                },
                {
                    "id": 2,
                    "author": {
                        "id": 3,
                        "name": "lol",
                    },
                    "content": "Lol kek",
                    # "views": 1,
                    "likes": [{"id": 1, "name": "John"}],
                    # "reposts": 1,
                    "attachments": [1, 2],
                    # "created_at": "2024-02-04T09:30:14+00:00",
                },
            ]
        ],
    )
