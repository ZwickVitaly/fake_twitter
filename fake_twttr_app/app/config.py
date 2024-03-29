"""Config module"""

from os import path

from fastapi.staticfiles import StaticFiles

# Static files directory (currently only for downloaded media)
main_static_path = path.join("fake_twttr_app", "app", "app_static")
static_request_path = "/static"
media_dir_name = "media"


media_path = path.join(main_static_path, media_dir_name)
static = StaticFiles(directory=media_path)

# Api keyword for header
api_key_keyword = "api-key"

# Logger name
logger_name = "uvicorn"
