from pydantic import BaseModel, Field


class UserBaseOutSchema(BaseModel):
    id: int = Field(
        title="User's id",
        examples=[1, 2, 3],
    )
    name: str = Field(
        title="User's name",
        examples=["Doctor Doom", "Sinestro"]
    )
