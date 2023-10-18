import logging
from pathlib import Path
from typing import Optional, TypeVar

from confz import BaseConfig, FileSource

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseConfig)


class NoConfigSourceError(Exception):
    pass


def create_config(
    config_class: type[T],
    config_folder: Optional[Path | str] = None,
    config_file: str = "",
) -> T:
    if config_class.CONFIG_SOURCES is not None or config_folder is not None:
        config_sources = None
        if config_folder is not None:
            config_sources = FileSource(Path(config_folder) / config_file)
        return config_class(config_sources=config_sources)
    else:
        error_msg = (
            "No 'database_config' folder found in the root directory. Please ensure "
            "that a 'database_config' folder exists in your project's root directory. "
            "Alternatively, you can provide a different config folder by passing its "
            "path to the constructor."
        )
        logger.error(error_msg)

        raise NoConfigSourceError(error_msg)
