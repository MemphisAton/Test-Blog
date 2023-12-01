from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DatabaseConfig:
    SECRET_KEY: str
    PASSWORD: str
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str


@dataclass
class Config:
    db: DatabaseConfig


def load_config(path: Optional[str]) -> Config:
    env: Env = Env()  # Создаем экземпляр класса Env
    env.read_env(path)  # Добавляем в переменные окружения данные, прочитанные из файла .env
    return Config(db=DatabaseConfig(SECRET_KEY=env('SECRET_KEY'),
                                    PASSWORD=env('PASSWORD'),
                                    EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD'),
                                    EMAIL_HOST_USER=env('EMAIL_HOST_USER')))


