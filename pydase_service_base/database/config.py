from pathlib import Path
from typing import Literal

from confz import BaseConfig, EnvSource
from pydantic import AnyUrl, SecretStr


class OperationMode(BaseConfig):  # type: ignore
    environment: Literal["development", "production"] = "development"

    CONFIG_SOURCES = EnvSource(allow=["ENVIRONMENT"])


class ServiceConfig(BaseConfig):  # type: ignore
    database_config_dir: Path = Path("database_config")

    CONFIG_SOURCES = EnvSource(prefix="SERVICE_", allow_all=True)


class PostgreSQLConfig(BaseConfig):  # type: ignore
    host: AnyUrl
    port: int
    database: str
    user: str
    password: SecretStr


class InfluxDBConfig(BaseConfig):  # type: ignore
    url: str
    org: str
    token: SecretStr


class InfluxDBv1Config(BaseConfig):  # type: ignore
    host: str
    port: int = 8086
    username: str
    password: SecretStr
    database: str
    ssl: bool = True
    verify_ssl: bool = True
