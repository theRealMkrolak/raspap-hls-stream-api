from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    system: Literal["raspberrypi", "mac"] = "raspberrypi"
    raspap_api_key: str | None = None
    mediamtx_hls_url: str = "http://localhost:8888/mystream"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
