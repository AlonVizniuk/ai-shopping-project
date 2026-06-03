from pydantic import BaseSettings


class Config(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "ai_shopping"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: str = "3306"

    DATABASE_URL: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 100

    SECRET_KEY: str = "user_app"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRY_TIME: int = 20

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"

    class Config:
        env_file = ".env"