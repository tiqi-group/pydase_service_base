from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Optional

from confz import FileSource
from influxdb_client import (  # type: ignore
    Bucket,
    BucketRetentionRules,
    BucketsApi,
    InfluxDBClient,
    WriteApi,
)
from influxdb_client.client.write_api import SYNCHRONOUS  # type: ignore
from influxdb_client.rest import ApiException  # type: ignore
from loguru import logger

from icon_service_base.database.config import InfluxDBConfig


class InfluxDBSession:
    """
    The `InfluxDBConnection` class serves as a context manager for a connection
    to an InfluxDB server. This connection is established using credentials
    provided through environment variables.

    Example usage:
    ```
    with InfluxDBSession() as influx_client:
        # Creating a bucket
        influx_client.create_bucket(
            bucket_name='my_new_bucket', description='This is a new bucket'
        )

        # Writing data to a bucket
        record = {
            "measurement": "your_measurement",  # Replace with your measurement
            "tags": {
                "example_tag": "tag_value",  # Replace with your tag and its value
            },
            "fields": {
                "example_field": 123,  # Replace with your field and its value
            },
            "time": "2023-06-05T00:00:00Z",  # Replace with your timestamp
        }
        influx_client.write_api.write(
            bucket='my_new_bucket', record=record
        )
    ```
    """

    conf_folder: Path | str

    def __init__(self, config_folder: Optional[Path | str] = None) -> None:
        config_folder = config_folder or getattr(self, "conf_folder", None)
        if InfluxDBConfig.CONFIG_SOURCES is not None or config_folder is not None:
            config_sources = None
            if config_folder is not None:
                config_sources = FileSource(
                    Path(config_folder) / "influxdb_config.yaml"
                )
            self._config = InfluxDBConfig(config_sources=config_sources)
        else:
            logger.error(
                "No config folder given. Please provide a config folder either by "
                "passing it to the constructor or by setting the 'conf_folder' "
                "attribute."
            )
            return

        self.url = self._config.url
        self.token = str(self._config.token)
        self.org = self._config.org
        self.client: InfluxDBClient
        self.write_api: WriteApi
        self.buckets_api: BucketsApi | None = None

    def __enter__(self) -> InfluxDBSession:
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)  # type: ignore
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        self.write_api.close()
        self.client.__del__()

    def create_bucket(  # noqa: CFQ002
        self,
        bucket: Bucket | None = None,
        bucket_name: str | None = None,
        org_id: int | None = None,
        retention_rules: BucketRetentionRules | None = None,
        description: str | None = None,
        org: str | None = None,
    ) -> None:
        """
        Create a bucket in the InfluxDB instance. This function wraps the create_bucket
        from `influxdb_client` in a try-catch block and logs potential errors with
        loguru.

        Args:
            bucket (Bucket | PostBucketRequest, optional): Bucket instance to be
            created.
            bucket_name (str, optional): Name of the bucket to be created.
            org_id (int, optional): The organization id for the bucket.
            retention_rules (BucketRetentionRules, optional): Retention rules for the
            bucket.
            description (str, optional): Description of the bucket.
            org (str, optional): The name of the organization for the bucket. Takes
            the ID, Name, or Organization. If not specified, the default value from
            `InfluxDBClient.org` is used.
        """

        self.buckets_api = self.client.buckets_api()
        try:
            self.buckets_api.create_bucket(
                bucket=bucket,
                bucket_name=bucket_name,
                org_id=org_id,
                retention_rules=retention_rules,
                description=description,
                org=org,
            )
        except ApiException as e:
            if e.status == 422:
                logger.debug(e.message)
                return
            logger.error(e)
        return
