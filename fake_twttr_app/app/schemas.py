"""
Module of pydantic schemas for app.py
"""


from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GetMyProfile(BaseModel):
    """
    Base recipe schema
    """

    model_config = ConfigDict(from_attributes=True)
    result: bool = Field(
        title="Result",
        examples=[
            True,
            False,
        ],
    )
    cook_time: int = Field(
        title="Cooking time in minutes",
        examples=[
            10,
        ],
    )


class NewTweetSchema(BaseModel):
    tweet_data: str = Field(
        title="Tweet content"
    )
    tweet_media: Optional[list[str]] = Field(
        title="Tweet media links",
        default=None
    )


class DeleteTweetSchema(BaseModel):
    uuid: str = Field(
        title="Tweet or repost uuid"
    )

