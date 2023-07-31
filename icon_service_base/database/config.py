from typing import Literal

from confz import BaseConfig, EnvSource
from pydantic import AnyUrl, SecretStr


class OperationMode(BaseConfig):  # type: ignore
    environment: Literal["development"] | Literal["production"] = "development"

    CONFIG_SOURCES = EnvSource(allow=["ENVIRONMENT"])


class PostgreSQLConfig(BaseConfig):  # type: ignore
    host: AnyUrl
    port: int
    database: str
    user: str
    password: SecretStr


class InfluxDBConfig(BaseConfig):  # type: ignore
    url: AnyUrl
    org: str
    token: SecretStr
