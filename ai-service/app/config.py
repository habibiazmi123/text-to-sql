from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgres://app_user:app_password@localhost:5432/text_to_sql?sslmode=disable"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
