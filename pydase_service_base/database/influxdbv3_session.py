"""Module for InfluxDB v3 session management."""
from __future__ import annotations
from influxdb_client_3 import InfluxDBClient3, Point, WritePrecision as _WritePrecision
from typing import Any, NamedTuple, Iterable
from types import TracebackType
import logging
from confz import FileSource

from pydase_service_base.database.config import InfluxDBv3Config
from pydase_service_base.database.config import ServiceConfig
from os import PathLike

logger = logging.getLogger(__name__)

__all__ = [
    "InfluxDBv3Session",
    "WritePrecision",
]

WritePrecision = _WritePrecision

class InfluxDBv3Session:
    """Context manager for InfluxDB v3 session."""
    def __init__(self, host: str, org: str, bucket: str, token: str, verify_ssl: bool = True):
        """Initialize InfluxDB v3 session.

        Args:
            host (str): The InfluxDB host URL.
            org (str): The organization name.
            bucket (str): The bucket name.
            token (str): The authentication token.
            verify_ssl (bool): Whether to verify SSL certificates. Defaults to True.
            Recommended to set it to True in production environments.
        """
        self._bucket = bucket
        self._org = org
        self._host = host
        self._token = token
        self._verify_ssl = verify_ssl
        self._client = InfluxDBClient3(self._host, self._org, self._bucket, self._token, verify_ssl=self._verify_ssl)

    def __enter__(self) -> InfluxDBv3Session:
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            exc_traceback: TracebackType | None,
        ) -> None:
        self._client.close()


    def write(self, bucket: str,
        record:str
        | Iterable[str]
        | Point
        | Iterable[Point]
        | dict[str, Any]
        | Iterable[dict[str, Any]]
        | bytes
        | Iterable[bytes]
        | NamedTuple
        | Iterable[NamedTuple],
        write_precision: WritePrecision | None = None)->None:
        """Write records to InfluxDB v3.

        Args:
            bucket (str): The target bucket.
            record (various types): The record(s) to write.
            write_precision (WritePrecision | None): Precision of the timestamps.
                If None, defaults to the NS (nanoseconds) precision.
                Only matters if the record contains timestamps in POSIX format.
        """
        logger.debug("Writing to InfluxDB v3 bucket %s: %s", bucket, record)
        self._client.write(record)

    @classmethod
    def from_config_file(cls, path: str | PathLike | None = None)->"InfluxDBv3Session":
        """Create InfluxDBv3Session from configuration file.

        Args:
            path (str | PathLike | None): Path to the configuration file.
                If None, defaults to 'influxdbv3_config.yaml' in the database config directory.

                The database config directory can be set using environment variables or defaults.

                The default path is 'database_config/influxdbv3_config.yaml'.

                To change the default path, set the environment variable:

                `export SERVICE_DATABASE_CONFIG_DIR=/tmp/myconfigs`
        Returns:
            InfluxDBv3Session: An instance of InfluxDBv3Session.
        """
        if path is not None:
            _config = InfluxDBv3Config(
                config_sources=FileSource(path)
            )
        else:
            _config = InfluxDBv3Config(
                config_sources=FileSource(
                    ServiceConfig().database_config_dir / "influxdbv3_config.yaml"
                )
            )
        return cls(
            host=_config.url,
            org=_config.org,
            bucket=_config.bucket,
            token=_config.token.get_secret_value(),
            verify_ssl=_config.verify_ssl
        )
