from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .result import DefaultResult


class NewUserDataSchema(BaseModel):
    uuid: Optional[UUID] = Field(title="User's uuid", default=None)
    name: str = Field(
        title="User's name",
        examples=["John", "Vasya"],
    )
    api_key: str = Field(
        title="User's api-key",
        examples=["123", "Ap1-k3Y"],
    )


class AdminSchema(BaseModel):
    login: str = Field(
        title="Admin's login",
        examples=["darkhacker", "megadestroyer"],
    )
    password: str = Field(
        title="Admin's password",
        examples=["123", "321"],
    )

    new_user_data: NewUserDataSchema = Field(title="New user's data")


class CreatedUserSchema(DefaultResult):
    created_user_data: NewUserDataSchema = Field(title="Newly created user's data")
