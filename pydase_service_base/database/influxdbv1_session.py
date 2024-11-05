from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

try:
    from typing import Self  # type: ignore
except ImportError:
    from typing_extensions import Self


import influxdb
from confz import FileSource

from pydase_service_base.database.config import InfluxDBv1Config, ServiceConfig

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType


logger = logging.getLogger(__name__)


class InfluxDBv1Session:
    """
    The `InfluxDBv1Session` class serves as a context manager for a connection
    to an InfluxDB server. This connection is established using credentials provided
    through environment variables.

    Example:
        ```python
        with InfluxDBv1Session() as influx_client:
            # Creating a database
            influx_client.create_database(
                dbname='my_new_database'
            )

            # Writing data to a database
            data = [
                {
                    "measurement": "your_measurement",  # Replace with your measurement
                    "tags": {
                        "example_tag": "tag_value",  # Replace with your tag and value
                    },
                    "fields": {
                        "example_field": 123,  # Replace with your field and its value
                    },
                    "time": "2023-06-05T00:00:00Z",  # Replace with your timestamp
                }
            ]
            influx_client.write_points(data=data, database="other_database")

            # just write one point into the client's current database
            influx_client.write(data=data[0])
        ```
    """

    conf_folder: Path | str

    def __init__(self) -> None:
        self._config = InfluxDBv1Config(
            config_sources=FileSource(
                ServiceConfig().database_config_dir / "influxdbv1_config.yaml"
            )
        )

        self._client: influxdb.InfluxDBClient
        self._host = self._config.host
        self._port = self._config.port
        self._username = self._config.username
        self._password = self._config.password
        self._database = self._config.database
        self._ssl = self._config.ssl
        self._verify_ssl = self._config.verify_ssl

    def __enter__(self) -> Self:
        self._client = influxdb.InfluxDBClient(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password.get_secret_value(),
            database=self._database,
            ssl=self._ssl,
            verify_ssl=self._verify_ssl,
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        self._client.close()

    def write(
        self,
        data: dict[str, Any],
    ) -> Any:
        """Write data to InfluxDB.

        Args:
            data:
                The data to be written.

        Example:
            ```python
            >>> data = {
                "measurement": "cpu_load_short",
                "tags": {
                    "host": "server01",
                    "region": "us-west"
                },
                "time": "2009-11-10T23:00:00Z",
                "fields": {
                    "value": 0.64
                }
            }
            >>> with InfluxDBv1Session() as client:
                    client.write(data=data)
            ```
        """
        self._client.write(data=data)

    def write_points(  # noqa: PLR0913
        self,
        points: list[dict[str, Any]],
        time_precision: Literal["s", "m", "ms", "u"] | None = None,
        database: str | None = None,
        tags: dict[str, str] | None = None,
        batch_size: int | None = None,
        consistency: Literal["any", "one", "quorum", "all"] | None = None,
    ) -> bool:
        """Write to multiple time series names.

        Args:
            points:
                The list of points to be written in the database.
            time_precision:
                Either 's', 'm', 'ms' or 'u', defaults to None.
            database:
                The database to write the points to. Defaults to the client's current
                database.
            tags:
                A set of key-value pairs associated with each point. Both keys and
                values must be strings. These are shared tags and will be merged with
                point-specific tags. Defaults to None.
            batch_size:
                Value to write the points in batches instead of all at one time. Useful
                for when doing data dumps from one database to another or when doing a
                massive write operation. Defaults to None
            consistency:
                Consistency for the points. One of {'any','one','quorum','all'}.

        Return:
            True, if the operation is successful

        Example:
            ```python
            >>> data = {
                "measurement": "cpu_load_short",
                "tags": {
                    "host": "server01",
                    "region": "us-west"
                },
                "time": "2009-11-10T23:00:00Z",
                "fields": {
                    "value": 0.64
                }
            }
            >>> with InfluxDBv1Session() as client:
                    client.write(data=data)
            ```
        """

        return self._client.write_points(
            points=points,
            time_precision=time_precision,
            database=database,
            tags=tags,
            batch_size=batch_size,
            consistency=consistency,
        )

    def create_database(
        self,
        dbname: str,
    ) -> None:
        """Create a new database in the InfluxDB instance. This function wraps the
        create_database from `influxdb` in a try-catch block and logs potential errors.

        Args:
            dbname:
                The name of the database to create.
        """

        try:
            self._client.create_database(dbname=dbname)
        except Exception as e:
            logger.error(e)
