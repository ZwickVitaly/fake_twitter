from os import path
from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile
from typing import List

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.folders import media_path
from fake_twttr_app.app.schemas.result import BadResultSchema, ResultMediaSchema
from fake_twttr_app.app.schemas.upload_file import (
    FileExtensionValidator,
    FileSizeValidator,
    FilesAmountValidator,
)
from fake_twttr_app.db import Image, async_session


api_media_router = APIRouter(prefix="/media", tags=["media"])


@api_media_router.post(
    "",
    dependencies=[
        Depends(FilesAmountValidator(max_files=4)),
        Depends(FileSizeValidator(max_mb=10)),
        Depends(FileExtensionValidator(allowed_extensions=[".jpg", ".jpeg", ".png"])),
    ],
    responses={
        200: {"model": ResultMediaSchema},
        400: {"model": BadResultSchema},
        401: {"model": BadResultSchema},
        422: {"model": BadResultSchema},
    },
)
@auth_required_header
async def post_media_handler(request: Request, files: List[UploadFile] = File(...)):
    media_ids: list = []
    for file in files:
        file_extension = Path(file.filename).suffix.lower()
        async with async_session() as session:
            async with session.begin():
                new_image = Image(file_extension=file_extension)
                session.add(new_image)
                await session.commit()
        file_path = path.join(media_path, f"{new_image.id}{file_extension}")
        with open(file_path, "wb") as new_file:
            new_file.write(await file.read())
        media_ids.append(new_image.id)
    return ResultMediaSchema(media_ids=media_ids)
