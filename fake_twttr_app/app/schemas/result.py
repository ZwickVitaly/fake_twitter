from dataclasses import dataclass

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

    media_ids: list[int] = Field(examples=[[1], [2, 45]])


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
    result: bool = Field(default=False)
    error_type: str
    error_msg: str | list[dict]


class ValidationErrorResultSchema(DefaultPositiveResult):
    result: bool = Field(default=False)
    error_type: str
    error_msg: list[dict]


@dataclass
class ErrorResponse:
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
    def __init__(
        self, error_msg: str, result: bool = False, error_type: str = "IntegrityError"
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class NotFoundErrorResponse(ErrorResponse):
    def __init__(
        self, error_msg: str, result: bool = False, error_type: str = "NotFoundError"
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class UnAuthenticatedErrorResponse(ErrorResponse):
    def __init__(
        self,
        error_msg: str,
        result: bool = False,
        error_type: str = "UnAuthenticatedError",
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)


class UnAuthorizedErrorResponse(ErrorResponse):
    def __init__(
        self,
        error_msg: str,
        result: bool = False,
        error_type: str = "UnAuthorizedError",
    ):
        super().__init__(result=result, error_type=error_type, error_msg=error_msg)
