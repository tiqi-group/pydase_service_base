from pathlib import Path
from typing import Literal, Optional

from confz import BaseConfig, EnvSource, FileSource
from pydantic import AnyUrl, SecretStr

# Retrieve the name of the current package
package_name = Path(__file__).resolve().parent.parent.name


def find_dir_upwards(start_dir: Path, targets: list[str]) -> Path | None:
    """
    Traverse directory path upwards until finding a directory named as one of the
    targets.

    Args:
        start_dir: The starting point directory path.
        targets: List of target directory names to be searched for.

    Returns:
        The directory path if found, None otherwise.
    """
    for parent in start_dir.parents:
        for target in targets:
            if (parent / target).is_dir():
                return parent / target
    return None


# Look for ".venv" or "venv" directories starting from the current file's directory.
VENV_DIR = find_dir_upwards(Path(__file__).resolve(), [".venv", "venv"])
# Look for "deps" directory starting from the current file's directory.
DEPS_DIR = find_dir_upwards(Path(__file__).resolve(), ["deps"])

CONFIG_DIR: Optional[Path] = None

# If a ".venv" or "venv" directory was found and its parent's name is not the current
# package name, check for the "database_config" directory inside the parent directory of
# the found directory.
if VENV_DIR is not None and VENV_DIR.parent.name != package_name:
    CONFIG_DIR = VENV_DIR.parent / "database_config"
    if not CONFIG_DIR.exists():
        CONFIG_DIR = None
# If no ".venv" or "venv" directory was found or its parent's name is the current
# package name, but a "deps" directory was found, check for the "database_config"
# directory inside the parent directory of the found "deps" directory.
elif DEPS_DIR is not None:
    CONFIG_DIR = DEPS_DIR.parent / "database_config"
    if not CONFIG_DIR.exists():
        CONFIG_DIR = None


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
