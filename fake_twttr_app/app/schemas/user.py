from uuid import UUID

from pydantic import BaseModel, Field


class UserBaseOutSchema(BaseModel):
    uuid: UUID | str = Field(
        title="User's uuid",
        examples=["bdd7e8c8-f65c-4978-9c70-95ec39b13f9d"],
    )
    name: str = Field(title="User's name")
