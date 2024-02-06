from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .tweet import TweetOutSchema


class RepostOutSchema(BaseModel):
    uuid: UUID | str = Field(
        title="Repost uuid",
        examples=[
            "58977674-4581-4d26-b862-2bf4c2b23a49",
        ],
    )
    repost: TweetOutSchema = Field(
        title="Reposted tweet",
        examples=[
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
        ],
    )
    created_at: datetime = Field(
        title="Time of repost creation", examples=[datetime.now()]
    )
