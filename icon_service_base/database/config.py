from pathlib import Path
from typing import Literal, Optional

from confz import BaseConfig, EnvSource, FileSource
from loguru import logger
from pydantic import AnyUrl, SecretStr


def find_dir_upwards(start_dir: Path, targets: list[str]) -> Path | None:
    for parent in start_dir.parents:
        for target in targets:
            if (parent / target).is_dir():
                return parent / target
    return None


# we expect the database_config directory in the root directory of any module installing
# this package.
VENV_DIR = find_dir_upwards(Path(__file__).resolve(), [".venv", "venv"])
CONFIG_DIR: Optional[Path] = None
if VENV_DIR is not None:
    CONFIG_DIR = VENV_DIR.parent / "database_config"
    if not VENV_DIR.exists():
        CONFIG_DIR = None
    else:
        logger.debug(CONFIG_DIR)


class OperationMode(BaseConfig):  # type: ignore
    environment: Literal["development"] | Literal["production"] = "development"

    CONFIG_SOURCES = EnvSource(allow=["ENVIRONMENT"])


class PostgreSQLConfig(BaseConfig):  # type: ignore
    host: AnyUrl
    port: int
    database: str
    user: str
    password: SecretStr

    if CONFIG_DIR:
        CONFIG_SOURCES = FileSource(
            CONFIG_DIR / f"postgres_{OperationMode().environment}.yaml"
        )


class InfluxDBConfig(BaseConfig):  # type: ignore
    url: AnyUrl
    org: str
    token: SecretStr

    if CONFIG_DIR:
        CONFIG_SOURCES = FileSource(CONFIG_DIR / "influxdb_config.yaml")
