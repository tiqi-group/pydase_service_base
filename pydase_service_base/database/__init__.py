class OptionalDependencyError(Exception):
    """Exception raised when an optional dependency is not installed."""


try:
    import influxdb_client  # type: ignore # noqa

    from .influxdb_session import InfluxDBSession  # type: ignore
except ImportError:

    class InfluxDBSession:  # type: ignore
        def __init__(self) -> None:
            raise OptionalDependencyError(
                "InfluxDBSession requires the 'influxdbv2' extra. "
                "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
            )


try:
    import sqlmodel  # noqa

    from .postgres_session import PostgresDatabaseSession  # type: ignore
except ImportError:

    class PostgresDatabaseSession:  # type: ignore
        def __init__(self) -> None:
            raise OptionalDependencyError(
                "PostgresDatabaseSession requires the 'postgresql' extra. "
                "Please refer to https://gitlab.phys.ethz.ch/tiqi-projects/qchub/icon-services/pydase_service_base."
            )


__all__ = ["InfluxDBSession", "PostgresDatabaseSession"]
