"""
Schemas for validation of Repost CRUD
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .tweet import TweetOutSchema


class RepostOutSchema(BaseModel):
    id: int = Field(
        title="Repost id",
        examples=[
            1, 2, 3
        ],
    )
    repost: TweetOutSchema = Field(
        title="Reposted tweet",
        examples=[
            {
                "id": 3,
                "author": {
                    "id": 2,
                    "name": "lol",
                },
                "content": "Later, alligator",
                "views": 0,
                "likes": 0,
                "reposts": 0,
                "images": [],
                "created_at": "2024-02-04T09:30:14+00:00",
            },
        ],
    )
    created_at: datetime = Field(
        title="Time of repost creation", examples=[datetime.now()]
    )
