from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These match the variables in your .env file
    GEMINI_API_KEY: str
    YOUR_SECRET_API_KEY: str
    GUVI_CALLBACK_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

"""
This file checks for the system variables in the Config file (.env here)
"""