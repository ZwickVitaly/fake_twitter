from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .user import UserBaseOutSchema


class NewTweetSchema(BaseModel):
    tweet_data: str = Field(
        title="Tweet content",
        examples=["Biden go Texas!", "I might been underestimating my sleep time"],
    )
    tweet_media: Optional[list[int]] = Field(title="Tweet media links", default=None)


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
    views: int = Field(
        title="Tweet's views",
        examples=[0, 1, 2, 3],
    )
    likes: int = Field(
        title="Tweet's likes",
        examples=[0, 1, 2, 3],
    )
    reposts: int = Field(
        title="Tweet's reposts",
        examples=[0, 1, 2, 3],
    )
    images: list[str] = Field(
        title="List of tweet's images ids",
        examples=[1, 2, 35],
    )
    created_at: datetime = Field(
        title="Time of tweet creation",
        examples=[datetime.now()],
    )


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
                    "views": 0,
                    "likes": 0,
                    "reposts": 0,
                    "images": [],
                    "created_at": "2024-02-04T09:30:14+00:00",
                },
                {
                    "id": 2,
                    "author": {
                        "id": 3,
                        "name": "lol",
                    },
                    "content": "Lol kek",
                    "views": 1,
                    "likes": 1,
                    "reposts": 1,
                    "images": [1, 2],
                    "created_at": "2024-02-04T09:30:14+00:00",
                },
            ]
        ],
    )
