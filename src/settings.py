from pathlib import Path

from injection import mod
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

import src
from src.enums import Profile, SubProfile


class _DatabaseSettings(BaseModel):
    name: SecretStr = Field(default=SecretStr("pushup_api"))
    user: SecretStr = Field(default=SecretStr("root"))
    password: SecretStr = Field(default=SecretStr("root"))
    host: str = Field(default="localhost")
    port: str = Field(default="5432")

    def get_url(self, custom_name: str | None = None) -> str:
        name = custom_name or self.name.get_secret_value()
        user = self.user.get_secret_value()
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{user}:{password}@{self.host}:{self.port}/{name}"


@mod(SubProfile.GLOBAL).constant
class Settings(BaseSettings):
    profile: Profile = Field(default=Profile.DEFAULT)
    allowed_hosts: tuple[str, ...] = ("http://localhost:3000", "http://127.0.0.1:3000")
    debug: bool = Field(default=False)
    db: _DatabaseSettings = Field(default_factory=_DatabaseSettings)
    root_dir: Path = Field(default=Path(src.__file__).parents[1], init=False)
    secret_key: SecretStr = Field(default=SecretStr("pushup-dev-key"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )
