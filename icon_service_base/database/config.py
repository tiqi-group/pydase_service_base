from pathlib import Path
from typing import Literal

from confz import ConfZ, ConfZEnvSource, ConfZFileSource
from pydantic import AnyUrl, SecretStr

CONFIG_DIR = Path(__file__).parent.parent.parent.resolve() / "config"


class OperationMode(ConfZ):  # type: ignore
    environment: Literal["development"] | Literal["production"] = "development"

    CONFIG_SOURCES = ConfZEnvSource(allow=["ENVIRONMENT"])


class PostgreSQLConfig(ConfZ):  # type: ignore
    host: AnyUrl
    port: int
    database: str
    user: str
    password: SecretStr

    CONFIG_SOURCES = [
        ConfZFileSource(f"{CONFIG_DIR}/postgres_{OperationMode().environment}.yaml"),
        ConfZEnvSource(prefix="POSTGRES_", allow=["user", "password"], file=".env"),
    ]


class InfluxDBConfig(ConfZ):  # type: ignore
    url: AnyUrl
    org: str
    token: SecretStr

    CONFIG_SOURCES = [
        ConfZFileSource(f"{CONFIG_DIR}/influxdb_config.yaml"),
        ConfZEnvSource(prefix="INFLUXDB_V2_", allow=["token"], file=".env"),
    ]
