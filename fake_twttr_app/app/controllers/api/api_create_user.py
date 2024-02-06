from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from fake_twttr_app.app.auth_wrappers import check_is_admin
from fake_twttr_app.app.schemas import CreatedUserSchema, AdminSchema, BadResultSchema, IntegrityErrorResponse
from fake_twttr_app.db import User, async_session


api_admin_router = APIRouter(
    prefix="/admin/user", tags=["admin"], include_in_schema=False
)


@api_admin_router.post(
    "",
    responses={
        200: {"model": CreatedUserSchema},
        409: {"model": BadResultSchema}
    }
)
@check_is_admin
async def create_new_user(request: Request, admin_schema: AdminSchema):
    async with async_session() as session:
        async with session.begin():
            try:
                new_user = User(**admin_schema.new_user_data.model_dump())
                session.add(new_user)
                await session.commit()
            except IntegrityError as e:
                if e.orig.pgcode == "23505":
                    return JSONResponse(status_code=409, content=IntegrityErrorResponse("User with this data already exists").to_json())
            return CreatedUserSchema(created_user_data=new_user.to_json())
