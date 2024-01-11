from pathlib import Path
from typing import Literal

from confz import BaseConfig, EnvSource
from pydantic import AnyUrl, SecretStr


class OperationMode(BaseConfig):  # type: ignore
    environment: Literal["development", "production"] = "development"

    CONFIG_SOURCES = EnvSource(allow=["ENVIRONMENT"])


class ServiceConfig(BaseConfig):  # type: ignore
    database_config_dir: Path = Path("database_config")

    CONFIG_SOURCES = EnvSource(allow=["SERVICE_DATABASE_CONFIG_DIR"])


class PostgreSQLConfig(BaseConfig):  # type: ignore
    host: AnyUrl
    port: int
    database: str
    user: str
    password: SecretStr

    # if CONFIG_DIR:
    #     CONFIG_SOURCES = FileSource(
    #         CONFIG_DIR / f"postgres_{OperationMode().environment}.yaml"
    #     )


class InfluxDBConfig(BaseConfig):  # type: ignore
    url: AnyUrl
    org: str
    token: SecretStr

    # if CONFIG_DIR:
    #     CONFIG_SOURCES = FileSource(CONFIG_DIR / "influxdb_config.yaml")
