from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .user import UserBaseOutSchema


class NewTweetSchema(BaseModel):
    tweet_data: str = Field(
        title="Tweet content",
        examples=["Biden go Texas!", "I might been underestimating my sleep time"],
    )
    tweet_media: Optional[list[int]] = Field(title="Tweet media links", default=None)


class TweetOutSchema(BaseModel):
    uuid: UUID | str = Field(
        title="Tweet uuid",
        examples=["bdd7e8c8-f65c-4978-9c70-95ec39b13f9d"],
    )
    author: UserBaseOutSchema = Field(
        title="User's info",
        examples=[
            {
                "uuid": "bdd7e8c8-f65c-4978-9c70-95ec39b13f9d",
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
            ]
        ],
    )
