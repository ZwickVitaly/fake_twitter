"""
Module of pydantic schemas for app.py
"""


from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseRecipe(BaseModel):
    """
    Base recipe schema
    """

    model_config = ConfigDict(from_attributes=True)
    name: str = Field(
        title="Recipe name",
        examples=[
            "Carbonara",
        ],
    )
    cook_time: int = Field(
        title="Cooking time in minutes",
        examples=[
            10,
        ],
    )


class GetRecipeDetails(BaseModel):
    """
    Schema for recipe id validation
    NOT IN USE AT THE MOMENT
    """

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(
        title="Recipe id",
        examples=[
            1,
        ],
    )


class RecipeNoDetailsOut(BaseRecipe, GetRecipeDetails):
    """
    Schema for no-detailed recipe response
    """

    views: int = Field(
        title="Recipe views",
        examples=[
            0,
        ],
    )


class RecipeCreate(BaseRecipe):
    """
    Schema for recipe creation data validation
    """

    ingredients: str = Field(
        title="Ingredients",
        examples=[
            "Racoon butt - 1kg, Cream - 300ml",
        ],
    )
    description: Optional[str] = Field(
        title="Description",
        examples=["TASTY AF"],
    )


class RecipeDetailsOut(RecipeNoDetailsOut, RecipeCreate):
    """
    Schema for recipe details response
    """

    ...


class Message(BaseModel):
    """
    Schema for "Not found" response
    """

    detail: str = Field()
