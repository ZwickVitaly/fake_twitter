"""Config module"""

from os import path, getenv

from fastapi.staticfiles import StaticFiles

# Static files directory (currently only for downloaded media)
main_static_path = "app_static"
static_request_path = "/static"
media_dir_name = "media"


media_path = path.join(main_static_path, media_dir_name)
static = StaticFiles(directory=media_path, check_dir=False)

# Api keyword for header
api_key_keyword = getenv("API_KEYWORD") or "api-key"

# Logger name
logger_name = "uvicorn"


# Max media file size
max_megabytes_file_size = 10

# Allowed meda extensions
allowed_extensions = [".jpeg", ".jpg", ".png"]
