from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra='ignore',
    )
    bot_token: str


def load_config() -> BotSettings:
    return BotSettings()
