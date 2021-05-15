from functools import lru_cache
from pydantic import BaseSettings


class AppFrenzySettings(BaseSettings):
    DATABASE_CONN_STR: str


@lru_cache
def get_app_frenzy_settings():
    return AppFrenzySettings()
