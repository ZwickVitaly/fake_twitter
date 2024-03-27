from pathlib import Path

from fastapi import HTTPException, UploadFile
import logging


logger = logging.getLogger("uvicorn")


class FilesAmountValidator:
    exceed_message = "Too many files. Allowed quantity: {max_files} files"
    empty_message = "File field is empty."

    def __init__(self, max_files: int):
        self.max_files = max_files

    def __call__(self, files: list[UploadFile]):
        self.validate(files)

    def validate(self, files: list[UploadFile]):
        files_amount = len(files)
        if not files[0].size:
            raise HTTPException(400, detail=self.empty_message)
        elif files_amount > self.max_files:
            raise HTTPException(400, detail=self.exceed_message.format(max_files=self.max_files))


class FileExtensionValidator:
    message = "Extension “{extension}” not allowed. Allowed extensions are {allowed_extensions}"

    def __init__(self, allowed_extensions: list[str], message: str | None = None):
        if allowed_extensions is not None:
            allowed_extensions = [
                allowed_extension.lower() for allowed_extension in allowed_extensions
            ]
        self.allowed_extensions = allowed_extensions
        if message is not None:
            self.message = message

    def __call__(self, files: list[UploadFile]):
        self.validate(files)

    def validate(self, files: list[UploadFile]):
        filenames = [Path(file.filename) for file in files]
        for filename in filenames:
            extension = filename.suffix.lower()
            if filename.suffix.lower() not in self.allowed_extensions:
                detail = self.message.format(
                    extension=extension,
                    allowed_extensions=", ".join(self.allowed_extensions),
                )
                raise HTTPException(status_code=400, detail=detail)


class FileSizeValidator:
    message = "Maximum file size exceeded. Max file size is {max_mb}Mb"

    def __init__(self, max_mb: int):
        self.max_mb = max_mb

    def __call__(self, files: list[UploadFile]):
        self.validate(files)

    def validate(self, files: list[UploadFile]):
        for file in files:
            if file.size / 1024 / 1024 > self.max_mb:
                raise HTTPException(400, detail=self.message.format(max_mb=self.max_mb))
