"""
Schemas for validation of new user's info
"""

from typing import Optional

from pydantic import BaseModel, Field

from .result import DefaultPositiveResult


class NewUserDataSchema(BaseModel):
    """
    Schema for new user's data validation
    """

    id: Optional[int] = Field(title="User's id", default=None)
    name: str = Field(
        title="User's name",
        examples=["John", "Vasya"],
    )
    api_key: str = Field(
        title="User's api-key",
        examples=["123", "Ap1-k3Y"],
    )


class AdminSchema(BaseModel):
    """
    Schema for admin's credentials validation
    """

    login: str = Field(
        title="Admin's login",
        examples=["darkhacker", "megadestroyer"],
    )
    password: str = Field(
        title="Admin's password",
        examples=["123", "321"],
    )

    new_user_data: NewUserDataSchema = Field(title="New user's data")


class CreatedUserSchema(DefaultPositiveResult):
    """
    Schema for response with new user's data
    """

    created_user_data: NewUserDataSchema = Field(title="Newly created user's data")
