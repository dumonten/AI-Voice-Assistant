import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A class for managing application settings, including environment variables.
    """

    BOT_KEY: str = Field(env="BOT_KEY")
    OPENAI_KEY: str = Field(env="OPENAI_KEY")

    class Config:
        """
        Configuration for the Settings class, specifying the location of the .env file and its encoding.
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(base_dir, ".env")
        env_file_encoding = "utf-8"


settings = Settings()
