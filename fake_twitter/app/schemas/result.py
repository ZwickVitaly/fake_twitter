"""
Schemas for validation of different results output
"""


from dataclasses import dataclass
from typing import Any, Sequence

from pydantic import BaseModel, Field

from .tweet import FeedOutSchema, TweetOutSchema


class DefaultPositiveResult(BaseModel):
    """
    Default successful result schema. Used for inheritance and simple response like {"result": true}
    """

    result: bool = Field(
        default=True,
    )


class ResultMediaSchema(DefaultPositiveResult):
    """Schema for successful result response adding media_id"""

    media_id: int = Field(examples=[1, 2, 45])


class ResultTweetCreationSchema(DefaultPositiveResult):
    """Schema for successful result response adding tweet_id"""

    tweet_id: int


class ResultFeedSchema(DefaultPositiveResult):
    """Schema for successful result response adding feed (tweets list)"""

    tweets: FeedOutSchema


class ResultTweetSchema(ResultFeedSchema):
    """Schema for successful result response adding tweet data"""

    tweet: TweetOutSchema


class BadResultSchema(DefaultPositiveResult):
    """Schema for unsuccessful result response"""

    result: bool = Field(default=False)
    error_type: str
    error_msg: Sequence[Any]


@dataclass
class ErrorResponse:
    """
    Class for basic error response
    """

    error_type: str
    error_msg: str
    result: bool

    def __init__(
        self,
        result: bool = False,
        error_type: str = "Error type",
        error_msg: str = "Error msg",
    ):
        self.result = result
        self.error_msg = error_msg
        self.error_type = error_type

    def to_json(self):
        return {
            "result": self.result,
            "error_type": self.error_type,
            "error_msg": self.error_msg,
        }


class IntegrityErrorResponse(ErrorResponse):
    """
    Class for integrity error response
    """

    def __init__(
        self, error_msg: str, result: bool = False, error_type: str = "IntegrityError"
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class NotFoundErrorResponse(ErrorResponse):
    """
    Class for not found error response
    """

    def __init__(
        self, error_msg: str, result: bool = False, error_type: str = "NotFoundError"
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class UnAuthenticatedErrorResponse(ErrorResponse):
    """
    Class for unauthenticated error response
    """

    def __init__(
        self,
        error_msg: str,
        result: bool = False,
        error_type: str = "UnAuthenticatedError",
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class UnAuthorizedErrorResponse(ErrorResponse):
    """
    Class for unauthorized error response
    """

    def __init__(
        self,
        error_msg: str,
        result: bool = False,
        error_type: str = "UnAuthorizedError",
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)
