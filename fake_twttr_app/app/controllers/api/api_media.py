"""
Endpoints for Media CRUD (Creation only at the moment)
"""

import logging
from os import path
from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile

from fake_twttr_app.app.auth_wrappers import auth_required_header
from fake_twttr_app.app.config import logger_name, media_path, max_megabytes_file_size, allowed_extensions, api_key_keyword
from fake_twttr_app.app.schemas import (
    BadResultSchema,
    FileExtensionValidator,
    FileSizeValidator,
    ResultMediaSchema,
)
from fake_twttr_app.db import Image, async_session

api_media_router = APIRouter(prefix="/medias", tags=["media"])

logger = logging.getLogger(logger_name)


@api_media_router.post(
    "",
    dependencies=[
        Depends(FileSizeValidator(max_mb=max_megabytes_file_size)),
        Depends(FileExtensionValidator(allowed_extensions=allowed_extensions)),
    ],
    responses={
        200: {"model": ResultMediaSchema},
        400: {"model": BadResultSchema},
        401: {"model": BadResultSchema},
        422: {"model": BadResultSchema},
    },
)
@auth_required_header
async def post_media_handler(request: Request, file: UploadFile = File(...)):
    """
    Endpoint to download media file.
    
    <h3>Requires api-key header with valid api key</h3>
    """
    logger.debug("Attempting file download")
    file_extension = Path(file.filename).suffix.lower()  # type: ignore[arg-type]
    async with async_session() as session:
        async with session.begin():
            new_image = Image(file_extension=file_extension)
            session.add(new_image)
            await session.commit()
        logger.debug(f"Added new Image instance to database with id={new_image.id}")
    file_path = path.join(media_path, f"{new_image.id}{file_extension}")
    with open(file_path, "wb") as new_file:
        logger.debug(f"Writing file to: {file_path}")
        new_file.write(await file.read())
    logger.debug("File download complete")
    return ResultMediaSchema(media_id=new_image.id)  # type: ignore[arg-type]
